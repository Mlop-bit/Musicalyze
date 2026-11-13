from unittest.mock import MagicMock, patch

from ml.core.config import Settings
from ml.serving.feature_store.enrichment import save_acousticbrainz_enrichment


def _settings() -> Settings:
    return Settings.model_validate(
        {
            "s3_endpoint_url": "https://s3.example.com",
            "s3_region": "garage",
            "s3_bucket": "dev-bucket",
            "s3_access_key": "test-access-key",
            "s3_secret_key": "test-secret-key",
            "kv_account_id": "0" * 32,
            "kv_namespace_id": "1" * 32,
            "kv_api_token": "test-token",
            "db_host": "localhost",
            "db_port": 5432,
            "db_user": "musicalyze",
            "db_password": "musicalyze",
            "db_name": "musicalyze",
            "api_key": "test-api-key",
        }
    )


def test_saves_bpm_and_key_from_lowlevel_data_with_mood_left_null_without_highlevel_data() -> None:
    fake_session = MagicMock()
    fake_client = MagicMock()
    fake_data = {
        "highlevel": None,
        "lowlevel": {
            "rhythm": {"bpm": 128.4},
            "tonal": {"key_key": "C", "key_scale": "major", "chords_changes_rate": 0.42},
            "lowlevel": {"average_loudness": -6.5, "dynamic_complexity": 4.2},
        },
    }
    settings = _settings()

    with (
        patch("ml.serving.feature_store.enrichment.s3_client", return_value=fake_client),
        patch(
            "ml.serving.feature_store.enrichment.get_acousticbrainz_data_from_s3",
            return_value=fake_data,
        ) as mock_get_data,
        patch("ml.serving.feature_store.enrichment.save_enrichment") as mock_save_enrichment,
    ):
        save_acousticbrainz_enrichment(fake_session, "track-1", "mbid-1", settings)

    mock_get_data.assert_called_once_with(
        "mbid-1",
        settings.acousticbrainz_shard_cache_dir,
        fake_client,
        settings.s3_bucket,
        settings.acousticbrainz_shard_cache_dir / ".tmp",
        max_cached_shards=settings.acousticbrainz_max_cached_shards,
        download_missing=settings.acousticbrainz_download_missing_shards,
        include_lowlevel=settings.acousticbrainz_include_lowlevel,
    )
    mock_save_enrichment.assert_called_once_with(
        fake_session,
        "track-1",
        musicbrainz_id="mbid-1",
        bpm=128.4,
        key="C major",
        chords_changes_rate=0.42,
        danceability=None,
        average_loudness=-6.5,
        dynamic_complexity=4.2,
        voice_instrumental=None,
        mood_scores=None,
        mood_label=None,
        source="acousticbrainz",
    )


def test_saves_danceability_voice_and_mood_scores_from_highlevel_data() -> None:
    fake_session = MagicMock()
    fake_data = {
        "highlevel": {
            "highlevel": {
                "danceability": {"all": {"danceable": 0.81, "not_danceable": 0.19}},
                "voice_instrumental": {
                    "all": {"voice": 0.9, "instrumental": 0.1},
                    "value": "voice",
                },
                "mood_happy": {"all": {"happy": 0.75, "not_happy": 0.25}},
                "mood_party": {"all": {"party": 0.66, "not_party": 0.34}},
                "mood_sad": {"all": {"sad": 0.1, "not_sad": 0.9}},
            }
        },
        "lowlevel": None,
    }

    with (
        patch("ml.serving.feature_store.enrichment.s3_client", return_value=MagicMock()),
        patch(
            "ml.serving.feature_store.enrichment.get_acousticbrainz_data_from_s3",
            return_value=fake_data,
        ),
        patch("ml.serving.feature_store.enrichment.save_enrichment") as mock_save_enrichment,
    ):
        save_acousticbrainz_enrichment(fake_session, "track-1", "mbid-1", _settings())

    mock_save_enrichment.assert_called_once_with(
        fake_session,
        "track-1",
        musicbrainz_id="mbid-1",
        bpm=None,
        key=None,
        chords_changes_rate=None,
        danceability=0.81,
        average_loudness=None,
        dynamic_complexity=None,
        voice_instrumental="voice",
        mood_scores={"happy": 0.75, "party": 0.66, "sad": 0.1},
        mood_label="happy",
        source="acousticbrainz",
    )


def test_mood_label_is_left_null_when_no_mood_crosses_the_confidence_threshold() -> None:
    fake_session = MagicMock()
    fake_data = {
        "highlevel": {
            "highlevel": {
                "mood_happy": {"all": {"happy": 0.55, "not_happy": 0.45}},
                "mood_sad": {"all": {"sad": 0.45, "not_sad": 0.55}},
            }
        },
        "lowlevel": None,
    }

    with (
        patch("ml.serving.feature_store.enrichment.s3_client", return_value=MagicMock()),
        patch(
            "ml.serving.feature_store.enrichment.get_acousticbrainz_data_from_s3",
            return_value=fake_data,
        ),
        patch("ml.serving.feature_store.enrichment.save_enrichment") as mock_save_enrichment,
    ):
        save_acousticbrainz_enrichment(fake_session, "track-1", "mbid-1", _settings())

    assert mock_save_enrichment.call_args.kwargs["mood_scores"] == {"happy": 0.55, "sad": 0.45}
    assert mock_save_enrichment.call_args.kwargs["mood_label"] is None


def test_saves_nulls_when_track_has_no_lowlevel_or_highlevel_data() -> None:
    fake_session = MagicMock()
    fake_data = {"highlevel": None, "lowlevel": None}

    with (
        patch("ml.serving.feature_store.enrichment.s3_client", return_value=MagicMock()),
        patch(
            "ml.serving.feature_store.enrichment.get_acousticbrainz_data_from_s3",
            return_value=fake_data,
        ),
        patch("ml.serving.feature_store.enrichment.save_enrichment") as mock_save_enrichment,
    ):
        save_acousticbrainz_enrichment(fake_session, "track-1", "mbid-1", _settings())

    mock_save_enrichment.assert_called_once_with(
        fake_session,
        "track-1",
        musicbrainz_id="mbid-1",
        bpm=None,
        key=None,
        chords_changes_rate=None,
        danceability=None,
        average_loudness=None,
        dynamic_complexity=None,
        voice_instrumental=None,
        mood_scores=None,
        mood_label=None,
        source="acousticbrainz",
    )
