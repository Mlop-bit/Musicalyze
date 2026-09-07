import random
import shutil
import time
from collections.abc import Callable
from pathlib import Path

from botocore.exceptions import ClientError
from mypy_boto3_s3.client import S3Client

from ml.serving.acousticbrainz.find_song_acousticbrainz import (
    HIGHLEVEL_DIR_NAME,
    LOWLEVEL_DIR_NAME,
    AcousticBrainzData,
    AcousticBrainzDumpNotExtractedError,
    get_acousticbrainz_data,
)
from ml.serving.acousticbrainz.s3_shards import shard_prefix, unpack_shard

DEFAULT_MAX_CACHED_SHARDS = 16
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_DOWNLOAD_PACING_SECONDS = 0.2
_DATASETS = ((HIGHLEVEL_DIR_NAME, "highlevel"), (LOWLEVEL_DIR_NAME, "lowlevel"))


def _shard_marker(cache_dir: Path, shard: str) -> Path:
    return cache_dir / f".{shard}.synced"


def _download_and_unpack_shard_once(
    client: S3Client,
    bucket: str,
    dataset_dir_name: str,
    level: str,
    shard: str,
    destination_dir: Path,
    tmp_dir: Path,
    sleep: Callable[[float], None] = time.sleep,
    pacing_seconds: float = DEFAULT_DOWNLOAD_PACING_SECONDS,
    jitter: Callable[[], float] = lambda: random.uniform(0, DEFAULT_DOWNLOAD_PACING_SECONDS),
) -> None:
    prefix = shard_prefix(dataset_dir_name, level, shard)
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    keys = [key for obj in response.get("Contents", []) if (key := obj.get("Key")) is not None]

    tmp_dir.mkdir(parents=True, exist_ok=True)
    for index, key in enumerate(keys):
        if index > 0:
            # A shard can hold hundreds of chunks; some self-hosted S3 servers
            # rate-limit bursts of requests and answer with 403 rather than 429.
            sleep(pacing_seconds + jitter())
        chunk_path = tmp_dir / Path(key).name
        client.download_file(bucket, key, str(chunk_path))
        unpack_shard(chunk_path, destination_dir)
        chunk_path.unlink()


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
    pacing_seconds: float = DEFAULT_DOWNLOAD_PACING_SECONDS,
    jitter: Callable[[], float] = lambda: random.uniform(0, DEFAULT_DOWNLOAD_PACING_SECONDS),
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
                sleep,
                pacing_seconds,
                jitter,
            )
        except (ClientError, OSError):
            if attempt == attempts:
                raise
            sleep(2**attempt)
        else:
            return


def _evict_lru_shards(cache_dir: Path, max_cached_shards: int) -> None:
    markers = sorted(cache_dir.glob(".*.synced"), key=lambda path: path.stat().st_mtime)
    while len(markers) > max_cached_shards:
        oldest = markers.pop(0)
        shard = oldest.name.removeprefix(".").removesuffix(".synced")
        for dataset_dir_name, level in _DATASETS:
            shutil.rmtree(cache_dir / dataset_dir_name / level / shard, ignore_errors=True)
        oldest.unlink()


def ensure_shard_cached(
    mbid: str,
    cache_dir: Path,
    client: S3Client,
    bucket: str,
    tmp_dir: Path,
    max_cached_shards: int = DEFAULT_MAX_CACHED_SHARDS,
    attempts: int = DEFAULT_RETRY_ATTEMPTS,
    sleep: Callable[[float], None] = time.sleep,
    pacing_seconds: float = DEFAULT_DOWNLOAD_PACING_SECONDS,
    jitter: Callable[[], float] = lambda: random.uniform(0, DEFAULT_DOWNLOAD_PACING_SECONDS),
) -> None:
    shard = mbid[:2]
    marker = _shard_marker(cache_dir, shard)
    if marker.exists():
        marker.touch()
        return

    for dataset_dir_name, level in _DATASETS:
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
            pacing_seconds,
            jitter,
        )

    cache_dir.mkdir(parents=True, exist_ok=True)
    marker.touch()
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
    pacing_seconds: float = DEFAULT_DOWNLOAD_PACING_SECONDS,
    jitter: Callable[[], float] = lambda: random.uniform(0, DEFAULT_DOWNLOAD_PACING_SECONDS),
) -> AcousticBrainzData:
    ensure_shard_cached(
        mbid,
        cache_dir,
        client,
        bucket,
        tmp_dir,
        max_cached_shards,
        attempts,
        sleep,
        pacing_seconds,
        jitter,
    )
    try:
        return get_acousticbrainz_data(mbid, cache_dir)
    except AcousticBrainzDumpNotExtractedError:
        return AcousticBrainzData(highlevel=None, lowlevel=None)
