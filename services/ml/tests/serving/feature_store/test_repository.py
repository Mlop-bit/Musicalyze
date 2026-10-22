from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.serving.feature_store.models import TrackFeatures
from ml.serving.feature_store.repository import (
    get_track_features,
    nearest_tracks,
    save_embedding,
    save_enrichment,
    save_tag_scores,
)

_TEST_TRACK_IDS = [
    "missing-track",
    "track-1",
    "track-2",
    "track-3",
    "track-4",
    "rec-a",
    "rec-b",
    "rec-c",
]


@pytest.fixture
def session() -> Iterator[Session]:
    settings = Settings.model_validate({})
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        yield session
        session.rollback()
        session.execute(delete(TrackFeatures).where(TrackFeatures.track_id.in_(_TEST_TRACK_IDS)))
        session.commit()
    engine.dispose()


@pytest.mark.live
def test_get_track_features_returns_none_when_absent(session: Session) -> None:
    assert get_track_features(session, "missing-track") is None


@pytest.mark.live
def test_save_embedding_then_get_returns_the_row(session: Session) -> None:
    save_embedding(session, "track-1", [0.1] * 1024, duration_sec=245)
    session.commit()

    result = get_track_features(session, "track-1")

    assert result is not None
    assert result.track_id == "track-1"
    assert result.duration_sec == 245
    assert result.mood_label is None


@pytest.mark.live
def test_save_embedding_twice_does_not_raise_or_duplicate(session: Session) -> None:
    save_embedding(session, "track-2", [0.1] * 1024)
    session.commit()
    save_embedding(session, "track-2", [0.2] * 1024)
    session.commit()

    result = get_track_features(session, "track-2")

    assert result is not None


@pytest.mark.live
def test_save_enrichment_backfills_fields_without_losing_the_embedding(session: Session) -> None:
    save_embedding(session, "track-3", [0.5] * 1024)
    session.commit()

    save_enrichment(
        session,
        "track-3",
        musicbrainz_id="mbid-123",
        bpm=128.0,
        key="C major",
        chords_changes_rate=0.3,
        danceability=0.8,
        average_loudness=-6.5,
        dynamic_complexity=4.2,
        voice_instrumental="voice",
        mood_scores={"happy": 0.7, "party": 0.6},
        mood_label="energetic",
        source="acousticbrainz",
    )
    session.commit()
    session.expire_all()

    result = get_track_features(session, "track-3")

    assert result is not None
    assert result.musicbrainz_id == "mbid-123"
    assert result.bpm == 128.0
    assert result.key == "C major"
    assert result.chords_changes_rate == 0.3
    assert result.danceability == 0.8
    assert result.average_loudness == -6.5
    assert result.dynamic_complexity == 4.2
    assert result.voice_instrumental == "voice"
    assert result.mood_scores == {"happy": 0.7, "party": 0.6}
    assert result.mood_label == "energetic"
    assert result.source == "acousticbrainz"
    assert result.embedding is not None


@pytest.mark.live
def test_save_tag_scores_only_fills_a_null_column(session: Session) -> None:
    save_embedding(session, "track-4", [0.5] * 1024)
    session.commit()

    save_tag_scores(session, "track-4", {"calm": 0.9, "dark": 0.1})
    session.commit()
    save_tag_scores(session, "track-4", {"calm": 0.0, "dark": 1.0})
    session.commit()
    session.expire_all()

    result = get_track_features(session, "track-4")

    assert result is not None
    assert result.tag_scores == {"calm": 0.9, "dark": 0.1}


_AXIS = 1000


def _unit(*weights: tuple[int, float]) -> list[float]:
    vector = [0.0] * 1024
    for index, weight in weights:
        vector[index] = weight
    norm = sum(value * value for value in vector) ** 0.5
    return [value / norm for value in vector]


def _store_recommendation_rows(session: Session) -> list[float]:
    save_embedding(session, "rec-a", _unit((_AXIS, 1.0)))
    save_embedding(session, "rec-b", _unit((_AXIS, 1.0), (_AXIS + 1, 0.5)))
    save_embedding(session, "rec-c", _unit((_AXIS + 1, 1.0)))
    save_tag_scores(session, "rec-a", {"calm": 0.9})
    save_tag_scores(session, "rec-b", {"calm": 0.2})
    session.commit()
    return _unit((_AXIS, 1.0))


@pytest.mark.live
def test_nearest_tracks_orders_by_similarity(session: Session) -> None:
    centroid = _store_recommendation_rows(session)

    result = nearest_tracks(session, [centroid], exclude_ids=[], tags=None, limit=2)

    assert [item.track_id for item in result] == ["rec-a", "rec-b"]
    assert result[0].similarity == pytest.approx(1.0)
    assert result[0].similarity > result[1].similarity


@pytest.mark.live
def test_nearest_tracks_excludes_the_seeds(session: Session) -> None:
    centroid = _store_recommendation_rows(session)

    result = nearest_tracks(session, [centroid], exclude_ids=["rec-a"], tags=None, limit=1)

    assert [item.track_id for item in result] == ["rec-b"]


@pytest.mark.live
def test_nearest_tracks_filters_by_tag(session: Session) -> None:
    centroid = _store_recommendation_rows(session)

    result = nearest_tracks(session, [centroid], exclude_ids=[], tags=["calm"], limit=1000)
    ids = [item.track_id for item in result]

    assert ids[0] == "rec-a"
    assert "rec-b" not in ids
    assert "rec-c" not in ids


@pytest.mark.live
def test_nearest_tracks_respects_the_limit(session: Session) -> None:
    centroid = _store_recommendation_rows(session)

    assert len(nearest_tracks(session, [centroid], exclude_ids=[], tags=None, limit=1)) == 1


@pytest.mark.live
def test_nearest_tracks_without_tag_filter_keeps_rows_without_tag_scores(session: Session) -> None:
    centroid = _store_recommendation_rows(session)

    result = nearest_tracks(session, [centroid], exclude_ids=[], tags=None, limit=1000)

    assert "rec-c" in [item.track_id for item in result]


@pytest.mark.live
def test_nearest_tracks_ranks_by_the_closest_seed(session: Session) -> None:
    first = _store_recommendation_rows(session)
    second = _unit((_AXIS + 1, 1.0))

    result = nearest_tracks(session, [first, second], exclude_ids=[], tags=None, limit=1000)
    similarity = {item.track_id: item.similarity for item in result}

    assert similarity["rec-a"] == pytest.approx(1.0)
    assert similarity["rec-c"] == pytest.approx(1.0)
    assert similarity["rec-b"] > 0.85
