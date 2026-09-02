import json
from pathlib import Path

import pytest

from ml.serving.acousticbrainz.constants import DUMP_VERSION
from ml.serving.acousticbrainz.find_song_acousticbrainz import (
    AcousticBrainzDumpNotExtractedError,
    get_acousticbrainz_data,
)

MBID = "1a0a0ac2-b294-4794-b275-1b064b31b3d5"


def _shard_dir(extract_dir: Path, dataset: str, level: str) -> Path:
    return extract_dir / f"acousticbrainz-{dataset}-{DUMP_VERSION}" / level / MBID[:2] / MBID[2]


def _write_submission(
    extract_dir: Path, dataset: str, level: str, index: int, payload: dict[str, object]
) -> None:
    shard_dir = _shard_dir(extract_dir, dataset, level)
    shard_dir.mkdir(parents=True, exist_ok=True)
    (shard_dir / f"{MBID}-{index}.json").write_text(json.dumps(payload), encoding="utf-8")


def test_returns_data_for_first_submission(tmp_path: Path) -> None:
    _write_submission(tmp_path, "highlevel-json", "highlevel", 0, {"highlevel": "hl"})
    _write_submission(tmp_path, "lowlevel-features", "lowlevel", 0, {"lowlevel": "ll"})

    result = get_acousticbrainz_data(MBID, tmp_path)

    assert result["highlevel"] == {"highlevel": "hl"}
    assert result["lowlevel"] == {"lowlevel": "ll"}


def test_falls_back_to_lowest_available_submission_when_zero_is_missing(tmp_path: Path) -> None:
    _write_submission(tmp_path, "highlevel-json", "highlevel", 1, {"highlevel": "hl-1"})

    result = get_acousticbrainz_data(MBID, tmp_path)

    assert result["highlevel"] == {"highlevel": "hl-1"}


def test_returns_none_for_dataset_missing_this_mbid(tmp_path: Path) -> None:
    _write_submission(tmp_path, "highlevel-json", "highlevel", 0, {"highlevel": "hl"})
    (tmp_path / f"acousticbrainz-lowlevel-features-{DUMP_VERSION}" / "lowlevel").mkdir(parents=True)

    result = get_acousticbrainz_data(MBID, tmp_path)

    assert result["highlevel"] == {"highlevel": "hl"}
    assert result["lowlevel"] is None


def test_raises_when_dump_was_never_extracted(tmp_path: Path) -> None:
    with pytest.raises(AcousticBrainzDumpNotExtractedError):
        get_acousticbrainz_data(MBID, tmp_path)


def test_propagates_error_for_corrupt_submission_file(tmp_path: Path) -> None:
    shard_dir = _shard_dir(tmp_path, "highlevel-json", "highlevel")
    shard_dir.mkdir(parents=True)
    (shard_dir / f"{MBID}-0.json").write_text("not valid json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        get_acousticbrainz_data(MBID, tmp_path)
