from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from ml.serving.acousticbrainz.find_song_acousticbrainz import get_acousticbrainz_data
from ml.serving.feature_store.repository import save_enrichment

SOURCE = "acousticbrainz"


def _bpm(lowlevel: dict[str, Any] | None) -> float | None:
    if lowlevel is None:
        return None
    bpm = lowlevel.get("rhythm", {}).get("bpm")
    return float(bpm) if bpm is not None else None


def _key(lowlevel: dict[str, Any] | None) -> str | None:
    if lowlevel is None:
        return None
    tonal = lowlevel.get("tonal", {})
    key_key = tonal.get("key_key")
    key_scale = tonal.get("key_scale")
    return f"{key_key} {key_scale}" if key_key and key_scale else None


def save_acousticbrainz_enrichment(
    session: Session, track_id: str, musicbrainz_id: str, extract_dir: Path
) -> None:
    data = get_acousticbrainz_data(musicbrainz_id, extract_dir)

    save_enrichment(
        session,
        track_id,
        musicbrainz_id=musicbrainz_id,
        bpm=_bpm(data["lowlevel"]),
        key=_key(data["lowlevel"]),
        mood_label=None,
        source=SOURCE,
    )
