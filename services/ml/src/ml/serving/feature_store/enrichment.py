from typing import Any

from sqlalchemy.orm import Session

from ml.core.artifact_store import s3_client
from ml.core.config import Settings
from ml.serving.acousticbrainz.s3_lookup import get_acousticbrainz_data_from_s3
from ml.serving.feature_store.repository import save_enrichment

SOURCE = "acousticbrainz"

MOOD_NAMES = ("acoustic", "aggressive", "electronic", "happy", "party", "relaxed", "sad")
MOOD_LABEL_CONFIDENCE_THRESHOLD = 0.6


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


def _chords_changes_rate(lowlevel: dict[str, Any] | None) -> float | None:
    if lowlevel is None:
        return None
    rate = lowlevel.get("tonal", {}).get("chords_changes_rate")
    return float(rate) if rate is not None else None


def _average_loudness(lowlevel: dict[str, Any] | None) -> float | None:
    if lowlevel is None:
        return None
    value = lowlevel.get("lowlevel", {}).get("average_loudness")
    return float(value) if value is not None else None


def _dynamic_complexity(lowlevel: dict[str, Any] | None) -> float | None:
    if lowlevel is None:
        return None
    value = lowlevel.get("lowlevel", {}).get("dynamic_complexity")
    return float(value) if value is not None else None


def _danceability(highlevel: dict[str, Any] | None) -> float | None:
    if highlevel is None:
        return None
    value = highlevel.get("highlevel", {}).get("danceability", {}).get("all", {}).get("danceable")
    return float(value) if value is not None else None


def _voice_instrumental(highlevel: dict[str, Any] | None) -> str | None:
    if highlevel is None:
        return None
    return highlevel.get("highlevel", {}).get("voice_instrumental", {}).get("value")


def _mood_scores(highlevel: dict[str, Any] | None) -> dict[str, float] | None:
    if highlevel is None:
        return None
    classifiers = highlevel.get("highlevel", {})
    scores: dict[str, float] = {}
    for mood in MOOD_NAMES:
        probability = classifiers.get(f"mood_{mood}", {}).get("all", {}).get(mood)
        if probability is not None:
            scores[mood] = float(probability)
    return scores or None


def _mood_label(mood_scores: dict[str, float] | None) -> str | None:
    if not mood_scores:
        return None
    dominant_mood, probability = max(mood_scores.items(), key=lambda item: item[1])
    return dominant_mood if probability >= MOOD_LABEL_CONFIDENCE_THRESHOLD else None


def save_acousticbrainz_enrichment(
    session: Session, track_id: str, musicbrainz_id: str, settings: Settings
) -> None:
    cache_dir = settings.acousticbrainz_shard_cache_dir
    data = get_acousticbrainz_data_from_s3(
        musicbrainz_id,
        cache_dir,
        s3_client(settings),
        settings.s3_bucket,
        cache_dir / ".tmp",
        max_cached_shards=settings.acousticbrainz_max_cached_shards,
        download_missing=settings.acousticbrainz_download_missing_shards,
        include_lowlevel=settings.acousticbrainz_include_lowlevel,
    )
    mood_scores = _mood_scores(data["highlevel"])

    save_enrichment(
        session,
        track_id,
        musicbrainz_id=musicbrainz_id,
        bpm=_bpm(data["lowlevel"]),
        key=_key(data["lowlevel"]),
        chords_changes_rate=_chords_changes_rate(data["lowlevel"]),
        danceability=_danceability(data["highlevel"]),
        average_loudness=_average_loudness(data["lowlevel"]),
        dynamic_complexity=_dynamic_complexity(data["lowlevel"]),
        voice_instrumental=_voice_instrumental(data["highlevel"]),
        mood_scores=mood_scores,
        mood_label=_mood_label(mood_scores),
        source=SOURCE,
    )
