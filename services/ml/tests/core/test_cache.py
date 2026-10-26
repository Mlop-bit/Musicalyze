from unittest.mock import MagicMock, patch

from ml.core.cache import get_cached_value, set_cached_value
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
            "api_key": "test-api-key",
        }
    )


def test_get_cached_value_returns_body_when_key_exists() -> None:
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.text = "cached value"

    with patch("ml.core.cache.httpx.get", return_value=fake_response) as mock_get:
        result = get_cached_value("some-key", _settings())

    assert result == "cached value"
    mock_get.assert_called_once_with(
        f"https://api.cloudflare.com/client/v4/accounts/{'0' * 32}"
        f"/storage/kv/namespaces/{'1' * 32}/values/some-key",
        headers={"Authorization": "Bearer test-token"},
    )


def test_get_cached_value_returns_none_when_key_missing() -> None:
    fake_response = MagicMock()
    fake_response.status_code = 404

    with patch("ml.core.cache.httpx.get", return_value=fake_response):
        result = get_cached_value("missing-key", _settings())

    assert result is None


def test_set_cached_value_puts_value_with_correct_url_and_auth() -> None:
    fake_response = MagicMock()
    fake_response.status_code = 200

    with patch("ml.core.cache.httpx.put", return_value=fake_response) as mock_put:
        set_cached_value("some-key", "some-value", _settings())

    mock_put.assert_called_once_with(
        f"https://api.cloudflare.com/client/v4/accounts/{'0' * 32}"
        f"/storage/kv/namespaces/{'1' * 32}/values/some-key",
        headers={"Authorization": "Bearer test-token"},
        content="some-value",
    )
    fake_response.raise_for_status.assert_called_once()


def test_set_cached_value_appends_expiration_ttl_when_given() -> None:
    fake_response = MagicMock()
    fake_response.status_code = 200

    with patch("ml.core.cache.httpx.put", return_value=fake_response) as mock_put:
        set_cached_value("some-key", "some-value", _settings(), expiration_ttl=3600)

    mock_put.assert_called_once_with(
        f"https://api.cloudflare.com/client/v4/accounts/{'0' * 32}"
        f"/storage/kv/namespaces/{'1' * 32}/values/some-key?expiration_ttl=3600",
        headers={"Authorization": "Bearer test-token"},
        content="some-value",
    )
