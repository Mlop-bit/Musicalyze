import io
import json
import tarfile
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
import zstandard as zstd
from botocore.exceptions import ClientError

from ml.serving.acousticbrainz.constants import DUMP_VERSION
from ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3 import (
    HIGHLEVEL_DIR_NAME,
    LOWLEVEL_DIR_NAME,
    ArchiveTarget,
    ProgressReporter,
    archive_stem,
    build_archive_plan,
    done_marker_key,
    is_archive_done,
    main,
    mark_archive_done,
    process_archive,
    process_archive_with_retries,
    process_one_archive,
    stream_archive_bytes,
)
from ml.serving.acousticbrainz.s3_shards import unpack_shard


def test_archive_stem_strips_tar_zst_suffix() -> None:
    url = "https://example.com/dumps/acousticbrainz-highlevel-json-20220623-0.tar.zst"
    assert archive_stem(url) == "acousticbrainz-highlevel-json-20220623-0"


def test_archive_stem_strips_tar_bz2_suffix() -> None:
    url = "https://example.com/dumps/part.tar.bz2"
    assert archive_stem(url) == "part"


def _single_archive_per_index(index_url: str) -> list[str]:
    return [f"{index_url}0.tar.zst"]


def test_build_archive_plan_tags_each_url_with_dataset_and_level() -> None:
    with patch(
        "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.list_archive_urls",
        side_effect=_single_archive_per_index,
    ):
        plan = build_archive_plan()

    assert (
        ArchiveTarget(
            url=f"https://data.metabrainz.org/pub/musicbrainz/acousticbrainz/dumps/acousticbrainz-highlevel-json-{DUMP_VERSION}/0.tar.zst",
            dataset_dir_name=HIGHLEVEL_DIR_NAME,
            level="highlevel",
        )
        in plan
    )
    assert (
        ArchiveTarget(
            url=f"https://data.metabrainz.org/pub/musicbrainz/acousticbrainz/dumps/acousticbrainz-lowlevel-json-{DUMP_VERSION}/0.tar.zst",
            dataset_dir_name=LOWLEVEL_DIR_NAME,
            level="lowlevel",
        )
        in plan
    )


def test_done_marker_key_is_namespaced_under_dot_done() -> None:
    assert done_marker_key("acousticbrainz-highlevel-json-20220623-0") == (
        "acousticbrainz/.done/acousticbrainz-highlevel-json-20220623-0"
    )


