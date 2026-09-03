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
        }
    )


def test_saves_bpm_and_key_from_lowlevel_data_with_mood_left_null() -> None:
    fake_session = MagicMock()
    fake_client = MagicMock()
    fake_data = {
        "highlevel": None,
        "lowlevel": {
            "rhythm": {"bpm": 128.4},
            "tonal": {"key_key": "C", "key_scale": "major"},
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
    )
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
        mood_label=None,
        source="acousticbrainz",
    )
