import tarfile
from collections.abc import Iterator
from contextlib import ExitStack
from pathlib import Path
from typing import IO

import zstandard as zstd

S3_PREFIX = "acousticbrainz"
DEFAULT_ROTATION_BYTES = 16 * 1024 * 1024


def shard_prefix(dataset_dir_name: str, level: str, shard: str) -> str:
    return f"{S3_PREFIX}/{dataset_dir_name}/{level}/{shard}/"


def pack_shard(shard_dir: Path, chunk_path: Path) -> None:
    compressor = zstd.ZstdCompressor()
    with (
        chunk_path.open("wb") as compressed,
        compressor.stream_writer(compressed) as writer,
        tarfile.open(fileobj=writer, mode="w|") as tar,
    ):
        tar.add(shard_dir, arcname=".")


class _OpenShardChunk:
    def __init__(self, output_dir: Path, shard: str, part: int) -> None:
        self.path = output_dir / f"{shard}-{part}.tar.zst"
        self.raw_bytes = 0
        self._stack = ExitStack()
        file = self._stack.enter_context(self.path.open("wb"))
        writer = self._stack.enter_context(zstd.ZstdCompressor().stream_writer(file))
        self._tar = self._stack.enter_context(tarfile.open(fileobj=writer, mode="w|"))  # noqa: SIM115

    def add_member(self, member: tarfile.TarInfo, fileobj: IO[bytes]) -> None:
        arcname = "/".join(member.name.split("/")[3:])
        entry = tarfile.TarInfo(name=arcname)
        entry.size = member.size
        entry.mtime = member.mtime
        self._tar.addfile(entry, fileobj)
        self.raw_bytes += member.size

    def close(self) -> Path:
        self._stack.close()
        return self.path


def repack_archive_stream(
    source_tar: tarfile.TarFile,
    output_dir: Path,
    rotation_bytes: int = DEFAULT_ROTATION_BYTES,
) -> Iterator[tuple[str, Path]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    open_chunks: dict[str, _OpenShardChunk] = {}
    part_counters: dict[str, int] = {}

    for member in source_tar:
        if not member.isfile() or not member.name.endswith(".json"):
            continue
        parts = member.name.split("/")
        if len(parts) < 4:
            continue
        shard = parts[2]

        fileobj = source_tar.extractfile(member)
        if fileobj is None:
            continue

        chunk = open_chunks.get(shard)
        if chunk is None:
            part_counters[shard] = part_counters.get(shard, 0) + 1
            chunk = _OpenShardChunk(output_dir, shard, part_counters[shard])
            open_chunks[shard] = chunk

        chunk.add_member(member, fileobj)

        if chunk.raw_bytes >= rotation_bytes:
            del open_chunks[shard]
            yield shard, chunk.close()

    for shard, chunk in open_chunks.items():
        yield shard, chunk.close()


def unpack_shard(chunk_path: Path, destination_dir: Path) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    decompressor = zstd.ZstdDecompressor()
    with (
        chunk_path.open("rb") as compressed,
        decompressor.stream_reader(compressed) as reader,
        tarfile.open(fileobj=reader, mode="r|") as tar,
    ):
        tar.extractall(path=destination_dir, filter="data")
