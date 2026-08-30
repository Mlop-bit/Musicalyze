from typing import Annotated

from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

Port = Annotated[int, Field(gt=0, le=65535)]
CloudflareId = Annotated[str, Field(pattern=r"^[0-9a-f]{32}$")]
NonEmptyStr = Annotated[str, Field(min_length=1)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="MUSICALYZE_")

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

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password.get_secret_value()}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
