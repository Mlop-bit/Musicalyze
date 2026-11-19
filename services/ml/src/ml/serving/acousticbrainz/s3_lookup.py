from __future__ import annotations

import shutil
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
from botocore.exceptions import ClientError

from ml.serving.acousticbrainz.find_song_acousticbrainz import (
    HIGHLEVEL_DIR_NAME,
    LOWLEVEL_DIR_NAME,
    AcousticBrainzData,
    AcousticBrainzDumpNotExtractedError,
    get_acousticbrainz_data,
)
from ml.serving.acousticbrainz.s3_shards import shard_prefix, unpack_shard

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client

DEFAULT_MAX_CACHED_SHARDS = 16
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_DOWNLOAD_WORKERS = 4
PRESIGNED_URL_EXPIRY_SECONDS = 3600
DOWNLOAD_TIMEOUT_SECONDS = 30.0
STREAM_BLOCK_BYTES = 1 << 20
_DATASETS = ((HIGHLEVEL_DIR_NAME, "highlevel"), (LOWLEVEL_DIR_NAME, "lowlevel"))


def _shard_marker(cache_dir: Path, shard: str, level: str) -> Path:
    return cache_dir / f".{shard}.{level}.synced"


def _wanted_datasets(include_lowlevel: bool) -> tuple[tuple[str, str], ...]:
    return _DATASETS if include_lowlevel else _DATASETS[:1]


def _download_and_unpack_chunk(
    client: S3Client, bucket: str, key: str, tmp_dir: Path, destination_dir: Path
) -> None:
    chunk_path = tmp_dir / Path(key).name
    url = client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=PRESIGNED_URL_EXPIRY_SECONDS,
    )
    with httpx.stream("GET", url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
        response.raise_for_status()
        with chunk_path.open("wb") as chunk_file:
            for block in response.iter_bytes(STREAM_BLOCK_BYTES):
                chunk_file.write(block)
    unpack_shard(chunk_path, destination_dir)
    chunk_path.unlink()


def _download_and_unpack_shard_once(
    client: S3Client,
    bucket: str,
    dataset_dir_name: str,
    level: str,
    shard: str,
    destination_dir: Path,
    tmp_dir: Path,
    max_workers: int = DEFAULT_DOWNLOAD_WORKERS,
) -> None:
    prefix = shard_prefix(dataset_dir_name, level, shard)
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    keys = [key for obj in response.get("Contents", []) if (key := obj.get("Key")) is not None]

    tmp_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                _download_and_unpack_chunk, client, bucket, key, tmp_dir, destination_dir
            )
            for key in keys
        ]
        for future in futures:
            future.result()


def _download_and_unpack_shard(
    client: S3Client,
    bucket: str,
    dataset_dir_name: str,
    level: str,
    shard: str,
    destination_dir: Path,
    tmp_dir: Path,
    attempts: int,
    sleep: Callable[[float], None],
    max_workers: int = DEFAULT_DOWNLOAD_WORKERS,
) -> None:
    for attempt in range(1, attempts + 1):
        try:
            _download_and_unpack_shard_once(
                client,
                bucket,
                dataset_dir_name,
                level,
                shard,
                destination_dir,
                tmp_dir,
                max_workers,
            )
        except (ClientError, OSError):
            if attempt == attempts:
                raise
            sleep(2**attempt)
        else:
            return


def _evict_lru_shards(cache_dir: Path, max_cached_shards: int) -> None:
    markers = sorted(cache_dir.glob(".*.synced"), key=lambda path: path.stat().st_mtime)
    dataset_dir_by_level = {level: dir_name for dir_name, level in _DATASETS}
    while len(markers) > max_cached_shards:
        oldest = markers.pop(0)
        shard, level = oldest.name.removeprefix(".").removesuffix(".synced").split(".")
        shutil.rmtree(cache_dir / dataset_dir_by_level[level] / level / shard, ignore_errors=True)
        oldest.unlink()


def _missing_datasets(mbid: str, cache_dir: Path, include_lowlevel: bool) -> list[tuple[str, str]]:
    shard = mbid[:2]
    missing: list[tuple[str, str]] = []
    for dataset_dir_name, level in _wanted_datasets(include_lowlevel):
        marker = _shard_marker(cache_dir, shard, level)
        if marker.exists():
            marker.touch()
        else:
            missing.append((dataset_dir_name, level))
    return missing


def ensure_shard_cached(
    mbid: str,
    cache_dir: Path,
    client: S3Client,
    bucket: str,
    tmp_dir: Path,
    max_cached_shards: int = DEFAULT_MAX_CACHED_SHARDS,
    attempts: int = DEFAULT_RETRY_ATTEMPTS,
    sleep: Callable[[float], None] = time.sleep,
    max_workers: int = DEFAULT_DOWNLOAD_WORKERS,
    include_lowlevel: bool = False,
) -> None:
    shard = mbid[:2]
    missing = _missing_datasets(mbid, cache_dir, include_lowlevel)
    if not missing:
        return

    for dataset_dir_name, level in missing:
        destination = cache_dir / dataset_dir_name / level / shard
        _download_and_unpack_shard(
            client,
            bucket,
            dataset_dir_name,
            level,
            shard,
            destination,
            tmp_dir,
            attempts,
            sleep,
            max_workers,
        )
        cache_dir.mkdir(parents=True, exist_ok=True)
        _shard_marker(cache_dir, shard, level).touch()
    _evict_lru_shards(cache_dir, max_cached_shards)


def get_acousticbrainz_data_from_s3(
    mbid: str,
    cache_dir: Path,
    client: S3Client,
    bucket: str,
    tmp_dir: Path,
    max_cached_shards: int = DEFAULT_MAX_CACHED_SHARDS,
    attempts: int = DEFAULT_RETRY_ATTEMPTS,
    sleep: Callable[[float], None] = time.sleep,
    max_workers: int = DEFAULT_DOWNLOAD_WORKERS,
    download_missing: bool = True,
    include_lowlevel: bool = False,
) -> AcousticBrainzData:
    if not download_missing and _missing_datasets(mbid, cache_dir, include_lowlevel):
        return AcousticBrainzData(highlevel=None, lowlevel=None)
    ensure_shard_cached(
        mbid,
        cache_dir,
        client,
        bucket,
        tmp_dir,
        max_cached_shards,
        attempts,
        sleep,
        max_workers,
        include_lowlevel,
    )
    try:
        return get_acousticbrainz_data(mbid, cache_dir)
    except AcousticBrainzDumpNotExtractedError:
        return AcousticBrainzData(highlevel=None, lowlevel=None)
