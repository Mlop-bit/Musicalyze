import json
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from ml.serving.acousticbrainz.find_song_acousticbrainz import HIGHLEVEL_DIR_NAME, LOWLEVEL_DIR_NAME
from ml.serving.acousticbrainz.s3_lookup import ensure_shard_cached, get_acousticbrainz_data_from_s3
from ml.serving.acousticbrainz.s3_shards import pack_shard

MBID = "1a0a0ac2-b294-4794-b275-1b064b31b3d5"
SHARD = MBID[:2]
SUBSHARD = MBID[2]


def _seed_bucket_with_shard(
    tmp_path: Path,
    dataset_dir_name: str,
    level: str,
    payload: dict[str, object],
    mbid: str = MBID,
) -> dict[str, bytes]:
    shard, subshard = mbid[:2], mbid[2]
    shard_source = tmp_path / f"shard_source-{dataset_dir_name}-{level}-{mbid}"
    submission_dir = shard_source / subshard
    submission_dir.mkdir(parents=True)
    (submission_dir / f"{mbid}-0.json").write_text(json.dumps(payload), encoding="utf-8")

    chunk_path = tmp_path / f"chunk-{dataset_dir_name}-{level}-{mbid}.tar.zst"
    pack_shard(shard_source, chunk_path)
    key = f"acousticbrainz/{dataset_dir_name}/{level}/{shard}/archive-0-{shard}-1.tar.zst"
    return {key: chunk_path.read_bytes()}


