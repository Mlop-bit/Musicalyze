from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

EMBEDDING_DIM = 1024


class Base(DeclarativeBase):
    pass


class TrackFeatures(Base):
    __tablename__ = "track_features"

    track_id: Mapped[str] = mapped_column(primary_key=True)
    musicbrainz_id: Mapped[str | None]
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))
    bpm: Mapped[float | None]
    key: Mapped[str | None]
    mood_label: Mapped[str | None]
    source: Mapped[str | None]
