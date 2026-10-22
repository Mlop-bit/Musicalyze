from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from ml.core.config import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.model_validate({})


@lru_cache(maxsize=1)
def _engine() -> Engine:
    return create_engine(get_settings().database_url)


def get_session() -> Iterator[Session]:
    with Session(_engine()) as session:
        yield session
