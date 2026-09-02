from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from ml.serving.feature_store.models import TrackFeatures


def get_track_features(session: Session, track_id: str) -> TrackFeatures | None:
    return session.get(TrackFeatures, track_id)


def save_embedding(session: Session, track_id: str, embedding: list[float]) -> None:
    statement = (
        insert(TrackFeatures)
        .values(track_id=track_id, embedding=embedding)
        .on_conflict_do_nothing(index_elements=[TrackFeatures.track_id])
    )
    session.execute(statement)


def save_enrichment(
    session: Session,
    track_id: str,
    musicbrainz_id: str | None,
    bpm: float | None,
    key: str | None,
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
            mood_label=mood_label,
            source=source,
        )
    )
    session.execute(statement)
