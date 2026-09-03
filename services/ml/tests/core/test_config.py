from pathlib import Path

import pytest
from pydantic import ValidationError

from ml.core.config import Settings

_VALID_KV_ACCOUNT_ID = "0" * 32
_VALID_KV_NAMESPACE_ID = "1" * 32


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "s3_endpoint_url": "https://s3.example.com",
        "s3_region": "garage",
        "s3_bucket": "dev-bucket",
        "s3_access_key": "test-access-key",
        "s3_secret_key": "test-secret-key",
        "kv_account_id": _VALID_KV_ACCOUNT_ID,
        "kv_namespace_id": _VALID_KV_NAMESPACE_ID,
        "kv_api_token": "test-token",
        "db_host": "localhost",
        "db_port": 5432,
        "db_user": "musicalyze",
        "db_password": "musicalyze",
        "db_name": "musicalyze",
    }
    values.update(overrides)
    return Settings.model_validate(values)


def test_database_url_builds_postgres_dsn_with_psycopg_driver() -> None:
    settings = _settings(
        db_host="db.internal",
        db_port=6543,
        db_user="alice",
        db_password="s3cr3t",
        db_name="musicalyze",
    )

    assert settings.database_url == "postgresql+psycopg://alice:s3cr3t@db.internal:6543/musicalyze"


def test_invalid_s3_endpoint_url_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _settings(s3_endpoint_url="not-a-url")


def test_db_port_below_valid_range_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _settings(db_port=0)


def test_db_port_above_valid_range_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _settings(db_port=70000)


def test_kv_account_id_must_be_32_char_hex() -> None:
    with pytest.raises(ValidationError):
        _settings(kv_account_id="not-a-cloudflare-id")


def test_kv_namespace_id_must_be_32_char_hex() -> None:
    with pytest.raises(ValidationError):
        _settings(kv_namespace_id="not-a-cloudflare-id")


def test_empty_db_host_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _settings(db_host="")


def test_tolerates_unprefixed_keys_in_env_file_belonging_to_other_tools(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "MUSICALYZE_S3_ENDPOINT_URL=https://s3.example.com\n"
        "MUSICALYZE_S3_REGION=garage\n"
        "MUSICALYZE_S3_BUCKET=dev-bucket\n"
        "MUSICALYZE_S3_ACCESS_KEY=test-access-key\n"
        "MUSICALYZE_S3_SECRET_KEY=test-secret-key\n"
        f"MUSICALYZE_KV_ACCOUNT_ID={_VALID_KV_ACCOUNT_ID}\n"
        f"MUSICALYZE_KV_NAMESPACE_ID={_VALID_KV_NAMESPACE_ID}\n"
        "MUSICALYZE_KV_API_TOKEN=test-token\n"
        "MUSICALYZE_DB_HOST=localhost\n"
        "MUSICALYZE_DB_PORT=5432\n"
        "MUSICALYZE_DB_USER=musicalyze\n"
        "MUSICALYZE_DB_PASSWORD=musicalyze\n"
        "MUSICALYZE_DB_NAME=musicalyze\n"
        "HF_TOKEN=hf_some_token_owned_by_huggingface_hub_not_us\n"
    )

    settings = Settings(_env_file=env_file)  # type: ignore[call-arg]

    assert settings.db_host == "localhost"


def test_secret_fields_are_masked_in_repr() -> None:
    settings = _settings(db_password="s3cr3t", kv_api_token="t0ken", s3_secret_key="s3key")

    dump = repr(settings)

    assert "s3cr3t" not in dump
    assert "t0ken" not in dump
    assert "s3key" not in dump
