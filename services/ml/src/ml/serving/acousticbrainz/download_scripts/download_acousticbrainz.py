from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import re

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
    print(f"Downloading {destination.name}...")

    existing_size = destination.stat().st_size if destination.exists() else 0

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
