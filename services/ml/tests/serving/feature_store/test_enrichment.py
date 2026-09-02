from pathlib import Path
from unittest.mock import MagicMock, patch

from ml.serving.feature_store.enrichment import save_acousticbrainz_enrichment


def test_saves_bpm_and_key_from_lowlevel_data_with_mood_left_null() -> None:
    fake_session = MagicMock()
    fake_data = {
        "highlevel": None,
        "lowlevel": {
            "rhythm": {"bpm": 128.4},
            "tonal": {"key_key": "C", "key_scale": "major"},
        },
    }

    with (
        patch(
            "ml.serving.feature_store.enrichment.get_acousticbrainz_data", return_value=fake_data
        ),
        patch("ml.serving.feature_store.enrichment.save_enrichment") as mock_save_enrichment,
    ):
        save_acousticbrainz_enrichment(fake_session, "track-1", "mbid-1", Path("extracted"))

    mock_save_enrichment.assert_called_once_with(
        fake_session,
        "track-1",
        musicbrainz_id="mbid-1",
        bpm=128.4,
        key="C major",
        mood_label=None,
        source="acousticbrainz",
    )


def test_saves_nulls_when_track_has_no_lowlevel_data() -> None:
    fake_session = MagicMock()
    fake_data = {"highlevel": None, "lowlevel": None}

    with (
        patch(
            "ml.serving.feature_store.enrichment.get_acousticbrainz_data", return_value=fake_data
        ),
        patch("ml.serving.feature_store.enrichment.save_enrichment") as mock_save_enrichment,
    ):
        save_acousticbrainz_enrichment(fake_session, "track-1", "mbid-1", Path("extracted"))

    mock_save_enrichment.assert_called_once_with(
        fake_session,
        "track-1",
        musicbrainz_id="mbid-1",
        bpm=None,
        key=None,
        mood_label=None,
        source="acousticbrainz",
    )
