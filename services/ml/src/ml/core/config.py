from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MUSICALYZE_")

    s3_endpoint_url: str
    s3_region: str
    s3_bucket: str
    s3_access_key: str
    s3_secret_key: str
    kv_account_id: str
    kv_namespace_id: str
    kv_api_token: str
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
