from pathlib import Path
from typing import Annotated

from dotenv import find_dotenv, load_dotenv
from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv(usecwd=True))

Port = Annotated[int, Field(gt=0, le=65535)]
CloudflareId = Annotated[str, Field(pattern=r"^[0-9a-f]{32}$")]
NonEmptyStr = Annotated[str, Field(min_length=1)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MUSICALYZE_", extra="ignore")

    s3_endpoint_url: HttpUrl
    s3_region: NonEmptyStr
    s3_bucket: NonEmptyStr
    s3_access_key: NonEmptyStr
    s3_secret_key: SecretStr
    kv_account_id: CloudflareId
    kv_namespace_id: CloudflareId
    kv_api_token: SecretStr
    db_host: NonEmptyStr
    db_port: Port
    db_user: NonEmptyStr
    db_password: SecretStr
    db_name: NonEmptyStr
    api_key: SecretStr
    musicbrainz_contact: NonEmptyStr | None = None
    acousticbrainz_dump_dir: Path = Path("acousticbrainz-dumps")
    acousticbrainz_extract_dir: Path = Path("acousticbrainz-extracted")
    acousticbrainz_shard_cache_dir: Path = Path("acousticbrainz-shard-cache")
    acousticbrainz_download_missing_shards: bool = True
    acousticbrainz_include_lowlevel: bool = False
    acousticbrainz_max_cached_shards: int = Field(default=16, gt=0)
    classifier_cache_dir: Path = Path("classifier-cache")
    max_new_candidates: int = Field(default=150, ge=0)
    job_lease_minutes: int = Field(default=20, gt=0)
    job_max_attempts: int = Field(default=3, gt=0)
    worker_poll_seconds: float = Field(default=2.0, gt=0)

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password.get_secret_value()}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
