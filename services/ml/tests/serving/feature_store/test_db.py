from unittest.mock import MagicMock, patch

from ml.core.config import Settings
from ml.serving.feature_store.db import session_scope


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


def test_session_scope_creates_engine_from_settings_and_disposes_it() -> None:
    fake_engine = MagicMock()

    with (
        patch(
            "ml.serving.feature_store.db.create_engine", return_value=fake_engine
        ) as mock_create_engine,
        patch("ml.serving.feature_store.db.Session") as mock_session_cls,
    ):
        mock_session_cls.return_value.__enter__.return_value = MagicMock()

        with session_scope(_settings()) as session:
            assert session is mock_session_cls.return_value.__enter__.return_value

    mock_create_engine.assert_called_once_with(_settings().database_url)
    fake_engine.dispose.assert_called_once()


def test_session_scope_disposes_engine_even_if_the_body_raises() -> None:
    fake_engine = MagicMock()

    with (
        patch("ml.serving.feature_store.db.create_engine", return_value=fake_engine),
        patch("ml.serving.feature_store.db.Session") as mock_session_cls,
    ):
        mock_session_cls.return_value.__enter__.return_value = MagicMock()

        try:
            with session_scope(_settings()):
                raise ValueError("boom")
        except ValueError:
            pass

    fake_engine.dispose.assert_called_once()