def _fake_client(objects_by_key: dict[str, bytes], monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    client = MagicMock()

    def list_objects_v2(Bucket: str, Prefix: str) -> dict[str, object]:  # noqa: N803
        return {"Contents": [{"Key": key} for key in objects_by_key if key.startswith(Prefix)]}

    def generate_presigned_url(
        ClientMethod: str,  # noqa: N803
        Params: dict[str, str],  # noqa: N803
        ExpiresIn: int,  # noqa: N803
    ) -> str:
        return f"https://fake-s3.test/{Params['Key']}"

    @contextmanager
    def fake_stream(method: str, url: str, timeout: float) -> Generator[MagicMock]:
        key = url.removeprefix("https://fake-s3.test/")
        response = MagicMock()
        response.iter_bytes.return_value = iter([objects_by_key[key]])
        yield response

    client.list_objects_v2.side_effect = list_objects_v2
    client.generate_presigned_url.side_effect = generate_presigned_url
    monkeypatch.setattr("ml.serving.acousticbrainz.s3_lookup.httpx.stream", fake_stream)
    return client


def test_ensure_shard_cached_downloads_and_unpacks_both_datasets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    objects: dict[str, bytes] = {}
    objects.update(_seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", {"a": 1}))
    objects.update(_seed_bucket_with_shard(tmp_path, LOWLEVEL_DIR_NAME, "lowlevel", {"b": 2}))
    client = _fake_client(objects, monkeypatch)
    cache_dir = tmp_path / "cache"

    ensure_shard_cached(MBID, cache_dir, client, "bucket", tmp_path / "work", include_lowlevel=True)

    filename = f"{MBID}-0.json"
    highlevel_file = cache_dir / HIGHLEVEL_DIR_NAME / "highlevel" / SHARD / SUBSHARD / filename
    lowlevel_file = cache_dir / LOWLEVEL_DIR_NAME / "lowlevel" / SHARD / SUBSHARD / filename
    assert json.loads(highlevel_file.read_text(encoding="utf-8")) == {"a": 1}
    assert json.loads(lowlevel_file.read_text(encoding="utf-8")) == {"b": 2}


def test_ensure_shard_cached_is_a_no_op_when_already_cached(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    objects: dict[str, bytes] = {}
    objects.update(_seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", {"a": 1}))
    objects.update(_seed_bucket_with_shard(tmp_path, LOWLEVEL_DIR_NAME, "lowlevel", {"b": 2}))
    client = _fake_client(objects, monkeypatch)
    cache_dir = tmp_path / "cache"

    for _ in range(2):
        ensure_shard_cached(
            MBID, cache_dir, client, "bucket", tmp_path / "work", include_lowlevel=True
        )

    assert client.list_objects_v2.call_count == 2


def test_ensure_shard_cached_evicts_oldest_shard_past_the_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload: dict[str, object] = {"a": 1}
    other_mbid = "ffffffff-b294-4794-b275-1b064b31b3d5"
    objects: dict[str, bytes] = {}
    objects.update(_seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", payload))
    objects.update(_seed_bucket_with_shard(tmp_path, LOWLEVEL_DIR_NAME, "lowlevel", payload))
    objects.update(
        _seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", payload, mbid=other_mbid)
    )
    client = _fake_client(objects, monkeypatch)
    cache_dir = tmp_path / "cache"

    ensure_shard_cached(MBID, cache_dir, client, "bucket", tmp_path / "work", max_cached_shards=1)
    ensure_shard_cached(
        other_mbid, cache_dir, client, "bucket", tmp_path / "work", max_cached_shards=1
    )

    assert not (cache_dir / HIGHLEVEL_DIR_NAME / "highlevel" / SHARD).exists()
    assert (cache_dir / HIGHLEVEL_DIR_NAME / "highlevel" / other_mbid[:2]).exists()


def test_ensure_shard_cached_retries_transient_client_errors_then_succeeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    objects: dict[str, bytes] = {}
    objects.update(_seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", {"a": 1}))
    objects.update(_seed_bucket_with_shard(tmp_path, LOWLEVEL_DIR_NAME, "lowlevel", {"b": 2}))
    client = _fake_client(objects, monkeypatch)
    real_list_objects_v2 = client.list_objects_v2.side_effect
    call_count = 0

    def flaky_list_objects_v2(**kwargs: object) -> dict[str, object]:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ClientError({"Error": {"Code": "403", "Message": "Forbidden"}}, "ListObjectsV2")
        return real_list_objects_v2(**kwargs)

    client.list_objects_v2.side_effect = flaky_list_objects_v2
    cache_dir = tmp_path / "cache"
    sleeps: list[float] = []

    ensure_shard_cached(MBID, cache_dir, client, "bucket", tmp_path / "work", sleep=sleeps.append)

    filename = f"{MBID}-0.json"
    highlevel_file = cache_dir / HIGHLEVEL_DIR_NAME / "highlevel" / SHARD / SUBSHARD / filename
    assert json.loads(highlevel_file.read_text(encoding="utf-8")) == {"a": 1}
    assert sleeps == [2]


def test_ensure_shard_cached_reraises_after_exhausting_retries(tmp_path: Path) -> None:
    client = MagicMock()
    client.list_objects_v2.side_effect = ClientError(
        {"Error": {"Code": "403", "Message": "Forbidden"}}, "ListObjectsV2"
    )
    cache_dir = tmp_path / "cache"

    with pytest.raises(ClientError):
        ensure_shard_cached(
            MBID,
            cache_dir,
            client,
            "bucket",
            tmp_path / "work",
            attempts=2,
            sleep=lambda _seconds: None,
        )


def test_ensure_shard_cached_downloads_multiple_chunks_concurrently(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    objects: dict[str, bytes] = {}
    for i in range(6):
        mbid = f"{SHARD}{i}0000-0000-4000-8000-00000000000{i}"
        shard_source = tmp_path / f"chunk-source-{i}"
        (shard_source / mbid[2]).mkdir(parents=True)
        (shard_source / mbid[2] / f"{mbid}-0.json").write_text(
            json.dumps({"i": i}), encoding="utf-8"
        )
        chunk_path = tmp_path / f"chunk-{i}.tar.zst"
        pack_shard(shard_source, chunk_path)
        key = f"acousticbrainz/{HIGHLEVEL_DIR_NAME}/highlevel/{SHARD}/archive-{i}.tar.zst"
        objects[key] = chunk_path.read_bytes()

    client = _fake_client(objects, monkeypatch)
    cache_dir = tmp_path / "cache"

    ensure_shard_cached(MBID, cache_dir, client, "bucket", tmp_path / "work", max_workers=3)

    highlevel_dir = cache_dir / HIGHLEVEL_DIR_NAME / "highlevel" / SHARD
    unpacked = sorted(path.name for path in highlevel_dir.rglob("*.json"))
    assert unpacked == [f"{SHARD}{i}0000-0000-4000-8000-00000000000{i}-0.json" for i in range(6)]


def test_get_acousticbrainz_data_from_s3_returns_nulls_when_nothing_uploaded_yet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = _fake_client({}, monkeypatch)
    cache_dir = tmp_path / "cache"

    result = get_acousticbrainz_data_from_s3(MBID, cache_dir, client, "bucket", tmp_path / "work")

    assert result == {"highlevel": None, "lowlevel": None}


def test_get_acousticbrainz_data_from_s3_populates_cache_then_returns_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    objects: dict[str, bytes] = {}
    objects.update(_seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", {"a": 1}))
    client = _fake_client(objects, monkeypatch)
    cache_dir = tmp_path / "cache"

    result = get_acousticbrainz_data_from_s3(MBID, cache_dir, client, "bucket", tmp_path / "work")

    assert result["highlevel"] == {"a": 1}
    assert result["lowlevel"] is None


def test_get_acousticbrainz_data_from_s3_skips_download_when_shard_missing_and_disabled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    objects = _seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", {"a": 1})
    client = _fake_client(objects, monkeypatch)

    result = get_acousticbrainz_data_from_s3(
        MBID, tmp_path / "cache", client, "bucket", tmp_path / "work", download_missing=False
    )

    assert result == {"highlevel": None, "lowlevel": None}
    client.list_objects_v2.assert_not_called()


def test_ensure_shard_cached_downloads_only_highlevel_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    objects: dict[str, bytes] = {}
    objects.update(_seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", {"a": 1}))
    objects.update(_seed_bucket_with_shard(tmp_path, LOWLEVEL_DIR_NAME, "lowlevel", {"b": 2}))
    client = _fake_client(objects, monkeypatch)
    cache_dir = tmp_path / "cache"

    ensure_shard_cached(MBID, cache_dir, client, "bucket", tmp_path / "work")

    assert client.list_objects_v2.call_count == 1
    assert (cache_dir / HIGHLEVEL_DIR_NAME / "highlevel" / SHARD).is_dir()
    assert not (cache_dir / LOWLEVEL_DIR_NAME).exists()
