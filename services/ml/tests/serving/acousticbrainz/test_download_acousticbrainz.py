import tarfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from ml.serving.acousticbrainz.download_scripts.download_acousticbrainz import (
    HIGHLEVEL_INDEX_URL,
    LOWLEVEL_INDEX_URL,
    download_dumps,
    download_file,
    extract_archive,
    is_extracted,
    list_archive_urls,
    marker_file,
)


class _FakeStream:
    def __init__(self, response: MagicMock) -> None:
        self._response = response

    def __enter__(self) -> MagicMock:
        return self._response

    def __exit__(self, *args: object) -> bool:
        return False


def _fake_response(status_code: int, chunks: list[bytes]) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.iter_bytes.return_value = iter(chunks)
    return response


def test_list_archive_urls_keeps_only_archive_links() -> None:
    html = """
    <a href="?C=N;O=D">Name</a>
    <a href="../">Parent Directory</a>
    <a href="index.html">index.html</a>
    <a href="acousticbrainz-highlevel-json-20220623-0.tar.zst">part 0</a>
    <a href="acousticbrainz-highlevel-json-20220623-1.tar.bz2">part 1</a>
    <a href="MD5SUMS">checksums</a>
    """
    fake_response = MagicMock()
    fake_response.text = html
    fake_response.raise_for_status = MagicMock()

    with patch(
        "ml.serving.acousticbrainz.download_scripts.download_acousticbrainz.httpx.get",
        return_value=fake_response,
    ):
        urls = list_archive_urls("https://example.com/dumps/")

    assert urls == [
        "https://example.com/dumps/acousticbrainz-highlevel-json-20220623-0.tar.zst",
        "https://example.com/dumps/acousticbrainz-highlevel-json-20220623-1.tar.bz2",
    ]


def test_download_dumps_lists_both_highlevel_and_lowlevel_json_indexes(tmp_path: Path) -> None:
    seen_index_urls: list[str] = []

    def fake_list_archive_urls(index_url: str) -> list[str]:
        seen_index_urls.append(index_url)
        return [f"{index_url}part-0.tar.zst"]

    with (
        patch(
            "ml.serving.acousticbrainz.download_scripts.download_acousticbrainz.list_archive_urls",
            side_effect=fake_list_archive_urls,
        ),
        patch(
            "ml.serving.acousticbrainz.download_scripts.download_acousticbrainz.download_file"
        ) as fake_download_file,
    ):
        download_dumps(tmp_path)

    assert set(seen_index_urls) == {HIGHLEVEL_INDEX_URL, LOWLEVEL_INDEX_URL}
    assert fake_download_file.call_count == 2
    assert "lowlevel-features" not in str(fake_download_file.call_args_list)


def test_download_file_writes_full_content_when_nothing_downloaded_yet(tmp_path: Path) -> None:
    destination = tmp_path / "archive.tar.zst"
    fake_response = _fake_response(httpx.codes.OK, [b"hello ", b"world"])

    with patch(
        "ml.serving.acousticbrainz.download_scripts.download_acousticbrainz.httpx.stream",
        return_value=_FakeStream(fake_response),
    ):
        download_file("https://example.com/archive.tar.zst", destination)

    assert destination.read_bytes() == b"hello world"


def test_download_file_resumes_partial_download(tmp_path: Path) -> None:
    destination = tmp_path / "archive.tar.zst"
    destination.write_bytes(b"hello ")
    fake_response = _fake_response(httpx.codes.PARTIAL_CONTENT, [b"world"])

    with patch(
        "ml.serving.acousticbrainz.download_scripts.download_acousticbrainz.httpx.stream",
        return_value=_FakeStream(fake_response),
    ):
        download_file("https://example.com/archive.tar.zst", destination)

    assert destination.read_bytes() == b"hello world"


def test_download_file_restarts_when_server_ignores_range_header(tmp_path: Path) -> None:
    destination = tmp_path / "archive.tar.zst"
    destination.write_bytes(b"stale partial data")
    fake_response = _fake_response(httpx.codes.OK, [b"full content"])

    with patch(
        "ml.serving.acousticbrainz.download_scripts.download_acousticbrainz.httpx.stream",
        return_value=_FakeStream(fake_response),
    ):
        download_file("https://example.com/archive.tar.zst", destination)

    assert destination.read_bytes() == b"full content"


def test_download_file_skips_when_already_fully_downloaded(tmp_path: Path) -> None:
    destination = tmp_path / "archive.tar.zst"
    destination.write_bytes(b"already complete")
    fake_response = _fake_response(httpx.codes.REQUESTED_RANGE_NOT_SATISFIABLE, [])

    with patch(
        "ml.serving.acousticbrainz.download_scripts.download_acousticbrainz.httpx.stream",
        return_value=_FakeStream(fake_response),
    ):
        download_file("https://example.com/archive.tar.zst", destination)

    assert destination.read_bytes() == b"already complete"
    fake_response.raise_for_status.assert_not_called()


def test_extract_archive_rejects_unsupported_format(tmp_path: Path) -> None:
    archive_path = tmp_path / "archive.zip"
    archive_path.touch()

    with pytest.raises(ValueError, match="unsupported archive format"):
        extract_archive(archive_path, tmp_path)


def test_extract_archive_extracts_tar_bz2_and_marks_it_done(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "track.json").write_text("{}", encoding="utf-8")

    archive_path = tmp_path / "dump.tar.bz2"
    with tarfile.open(archive_path, mode="w:bz2") as tar:
        tar.add(source_dir / "track.json", arcname="track.json")

    destination_dir = tmp_path / "extracted"
    destination_dir.mkdir()

    assert not is_extracted(archive_path, destination_dir)

    extract_archive(archive_path, destination_dir)

    assert (destination_dir / "track.json").read_text(encoding="utf-8") == "{}"
    assert is_extracted(archive_path, destination_dir)
    assert marker_file(archive_path, destination_dir).exists()
