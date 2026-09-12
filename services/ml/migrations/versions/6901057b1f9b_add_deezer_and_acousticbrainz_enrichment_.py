"""add deezer and acousticbrainz enrichment fields

Revision ID: 6901057b1f9b
Revises: 96eacc6ccfa5
Create Date: 2026-09-12 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "6901057b1f9b"
down_revision: str | None = "96eacc6ccfa5"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("track_features", sa.Column("duration_sec", sa.Integer(), nullable=True))
    op.add_column("track_features", sa.Column("chords_changes_rate", sa.Float(), nullable=True))
    op.add_column("track_features", sa.Column("danceability", sa.Float(), nullable=True))
    op.add_column("track_features", sa.Column("average_loudness", sa.Float(), nullable=True))
    op.add_column("track_features", sa.Column("dynamic_complexity", sa.Float(), nullable=True))
    op.add_column("track_features", sa.Column("voice_instrumental", sa.String(), nullable=True))
    op.add_column("track_features", sa.Column("mood_scores", JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("track_features", "mood_scores")
    op.drop_column("track_features", "voice_instrumental")
    op.drop_column("track_features", "dynamic_complexity")
    op.drop_column("track_features", "average_loudness")
    op.drop_column("track_features", "danceability")
    op.drop_column("track_features", "chords_changes_rate")
    op.drop_column("track_features", "duration_sec")
