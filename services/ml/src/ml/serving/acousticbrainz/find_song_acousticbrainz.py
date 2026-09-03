import json
from pathlib import Path
from typing import Any, TypedDict

from ml.serving.acousticbrainz.constants import DUMP_VERSION

HIGHLEVEL_DIR_NAME = f"acousticbrainz-highlevel-json-{DUMP_VERSION}"
LOWLEVEL_DIR_NAME = f"acousticbrainz-lowlevel-json-{DUMP_VERSION}"


class AcousticBrainzData(TypedDict):
    highlevel: dict[str, Any] | None
    lowlevel: dict[str, Any] | None


class AcousticBrainzDumpNotExtractedError(Exception):
    pass


def _submission_file(dataset_dir: Path, mbid: str) -> Path | None:
    shard_dir = dataset_dir / mbid[:2] / mbid[2]
    if not shard_dir.is_dir():
        return None
    matches = sorted(shard_dir.glob(f"{mbid}-*.json"))
    return matches[0] if matches else None


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_acousticbrainz_data(mbid: str, extract_dir: Path) -> AcousticBrainzData:
    highlevel_dir = extract_dir / HIGHLEVEL_DIR_NAME / "highlevel"
    lowlevel_dir = extract_dir / LOWLEVEL_DIR_NAME / "lowlevel"

    if not highlevel_dir.is_dir() and not lowlevel_dir.is_dir():
        raise AcousticBrainzDumpNotExtractedError(
            f"neither {highlevel_dir} nor {lowlevel_dir} exist — "
            "run download_acousticbrainz.py before looking up tracks"
        )

    highlevel_file = _submission_file(highlevel_dir, mbid) if highlevel_dir.is_dir() else None
    lowlevel_file = _submission_file(lowlevel_dir, mbid) if lowlevel_dir.is_dir() else None

    return AcousticBrainzData(
        highlevel=_load_json(highlevel_file) if highlevel_file else None,
        lowlevel=_load_json(lowlevel_file) if lowlevel_file else None,
    )
