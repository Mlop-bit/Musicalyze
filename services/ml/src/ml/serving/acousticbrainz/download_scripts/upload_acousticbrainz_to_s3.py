import io
import shutil
import tarfile
import threading
import time
from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import WriteableBuffer

import httpx
import zstandard as zstd
from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import ClientError
from mypy_boto3_s3.client import S3Client

from ml.core.artifact_store import s3_client
from ml.core.config import Settings
from ml.serving.acousticbrainz.download_scripts.download_acousticbrainz import (
    HIGHLEVEL_INDEX_URL,
    LOWLEVEL_INDEX_URL,
    list_archive_urls,
)
from ml.serving.acousticbrainz.find_song_acousticbrainz import (
    HIGHLEVEL_DIR_NAME,
    LOWLEVEL_DIR_NAME,
)
from ml.serving.acousticbrainz.s3_shards import (
    DEFAULT_ROTATION_BYTES,
    S3_PREFIX,
    repack_archive_stream,
    shard_prefix,
)

DONE_MARKER_PREFIX = f"{S3_PREFIX}/.done/"
NOT_FOUND_ERROR_CODES = frozenset({"404", "NoSuchKey", "NotFound"})
DEFAULT_UPLOAD_ATTEMPTS = 6
DEFAULT_MAX_WORKERS = 6
MAX_BACKOFF_SECONDS = 60.0
DOWNLOAD_CHUNK_BYTES = 1024 * 1024
DEFAULT_MAX_RECONNECTS = 50

ProgressCallback = Callable[[int, int], None]


@dataclass(frozen=True)
class ArchiveTarget:
    url: str
    dataset_dir_name: str
    level: str


