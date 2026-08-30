from ml.core.config import Settings


def _settings(
    db_host: str = "localhost",
    db_port: int = 5432,
    db_user: str = "musicalyze",
    db_password: str = "musicalyze",
    db_name: str = "musicalyze",
) -> Settings:
    return Settings(
        s3_endpoint_url="https://s3.example.com",
        s3_region="garage",
        s3_bucket="dev-bucket",
        s3_access_key="test-access-key",
        s3_secret_key="test-secret-key",
        kv_account_id="test-account",
        kv_namespace_id="test-namespace",
        kv_api_token="test-token",
        db_host=db_host,
        db_port=db_port,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
    )


def test_database_url_builds_postgres_dsn_with_psycopg_driver() -> None:
    settings = _settings(
        db_host="db.internal",
        db_port=6543,
        db_user="alice",
        db_password="s3cr3t",
        db_name="musicalyze",
    )

    assert settings.database_url == "postgresql+psycopg://alice:s3cr3t@db.internal:6543/musicalyze"
