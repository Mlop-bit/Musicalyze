from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ml.core.config import Settings


@contextmanager
def session_scope(settings: Settings) -> Generator[Session]:
    engine = create_engine(settings.database_url)
    try:
        with Session(engine) as session:
            yield session
    finally:
        engine.dispose()