def archive_stem(url: str) -> str:
    name = url.rsplit("/", maxsplit=1)[-1]
    for suffix in (".tar.zst", ".tar.bz2"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def build_archive_plan() -> list[ArchiveTarget]:
    return [
        *(
            ArchiveTarget(url, HIGHLEVEL_DIR_NAME, "highlevel")
            for url in list_archive_urls(HIGHLEVEL_INDEX_URL)
        ),
        *(
            ArchiveTarget(url, LOWLEVEL_DIR_NAME, "lowlevel")
            for url in list_archive_urls(LOWLEVEL_INDEX_URL)
        ),
    ]


def done_marker_key(stem: str) -> str:
    return f"{DONE_MARKER_PREFIX}{stem}"


def is_archive_done(client: S3Client, bucket: str, stem: str) -> bool:
    try:
        client.head_object(Bucket=bucket, Key=done_marker_key(stem))
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") in NOT_FOUND_ERROR_CODES:
            return False
        raise
    return True


def mark_archive_done(client: S3Client, bucket: str, stem: str) -> None:
    client.put_object(Bucket=bucket, Key=done_marker_key(stem), Body=b"")


def _backoff_seconds(attempt: int) -> float:
    return min(float(2**attempt), MAX_BACKOFF_SECONDS)


class _IterReader(io.RawIOBase):
    def __init__(self, chunks: Iterable[bytes]) -> None:
        self._iterator = iter(chunks)
        self._buffer = b""

    def readable(self) -> bool:
        return True

    def readinto(self, b: "WriteableBuffer") -> int:
        output = memoryview(b)  # type: ignore[arg-type]
        while len(self._buffer) < len(output):
            try:
                self._buffer += next(self._iterator)
            except StopIteration:
                break
        chunk, self._buffer = self._buffer[: len(output)], self._buffer[len(output) :]
        output[: len(chunk)] = chunk
        return len(chunk)


def stream_archive_bytes(
    url: str,
    expected_bytes: int,
    on_progress: ProgressCallback | None = None,
    timeout: float = 60.0,
    max_reconnects: int = DEFAULT_MAX_RECONNECTS,
    sleep: Callable[[float], None] = time.sleep,
) -> Iterator[bytes]:
    downloaded = 0
    reconnects = 0
    while downloaded < expected_bytes:
        headers = {"Range": f"bytes={downloaded}-"} if downloaded else {}
        try:
            with httpx.stream(
                "GET", url, headers=headers, follow_redirects=True, timeout=timeout
            ) as response:
                if downloaded and response.status_code != 206:
                    raise OSError(f"server does not support resuming {url}")
                response.raise_for_status()
                for chunk in response.iter_bytes(DOWNLOAD_CHUNK_BYTES):
                    downloaded += len(chunk)
                    if on_progress is not None:
                        on_progress(downloaded, expected_bytes)
                    yield chunk
        except (httpx.HTTPError, OSError):
            reconnects += 1
            if reconnects > max_reconnects:
                raise
            sleep(_backoff_seconds(reconnects))


def process_archive(
    target: ArchiveTarget,
    tmp_dir: Path,
    client: S3Client,
    bucket: str,
    expected_bytes: int,
    rotation_bytes: int = DEFAULT_ROTATION_BYTES,
    on_progress: ProgressCallback | None = None,
) -> None:
    stem = archive_stem(target.url)
    output_dir = tmp_dir / stem
    tmp_dir.mkdir(parents=True, exist_ok=True)

    decompressor = zstd.ZstdDecompressor()
    with (
        decompressor.stream_reader(
            _IterReader(stream_archive_bytes(target.url, expected_bytes, on_progress))  # type: ignore[arg-type]
        ) as reader,
        tarfile.open(fileobj=reader, mode="r|") as source_tar,
    ):
        for shard, chunk_path in repack_archive_stream(source_tar, output_dir, rotation_bytes):
            prefix = shard_prefix(target.dataset_dir_name, target.level, shard)
            key = f"{prefix}{stem}-{chunk_path.name}"
            client.upload_file(str(chunk_path), bucket, key)
            chunk_path.unlink()

    shutil.rmtree(output_dir, ignore_errors=True)


def process_archive_with_retries(
    target: ArchiveTarget,
    tmp_dir: Path,
    client: S3Client,
    bucket: str,
    expected_bytes: int,
    rotation_bytes: int = DEFAULT_ROTATION_BYTES,
    on_progress: ProgressCallback | None = None,
    attempts: int = DEFAULT_UPLOAD_ATTEMPTS,
    sleep: Callable[[float], None] = time.sleep,
) -> bool:
    stem = archive_stem(target.url)
    for attempt in range(1, attempts + 1):
        try:
            process_archive(
                target, tmp_dir, client, bucket, expected_bytes, rotation_bytes, on_progress
            )
        except (httpx.HTTPError, OSError, ClientError, S3UploadFailedError) as error:
            print(f"\n{stem}: attempt {attempt}/{attempts} failed: {error}")
            if attempt < attempts:
                sleep(_backoff_seconds(attempt))
        else:
            return True
    return False


def archive_content_length(url: str) -> int:
    response = httpx.head(url, follow_redirects=True)
    response.raise_for_status()
    return int(response.headers.get("content-length", "0"))


class ProgressReporter:
    def __init__(self, total_bytes: int, plan_size: int) -> None:
        self.total_bytes = total_bytes or 1
        self.plan_size = plan_size
        self.completed_bytes = 0
        self._last_permille = -1
        self._lock = threading.Lock()

    def start_archive(self, index: int, stem: str) -> ProgressCallback:
        def on_progress(downloaded: int, expected: int) -> None:
            with self._lock:
                archive_pct = downloaded / expected if expected else 0.0
                overall_pct = (self.completed_bytes + downloaded) / self.total_bytes
                permille = int(overall_pct * 1000)
                if permille == self._last_permille:
                    return
                self._last_permille = permille
                print(
                    f"\r[{index}/{self.plan_size}] {stem}: "
                    f"{archive_pct:6.1%} archive | {overall_pct:6.1%} overall     ",
                    end="",
                    flush=True,
                )

        return on_progress

    def finish_archive(self, size_bytes: int) -> None:
        with self._lock:
            self.completed_bytes += size_bytes
            print()

    def skip_archive(self, index: int, stem: str, size_bytes: int) -> None:
        with self._lock:
            self.completed_bytes += size_bytes
            overall_pct = self.completed_bytes / self.total_bytes
            print(
                f"[{index}/{self.plan_size}] {stem}: already uploaded, skipping ({overall_pct:.1%})"
            )


def process_one_archive(
    index: int,
    target: ArchiveTarget,
    tmp_dir: Path,
    client: S3Client,
    bucket: str,
    expected_bytes: int,
    rotation_bytes: int,
    reporter: ProgressReporter,
) -> None:
    stem = archive_stem(target.url)
    if is_archive_done(client, bucket, stem):
        reporter.skip_archive(index, stem, expected_bytes)
        return

    succeeded = process_archive_with_retries(
        target,
        tmp_dir,
        client,
        bucket,
        expected_bytes,
        rotation_bytes,
        reporter.start_archive(index, stem),
    )
    if not succeeded:
        print(f"{stem}: giving up after retries, will retry on next run")
        return

    mark_archive_done(client, bucket, stem)
    reporter.finish_archive(expected_bytes)


def main(
    settings: Settings,
    tmp_dir: Path,
    rotation_bytes: int = DEFAULT_ROTATION_BYTES,
    max_workers: int = DEFAULT_MAX_WORKERS,
) -> None:
    client = s3_client(settings)
    plan = build_archive_plan()
    sizes = {target.url: archive_content_length(target.url) for target in plan}
    reporter = ProgressReporter(sum(sizes.values()), len(plan))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                process_one_archive,
                index,
                target,
                tmp_dir,
                client,
                settings.s3_bucket,
                sizes[target.url],
                rotation_bytes,
                reporter,
            )
            for index, target in enumerate(plan, start=1)
        ]
        for future in as_completed(futures):
            future.result()

    print(f"Done: {len(plan)}/{len(plan)} archives, {reporter.completed_bytes / 1024**3:.1f} GiB")


if __name__ == "__main__":
    main(Settings(), Path("acousticbrainz-s3-tmp"))  # type: ignore[call-arg]
