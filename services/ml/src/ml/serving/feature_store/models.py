from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

EMBEDDING_DIM = 1024


class Base(DeclarativeBase):
    pass


class TrackFeatures(Base):
    __tablename__ = "track_features"

    track_id: Mapped[str] = mapped_column(primary_key=True)
    musicbrainz_id: Mapped[str | None]
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))
    duration_sec: Mapped[int | None]
    bpm: Mapped[float | None]
    key: Mapped[str | None]
    chords_changes_rate: Mapped[float | None]
    danceability: Mapped[float | None]
    average_loudness: Mapped[float | None]
    dynamic_complexity: Mapped[float | None]
    voice_instrumental: Mapped[str | None]
    mood_scores: Mapped[dict[str, float] | None] = mapped_column(JSONB)
    mood_label: Mapped[str | None]
    source: Mapped[str | None]
