from sqlalchemy import case, func, literal, or_, select, text, update
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.orm import Session

from ml.serving.feature_store.models import TrackFeatures
from ml.serving.playlist.recommend import Recommendation, merge_best_matches

CLASSIFIER_SOURCE = "classifier"
TAG_SCORE_THRESHOLD = 0.3


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
            bpm=func.coalesce(literal(bpm), TrackFeatures.bpm),
            key=func.coalesce(literal(key), TrackFeatures.key),
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


def save_audio_estimates(
    session: Session, track_id: str, bpm: float | None, key: str | None
) -> None:
    statement = (
        update(TrackFeatures)
        .where(TrackFeatures.track_id == track_id)
        .values(
            bpm=func.coalesce(TrackFeatures.bpm, literal(bpm)),
            key=func.coalesce(TrackFeatures.key, literal(key)),
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


def nearest_tracks(
    session: Session,
    seeds: list[list[float]],
    exclude_ids: list[str],
    tags: list[str] | None,
    limit: int,
    tag_threshold: float = TAG_SCORE_THRESHOLD,
) -> list[Recommendation]:
    session.execute(text("SET LOCAL hnsw.iterative_scan = relaxed_order"))
    matches_per_seed = [
        _nearest_to_seed(session, seed, exclude_ids, tags, limit, tag_threshold) for seed in seeds
    ]
    return merge_best_matches(matches_per_seed, limit)


def _nearest_to_seed(
    session: Session,
    seed: list[float],
    exclude_ids: list[str],
    tags: list[str] | None,
    limit: int,
    tag_threshold: float,
) -> list[Recommendation]:
    distance = TrackFeatures.embedding.cosine_distance(seed)
    statement = select(TrackFeatures.track_id, distance.label("distance")).order_by(distance)
    if exclude_ids:
        statement = statement.where(TrackFeatures.track_id.not_in(exclude_ids))
    if tags:
        statement = statement.where(
            or_(*[TrackFeatures.tag_scores[tag].as_float() >= tag_threshold for tag in tags])
        )
    rows = session.execute(statement.limit(limit)).all()
    return [Recommendation(track_id=row.track_id, similarity=1.0 - row.distance) for row in rows]
