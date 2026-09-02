import re
import tarfile
from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

import httpx
import zstandard as zstd

from ml.core.config import Settings
from ml.serving.acousticbrainz.constants import DUMP_VERSION

HIGHLEVEL_INDEX_URL = (
    "https://data.metabrainz.org/pub/musicbrainz/acousticbrainz/dumps/"
    f"acousticbrainz-highlevel-json-{DUMP_VERSION}/"
)
LOWLEVEL_ARCHIVE_URLS = [
    "https://data.metabrainz.org/pub/musicbrainz/acousticbrainz/dumps/"
    f"acousticbrainz-lowlevel-features-{DUMP_VERSION}/"
    f"acousticbrainz-lowlevel-features-{DUMP_VERSION}-rhythm.tar.zst",
    "https://data.metabrainz.org/pub/musicbrainz/acousticbrainz/dumps/"
    f"acousticbrainz-lowlevel-features-{DUMP_VERSION}/"
    f"acousticbrainz-lowlevel-features-{DUMP_VERSION}-tonal.tar.zst",
]
ARCHIVE_SUFFIXES = (".tar.zst", ".tar.bz2")
CHUNK_SIZE = 1024 * 1024
HTTP_PARTIAL_CONTENT = 206
HTTP_RANGE_NOT_SATISFIABLE = 416


def list_highlevel_archive_urls(index_url: str = HIGHLEVEL_INDEX_URL) -> list[str]:
    response = httpx.get(index_url)
    response.raise_for_status()
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', response.text)
    return [
        str(httpx.URL(index_url).join(href)) for href in hrefs if href.endswith(ARCHIVE_SUFFIXES)
    ]


def download_file(url: str, destination: Path) -> None:
    existing_size = destination.stat().st_size if destination.exists() else 0
    headers = {"Range": f"bytes={existing_size}-"} if existing_size else {}

    with httpx.stream("GET", url, headers=headers, follow_redirects=True) as response:
        if response.status_code == HTTP_RANGE_NOT_SATISFIABLE:
            return

        resuming = bool(existing_size) and response.status_code == HTTP_PARTIAL_CONTENT
        response.raise_for_status()

        with destination.open("ab" if resuming else "wb") as output:
            for chunk in response.iter_bytes(CHUNK_SIZE):
                output.write(chunk)


def marker_file(archive_path: Path, destination_dir: Path) -> Path:
    return destination_dir / f".{archive_path.name}_extracted"


def is_extracted(archive_path: Path, destination_dir: Path) -> bool:
    return marker_file(archive_path, destination_dir).exists()


def extract_archive(archive_path: Path, destination_dir: Path) -> None:
    if archive_path.name.endswith(".tar.zst"):
        decompressor = zstd.ZstdDecompressor()
        with (
            archive_path.open("rb") as compressed,
            decompressor.stream_reader(compressed) as reader,
            tarfile.open(fileobj=reader, mode="r|") as tar,
        ):
            tar.extractall(path=destination_dir, filter="data")
    elif archive_path.name.endswith(".tar.bz2"):
        with tarfile.open(archive_path, mode="r:bz2") as tar:
            tar.extractall(path=destination_dir, filter="data")
    else:
        raise ValueError(f"unsupported archive format: {archive_path.name}")

    marker_file(archive_path, destination_dir).touch()


def download_dumps(dump_dir: Path) -> list[Path]:
    dump_dir.mkdir(parents=True, exist_ok=True)
    urls = [*LOWLEVEL_ARCHIVE_URLS, *list_highlevel_archive_urls()]
    destinations = [dump_dir / url.rsplit("/", maxsplit=1)[-1] for url in urls]

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(download_file, urls, destinations))

    return destinations


def extract_dumps(archive_paths: Iterable[Path], extract_dir: Path) -> None:
    extract_dir.mkdir(parents=True, exist_ok=True)
    pending = [path for path in archive_paths if not is_extracted(path, extract_dir)]

    with ProcessPoolExecutor() as executor:
        list(executor.map(extract_archive, pending, [extract_dir] * len(pending)))


def main(settings: Settings) -> None:
    archive_paths = download_dumps(settings.acousticbrainz_dump_dir)
    extract_dumps(archive_paths, settings.acousticbrainz_extract_dir)


if __name__ == "__main__":
    main(Settings())
