from pathlib import Path
from unittest.mock import MagicMock, patch

from ml.core.artifact_store import download_model, upload_model
from ml.core.config import Settings


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


def test_upload_model_calls_upload_file_with_local_path_bucket_and_key() -> None:
    fake_client = MagicMock()

    with patch("ml.core.artifact_store.boto3.client", return_value=fake_client):
        upload_model(Path("model.pt"), "runs/model.pt", _settings())

    fake_client.upload_file.assert_called_once_with("model.pt", "dev-bucket", "runs/model.pt")


def test_download_model_calls_download_file_with_bucket_key_and_local_path() -> None:
    fake_client = MagicMock()

    with patch("ml.core.artifact_store.boto3.client", return_value=fake_client):
        download_model("runs/model.pt", Path("model.pt"), _settings())

    fake_client.download_file.assert_called_once_with("dev-bucket", "runs/model.pt", "model.pt")


def test_client_uses_path_style_addressing_and_settings_credentials() -> None:
    fake_client = MagicMock()

    with patch("ml.core.artifact_store.boto3.client", return_value=fake_client) as mock_client:
        upload_model(Path("model.pt"), "runs/model.pt", _settings())

    _, kwargs = mock_client.call_args
    assert kwargs["endpoint_url"] == "https://s3.example.com/"
    assert kwargs["region_name"] == "garage"
    assert kwargs["aws_access_key_id"] == "test-access-key"
    assert kwargs["aws_secret_access_key"] == "test-secret-key"
    assert kwargs["config"].s3["addressing_style"] == "path"
