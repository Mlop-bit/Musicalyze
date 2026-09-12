from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.serving.feature_store.models import TrackFeatures
from ml.serving.feature_store.repository import (
    get_track_features,
    save_embedding,
    save_enrichment,
)

_TEST_TRACK_IDS = ["missing-track", "track-1", "track-2", "track-3"]


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
