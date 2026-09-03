import io
import tarfile
from pathlib import Path

from ml.serving.acousticbrainz.s3_shards import pack_shard, shard_prefix, unpack_shard


def test_pack_and_unpack_shard_round_trips_nested_files(tmp_path: Path) -> None:
    shard_dir = tmp_path / "00"
    nested_dir = shard_dir / "0"
    nested_dir.mkdir(parents=True)
    (nested_dir / "1a0a0ac2-0.json").write_text('{"a": 1}', encoding="utf-8")

    chunk_path = tmp_path / "chunk.tar.zst"
    pack_shard(shard_dir, chunk_path)

    destination_dir = tmp_path / "restored"
    unpack_shard(chunk_path, destination_dir)

    restored_file = destination_dir / "0" / "1a0a0ac2-0.json"
    assert restored_file.read_text(encoding="utf-8") == '{"a": 1}'


def test_unpack_shard_merges_into_existing_destination_without_deleting_other_files(
    tmp_path: Path,
) -> None:
    first_shard = tmp_path / "first"
    (first_shard / "0").mkdir(parents=True)
    (first_shard / "0" / "aaa-0.json").write_text("{}", encoding="utf-8")
    first_chunk = tmp_path / "first.tar.zst"
    pack_shard(first_shard, first_chunk)

    second_shard = tmp_path / "second"
    (second_shard / "0").mkdir(parents=True)
    (second_shard / "0" / "bbb-0.json").write_text("{}", encoding="utf-8")
    second_chunk = tmp_path / "second.tar.zst"
    pack_shard(second_shard, second_chunk)

    destination_dir = tmp_path / "restored"
    unpack_shard(first_chunk, destination_dir)
    unpack_shard(second_chunk, destination_dir)

    assert (destination_dir / "0" / "aaa-0.json").exists()
    assert (destination_dir / "0" / "bbb-0.json").exists()


def test_shard_prefix_builds_prefixed_path() -> None:
    prefix = shard_prefix(
        dataset_dir_name="acousticbrainz-highlevel-json-20220623",
        level="highlevel",
        shard="00",
    )

    assert prefix == "acousticbrainz/acousticbrainz-highlevel-json-20220623/highlevel/00/"


def _make_source_tar(tmp_path: Path, entries: list[tuple[str, bytes]]) -> tarfile.TarFile:
    archive_path = tmp_path / "source.tar"
    with tarfile.open(archive_path, mode="w") as tar:
        for name, content in entries:
            info = tarfile.TarInfo(name=name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))

    return tarfile.open(archive_path, mode="r|")


def test_repack_archive_stream_groups_members_by_shard_and_strips_prefix(tmp_path: Path) -> None:
    source_tar = _make_source_tar(
        tmp_path,
        [
            ("acousticbrainz-highlevel-json-20220623/highlevel/00/1/aaa-0.json", b'{"a": 1}'),
            ("acousticbrainz-highlevel-json-20220623/highlevel/02/3/ccc-0.json", b'{"c": 3}'),
        ],
    )
    output_dir = tmp_path / "chunks"

    from ml.serving.acousticbrainz.s3_shards import repack_archive_stream

    chunks = list(repack_archive_stream(source_tar, output_dir, rotation_bytes=10_000_000))
    source_tar.close()

    assert {shard for shard, _ in chunks} == {"00", "02"}

    restored = tmp_path / "restored"
    for shard, chunk_path in chunks:
        unpack_shard(chunk_path, restored / shard)

    assert (restored / "00" / "1" / "aaa-0.json").read_text(encoding="utf-8") == '{"a": 1}'
    assert (restored / "02" / "3" / "ccc-0.json").read_text(encoding="utf-8") == '{"c": 3}'


def test_repack_archive_stream_rotates_shard_into_multiple_chunks_past_threshold(
    tmp_path: Path,
) -> None:
    source_tar = _make_source_tar(
        tmp_path,
        [
            ("acousticbrainz-highlevel-json-20220623/highlevel/00/1/aaa-0.json", b"x" * 100),
            ("acousticbrainz-highlevel-json-20220623/highlevel/00/1/bbb-0.json", b"y" * 100),
        ],
    )
    output_dir = tmp_path / "chunks"

    from ml.serving.acousticbrainz.s3_shards import repack_archive_stream

    chunks = list(repack_archive_stream(source_tar, output_dir, rotation_bytes=50))
    source_tar.close()

    shard_00_chunks = [path for shard, path in chunks if shard == "00"]
    assert len(shard_00_chunks) == 2


def test_repack_archive_stream_skips_non_json_and_shallow_entries(tmp_path: Path) -> None:
    source_tar = _make_source_tar(
        tmp_path,
        [
            ("acousticbrainz-highlevel-json-20220623/COPYING", b"license text"),
            ("acousticbrainz-highlevel-json-20220623/highlevel/00/1/aaa-0.json", b'{"a": 1}'),
        ],
    )
    output_dir = tmp_path / "chunks"

    from ml.serving.acousticbrainz.s3_shards import repack_archive_stream

    chunks = list(repack_archive_stream(source_tar, output_dir, rotation_bytes=10_000_000))
    source_tar.close()

    assert len(chunks) == 1
    assert chunks[0][0] == "00"
