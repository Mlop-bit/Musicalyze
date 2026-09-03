import json
from pathlib import Path
from unittest.mock import MagicMock

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


def _fake_client(objects_by_key: dict[str, bytes]) -> MagicMock:
    client = MagicMock()

    def list_objects_v2(Bucket: str, Prefix: str) -> dict[str, object]:  # noqa: N803
        return {"Contents": [{"Key": key} for key in objects_by_key if key.startswith(Prefix)]}

    def download_file(Bucket: str, Key: str, local_path: str) -> None:  # noqa: N803
        Path(local_path).write_bytes(objects_by_key[Key])

    client.list_objects_v2.side_effect = list_objects_v2
    client.download_file.side_effect = download_file
    return client


def test_ensure_shard_cached_downloads_and_unpacks_both_datasets(tmp_path: Path) -> None:
    objects: dict[str, bytes] = {}
    objects.update(_seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", {"a": 1}))
    objects.update(_seed_bucket_with_shard(tmp_path, LOWLEVEL_DIR_NAME, "lowlevel", {"b": 2}))
    client = _fake_client(objects)
    cache_dir = tmp_path / "cache"

    ensure_shard_cached(MBID, cache_dir, client, "bucket", tmp_path / "work")

    filename = f"{MBID}-0.json"
    highlevel_file = cache_dir / HIGHLEVEL_DIR_NAME / "highlevel" / SHARD / SUBSHARD / filename
    lowlevel_file = cache_dir / LOWLEVEL_DIR_NAME / "lowlevel" / SHARD / SUBSHARD / filename
    assert json.loads(highlevel_file.read_text(encoding="utf-8")) == {"a": 1}
    assert json.loads(lowlevel_file.read_text(encoding="utf-8")) == {"b": 2}


def test_ensure_shard_cached_is_a_no_op_when_already_cached(tmp_path: Path) -> None:
    objects: dict[str, bytes] = {}
    objects.update(_seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", {"a": 1}))
    objects.update(_seed_bucket_with_shard(tmp_path, LOWLEVEL_DIR_NAME, "lowlevel", {"b": 2}))
    client = _fake_client(objects)
    cache_dir = tmp_path / "cache"

    ensure_shard_cached(MBID, cache_dir, client, "bucket", tmp_path / "work")
    ensure_shard_cached(MBID, cache_dir, client, "bucket", tmp_path / "work")

    assert client.list_objects_v2.call_count == 2


def test_ensure_shard_cached_evicts_oldest_shard_past_the_limit(tmp_path: Path) -> None:
    payload: dict[str, object] = {"a": 1}
    other_mbid = "ffffffff-b294-4794-b275-1b064b31b3d5"
    objects: dict[str, bytes] = {}
    objects.update(_seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", payload))
    objects.update(_seed_bucket_with_shard(tmp_path, LOWLEVEL_DIR_NAME, "lowlevel", payload))
    objects.update(
        _seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", payload, mbid=other_mbid)
    )
    client = _fake_client(objects)
    cache_dir = tmp_path / "cache"

    ensure_shard_cached(MBID, cache_dir, client, "bucket", tmp_path / "work", max_cached_shards=1)
    ensure_shard_cached(
        other_mbid, cache_dir, client, "bucket", tmp_path / "work", max_cached_shards=1
    )

    assert not (cache_dir / HIGHLEVEL_DIR_NAME / "highlevel" / SHARD).exists()
    assert (cache_dir / HIGHLEVEL_DIR_NAME / "highlevel" / other_mbid[:2]).exists()


def test_get_acousticbrainz_data_from_s3_returns_nulls_when_nothing_uploaded_yet(
    tmp_path: Path,
) -> None:
    client = _fake_client({})
    cache_dir = tmp_path / "cache"

    result = get_acousticbrainz_data_from_s3(MBID, cache_dir, client, "bucket", tmp_path / "work")

    assert result == {"highlevel": None, "lowlevel": None}


def test_get_acousticbrainz_data_from_s3_populates_cache_then_returns_data(tmp_path: Path) -> None:
    objects: dict[str, bytes] = {}
    objects.update(_seed_bucket_with_shard(tmp_path, HIGHLEVEL_DIR_NAME, "highlevel", {"a": 1}))
    client = _fake_client(objects)
    cache_dir = tmp_path / "cache"

    result = get_acousticbrainz_data_from_s3(MBID, cache_dir, client, "bucket", tmp_path / "work")

    assert result["highlevel"] == {"a": 1}
    assert result["lowlevel"] is None
