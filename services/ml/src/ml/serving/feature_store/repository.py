from sqlalchemy import case, func, literal, update
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.orm import Session

from ml.serving.feature_store.models import TrackFeatures

CLASSIFIER_SOURCE = "classifier"


def get_track_features(session: Session, track_id: str) -> TrackFeatures | None:
    return session.get(TrackFeatures, track_id)


def save_embedding(
    session: Session, track_id: str, embedding: list[float], duration_sec: int | None = None
) -> None:
    statement = (
        insert(TrackFeatures)
        .values(track_id=track_id, embedding=embedding, duration_sec=duration_sec)
        .on_conflict_do_nothing(index_elements=[TrackFeatures.track_id])
    )
    session.execute(statement)


def save_enrichment(
    session: Session,
    track_id: str,
    musicbrainz_id: str | None,
    bpm: float | None,
    key: str | None,
    chords_changes_rate: float | None,
    danceability: float | None,
    average_loudness: float | None,
    dynamic_complexity: float | None,
    voice_instrumental: str | None,
    mood_scores: dict[str, float] | None,
    mood_label: str | None,
    source: str,
) -> None:
    statement = (
        update(TrackFeatures)
        .where(TrackFeatures.track_id == track_id)
        .values(
            musicbrainz_id=musicbrainz_id,
            bpm=bpm,
            key=key,
            chords_changes_rate=chords_changes_rate,
            danceability=danceability,
            average_loudness=average_loudness,
            dynamic_complexity=dynamic_complexity,
            voice_instrumental=voice_instrumental,
            mood_scores=mood_scores,
            mood_label=mood_label,
            source=source,
        )
    )
    session.execute(statement)


def save_classifier_mood(
    session: Session, track_id: str, mood_scores: dict[str, float], mood_label: str
) -> None:
    statement = (
        update(TrackFeatures)
        .where(TrackFeatures.track_id == track_id, TrackFeatures.mood_label.is_(None))
        .values(
            mood_scores=case(
                (
                    func.jsonb_typeof(TrackFeatures.mood_scores) == "object",
                    TrackFeatures.mood_scores,
                ),
                else_=literal(mood_scores, type_=JSONB),
            ),
            mood_label=mood_label,
            source=func.coalesce(TrackFeatures.source, CLASSIFIER_SOURCE),
        )
    )
    session.execute(statement)


def save_tag_scores(session: Session, track_id: str, tag_scores: dict[str, float]) -> None:
    statement = (
        update(TrackFeatures)
        .where(TrackFeatures.track_id == track_id, TrackFeatures.tag_scores.is_(None))
        .values(tag_scores=tag_scores)
    )
    session.execute(statement)