def test_is_archive_done_returns_false_when_marker_missing() -> None:
    client = MagicMock()
    client.head_object.side_effect = ClientError(
        {"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject"
    )

    assert is_archive_done(client, "bucket", "stem") is False


def test_is_archive_done_returns_true_when_marker_present() -> None:
    client = MagicMock()
    client.head_object.return_value = {}

    assert is_archive_done(client, "bucket", "stem") is True


def test_is_archive_done_reraises_unexpected_client_errors() -> None:
    client = MagicMock()
    client.head_object.side_effect = ClientError(
        {"Error": {"Code": "403", "Message": "Forbidden"}}, "HeadObject"
    )

    try:
        is_archive_done(client, "bucket", "stem")
    except ClientError:
        pass
    else:
        raise AssertionError("expected ClientError to propagate")


def test_mark_archive_done_puts_empty_marker_object() -> None:
    client = MagicMock()

    mark_archive_done(client, "bucket", "stem")

    client.put_object.assert_called_once_with(
        Bucket="bucket", Key="acousticbrainz/.done/stem", Body=b""
    )


def _make_source_archive_bytes(entries: list[tuple[str, bytes]]) -> bytes:
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
        for name, content in entries:
            info = tarfile.TarInfo(name=name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return zstd.ZstdCompressor().compress(tar_buffer.getvalue())


class _FakeStreamResponse:
    def __init__(self, body: bytes, status_code: int = 200) -> None:
        self._body = body
        self.status_code = status_code
        self.headers = {"content-length": str(len(body))}

    def raise_for_status(self) -> None:
        pass

    def iter_bytes(self, chunk_size: int) -> Iterator[bytes]:
        for start in range(0, len(self._body), chunk_size):
            yield self._body[start : start + chunk_size]


class _FakeStreamContext:
    def __init__(self, response: _FakeStreamResponse) -> None:
        self._response = response

    def __enter__(self) -> _FakeStreamResponse:
        return self._response

    def __exit__(self, *args: object) -> bool:
        return False


class _FailAfterYieldingResponse(_FakeStreamResponse):
    def iter_bytes(self, chunk_size: int) -> Iterator[bytes]:
        yield self._body
        raise httpx.ReadError("connection reset")


def test_process_archive_uploads_one_chunk_per_shard_and_cleans_up(tmp_path: Path) -> None:
    payload = {"mood": "happy"}
    archive_bytes = _make_source_archive_bytes(
        [
            (
                f"{HIGHLEVEL_DIR_NAME}/highlevel/00/1/aaa-0.json",
                json.dumps(payload).encode("utf-8"),
            ),
        ]
    )
    target = ArchiveTarget(
        url="https://example.com/dumps/acousticbrainz-highlevel-json-20220623-0.tar.zst",
        dataset_dir_name=HIGHLEVEL_DIR_NAME,
        level="highlevel",
    )
    client = MagicMock()
    uploaded_paths: list[Path] = []

    def fake_upload_file(local_path: str, bucket: str, key: str) -> None:
        uploaded_paths.append(Path(local_path))
        assert bucket == "dev-bucket"
        assert key == (
            "acousticbrainz/acousticbrainz-highlevel-json-20220623/highlevel/00/"
            "acousticbrainz-highlevel-json-20220623-0-00-1.tar.zst"
        )
        unpack_shard(Path(local_path), tmp_path / "restored")

    client.upload_file.side_effect = fake_upload_file

    with patch(
        "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.httpx.stream",
        return_value=_FakeStreamContext(_FakeStreamResponse(archive_bytes)),
    ):
        process_archive(target, tmp_path / "work", client, "dev-bucket", len(archive_bytes))

    assert client.upload_file.call_count == 1
    assert not uploaded_paths[0].exists()
    assert not (tmp_path / "work" / "acousticbrainz-highlevel-json-20220623-0").exists()
    restored = tmp_path / "restored" / "1" / "aaa-0.json"
    assert json.loads(restored.read_text(encoding="utf-8")) == payload


def test_stream_archive_bytes_yields_the_full_body_in_one_pass() -> None:
    body = b"a" * 100
    progress: list[tuple[int, int]] = []

    with patch(
        "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.httpx.stream",
        return_value=_FakeStreamContext(_FakeStreamResponse(body)),
    ) as mock_stream:
        collected = b"".join(
            stream_archive_bytes(
                "https://example.com/x",
                len(body),
                lambda downloaded, expected: progress.append((downloaded, expected)),
            )
        )

    mock_stream.assert_called_once_with(
        "GET", "https://example.com/x", headers={}, follow_redirects=True, timeout=60.0
    )
    assert collected == body
    assert progress[-1] == (100, 100)


def test_stream_archive_bytes_reconnects_with_a_range_header_after_a_transient_failure() -> None:
    first_chunk = b"a" * 40
    remainder = b"b" * 60

    with patch(
        "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.httpx.stream",
        side_effect=[
            _FakeStreamContext(_FailAfterYieldingResponse(first_chunk)),
            _FakeStreamContext(_FakeStreamResponse(remainder, status_code=206)),
        ],
    ) as mock_stream:
        collected = b"".join(
            stream_archive_bytes("https://example.com/x", 100, sleep=lambda _seconds: None)
        )

    assert collected == first_chunk + remainder
    assert mock_stream.call_args_list[0].kwargs["headers"] == {}
    assert mock_stream.call_args_list[1].kwargs["headers"] == {"Range": "bytes=40-"}


def test_stream_archive_bytes_backs_off_between_reconnects() -> None:
    first_chunk = b"a" * 40
    remainder = b"b" * 60
    sleeps: list[float] = []

    with patch(
        "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.httpx.stream",
        side_effect=[
            _FakeStreamContext(_FailAfterYieldingResponse(first_chunk)),
            _FakeStreamContext(_FailAfterYieldingResponse(b"")),
            _FakeStreamContext(_FakeStreamResponse(remainder, status_code=206)),
        ],
    ):
        collected = b"".join(
            stream_archive_bytes("https://example.com/x", 100, sleep=sleeps.append)
        )

    assert collected == first_chunk + remainder
    assert sleeps == [2, 4]


def _always_fail_to_connect(*_args: object, **_kwargs: object) -> _FakeStreamContext:
    return _FakeStreamContext(_FailAfterYieldingResponse(b""))


def test_stream_archive_bytes_gives_up_after_max_reconnects() -> None:
    with (
        patch(
            "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.httpx.stream",
            side_effect=_always_fail_to_connect,
        ) as mock_stream,
        pytest.raises(httpx.HTTPError),
    ):
        list(
            stream_archive_bytes(
                "https://example.com/x",
                100,
                max_reconnects=2,
                sleep=lambda _seconds: None,
            )
        )

    assert mock_stream.call_count == 3


def test_process_archive_with_retries_retries_transient_failures_then_succeeds() -> None:
    target = ArchiveTarget(url="https://example.com/x-0.tar.zst", dataset_dir_name="d", level="l")
    attempts_made: list[int] = []
    sleeps: list[float] = []

    def flaky_process_archive(*args: object, **kwargs: object) -> None:
        attempts_made.append(1)
        if len(attempts_made) < 3:
            raise TimeoutError("connection reset")

    with patch(
        "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.process_archive",
        side_effect=flaky_process_archive,
    ):
        succeeded = process_archive_with_retries(
            target,
            Path("/tmp/does-not-matter"),
            MagicMock(),
            "bucket",
            1000,
            attempts=3,
            sleep=sleeps.append,
        )

    assert succeeded is True
    assert len(attempts_made) == 3
    assert sleeps == [2, 4]


def test_process_archive_with_retries_gives_up_after_max_attempts() -> None:
    target = ArchiveTarget(url="https://example.com/x-0.tar.zst", dataset_dir_name="d", level="l")

    with patch(
        "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.process_archive",
        side_effect=TimeoutError("connection reset"),
    ):
        succeeded = process_archive_with_retries(
            target,
            Path("/tmp/does-not-matter"),
            MagicMock(),
            "bucket",
            1000,
            attempts=2,
            sleep=lambda _seconds: None,
        )

    assert succeeded is False


def test_process_archive_with_retries_caps_the_backoff_delay() -> None:
    target = ArchiveTarget(url="https://example.com/x-0.tar.zst", dataset_dir_name="d", level="l")
    sleeps: list[float] = []

    with patch(
        "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.process_archive",
        side_effect=TimeoutError("connection reset"),
    ):
        succeeded = process_archive_with_retries(
            target,
            Path("/tmp/does-not-matter"),
            MagicMock(),
            "bucket",
            1000,
            attempts=8,
            sleep=sleeps.append,
        )

    assert succeeded is False
    assert sleeps == [2, 4, 8, 16, 32, 60, 60]


def test_process_one_archive_skips_when_already_marked_done() -> None:
    client = MagicMock()
    client.head_object.return_value = {}
    reporter = MagicMock()
    target = ArchiveTarget(url="https://example.com/x-0.tar.zst", dataset_dir_name="d", level="l")

    process_one_archive(
        1, target, Path("/tmp/does-not-matter"), client, "bucket", 1000, 1024, reporter
    )

    reporter.skip_archive.assert_called_once_with(1, "x-0", 1000)
    client.put_object.assert_not_called()


def test_process_one_archive_marks_done_and_reports_finish_on_success() -> None:
    client = MagicMock()
    client.head_object.side_effect = ClientError(
        {"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject"
    )
    reporter = MagicMock()
    target = ArchiveTarget(url="https://example.com/x-0.tar.zst", dataset_dir_name="d", level="l")

    with patch(
        "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.process_archive_with_retries",
        return_value=True,
    ):
        process_one_archive(
            1, target, Path("/tmp/does-not-matter"), client, "bucket", 1000, 1024, reporter
        )

    client.put_object.assert_called_once_with(
        Bucket="bucket", Key="acousticbrainz/.done/x-0", Body=b""
    )
    reporter.finish_archive.assert_called_once_with(1000)


def test_process_one_archive_does_not_mark_done_when_retries_are_exhausted() -> None:
    client = MagicMock()
    client.head_object.side_effect = ClientError(
        {"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject"
    )
    reporter = MagicMock()
    target = ArchiveTarget(url="https://example.com/x-0.tar.zst", dataset_dir_name="d", level="l")

    with patch(
        "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.process_archive_with_retries",
        return_value=False,
    ):
        process_one_archive(
            1, target, Path("/tmp/does-not-matter"), client, "bucket", 1000, 1024, reporter
        )

    client.put_object.assert_not_called()
    reporter.finish_archive.assert_not_called()


def test_main_processes_every_archive_in_the_plan_concurrently(tmp_path: Path) -> None:
    plan = [
        ArchiveTarget(url=f"https://example.com/x-{i}.tar.zst", dataset_dir_name="d", level="l")
        for i in range(5)
    ]
    settings = MagicMock(s3_bucket="bucket")
    seen_indexes: list[int] = []

    def fake_process_one_archive(
        index: int, target: ArchiveTarget, *_args: object, **_kwargs: object
    ) -> None:
        seen_indexes.append(index)

    with (
        patch(
            "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.s3_client",
            return_value=MagicMock(),
        ),
        patch(
            "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.build_archive_plan",
            return_value=plan,
        ),
        patch(
            "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.archive_content_length",
            return_value=100,
        ),
        patch(
            "ml.serving.acousticbrainz.download_scripts.upload_acousticbrainz_to_s3.process_one_archive",
            side_effect=fake_process_one_archive,
        ) as mock_process_one,
    ):
        main(settings, tmp_path, max_workers=2)

    assert sorted(seen_indexes) == [1, 2, 3, 4, 5]
    assert mock_process_one.call_count == 5
    first_call_args = mock_process_one.call_args_list[0][0]
    assert first_call_args[2] == tmp_path
    assert first_call_args[4] == "bucket"
    assert first_call_args[5] == 100


def test_progress_reporter_computes_overall_percentage_across_archives(
    capsys: pytest.CaptureFixture[str],
) -> None:
    reporter = ProgressReporter(total_bytes=1000, plan_size=2)
    on_progress = reporter.start_archive(1, "archive-0")

    on_progress(250, 500)

    output = capsys.readouterr().out
    assert "50.0% archive" in output
    assert "25.0% overall" in output

    reporter.finish_archive(500)
    on_progress = reporter.start_archive(2, "archive-1")
    on_progress(250, 500)

    output = capsys.readouterr().out
    assert "50.0% archive" in output
    assert "75.0% overall" in output


def test_progress_reporter_skip_archive_advances_completed_bytes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    reporter = ProgressReporter(total_bytes=1000, plan_size=2)

    reporter.skip_archive(1, "archive-0", 500)

    assert reporter.completed_bytes == 500
    assert "already uploaded, skipping (50.0%)" in capsys.readouterr().out
