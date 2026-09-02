from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import re
import os
import logging
import argparse
import tarfile
import concurrent.futures
import zstandard as zstd

download_dir = Path("acousticbrainz-dumps")
download_dir.mkdir(exist_ok=True)

highlevel_url = (
    "https://data.metabrainz.org/pub/musicbrainz/acousticbrainz/"
    "dumps/acousticbrainz-highlevel-json-20220623/"
)

files_to_download = [
    "https://data.metabrainz.org/pub/musicbrainz/acousticbrainz/dumps/"
    "acousticbrainz-lowlevel-features-20220623/"
    "acousticbrainz-lowlevel-features-20220623-rhythm.tar.zst",

    "https://data.metabrainz.org/pub/musicbrainz/acousticbrainz/dumps/"
    "acousticbrainz-lowlevel-features-20220623/"
    "acousticbrainz-lowlevel-features-20220623-tonal.tar.zst",
]


def download_file(url: str, destination: Path) -> None:
    # For Resume-Function if local file is wrongly labeled as not completely downloaded
    # 1. Check the size of the local File
    existing_size = destination.stat().st_size if destination.exists() else 0

    # 2. Get file size from server
    try:
        req_head = Request(url, method="HEAD")
        with urlopen(req_head) as resp:
            server_size = int(resp.headers.get("Content-Length", 0))
    except Exception:
        server_size = 0

    # 3. Compare sizes
    if server_size and existing_size >= server_size:
        print(f"Skipping {destination.name} (already fully downloaded).")
        return

    print(f"Downloading {destination.name}...")

    headers = {}
    if existing_size:
        headers["Range"] = f"bytes={existing_size}-"

    request = Request(url, headers=headers)

    with urlopen(request) as response:
        status = response.status

        # If the server does not support resuming, start over.
        if existing_size and status != 206:
            existing_size = 0

        mode = "ab" if existing_size else "wb"

        with destination.open(mode) as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)

    print(f"Finished: {destination}")


# Read the high-level dump directory listing
with urlopen(highlevel_url) as response:
    html = response.read().decode("utf-8", errors="replace")

links = re.findall(r'href=["\']([^"\']+)["\']', html)

for link in links:
    if link in ("../", "./") or link.startswith("?"):
        continue

    file_url = urljoin(highlevel_url, link)
    filename = Path(link).name

    if filename and filename != "index.html":
        files_to_download.append(file_url)


for url in files_to_download:
    filename = Path(url.split("?")[0]).name
    destination = download_dir / filename
    download_file(url, destination)

print("All download_scripts completed.")


extract_dir = Path("acousticbrainz-extracted")
extract_dir.mkdir(exist_ok=True)


def extract_archive(archive_path: Path) -> None:
    # Create a unique marker folder or flag for this specific archive
    marker_file = extract_dir / f".{archive_path.name}_extracted"

    # If the marker exists, skip it entirely!
    if marker_file.exists():
        print(f"Skipping extraction for {archive_path.name} (already done).")
        return

    print(f"Extracting {archive_path.name}...")
    try:
        if archive_path.name.endswith('.tar.zst'):
            dctx = zstd.ZstdDecompressor()
            with open(archive_path, 'rb') as ifh:
                with dctx.stream_reader(ifh) as reader:
                    with tarfile.open(fileobj=reader, mode='r|') as tar:
                        tar.extractall(path=extract_dir, filter='data')

        elif archive_path.name.endswith('.tar.bz2'):
            with tarfile.open(archive_path, mode='r:bz2') as tar:
                tar.extractall(path=extract_dir, filter='data')

        # Drop a tiny marker file so we know this archive finished successfully
        marker_file.touch()
        print(f"Finished extracting: {archive_path.name}")

    except Exception as e:
        print(f"Error extracting {archive_path.name}: {e}")

archives = list(download_dir.glob("*.tar.*"))

if archives:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(extract_archive, archives)
    print("All archives extracted successfully.")
else:
    print("No archives found to extract.")