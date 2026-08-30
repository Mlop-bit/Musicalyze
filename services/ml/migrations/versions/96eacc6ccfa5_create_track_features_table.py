"""create track_features table

Revision ID: 96eacc6ccfa5
Revises:
Create Date: 2026-08-30 11:44:53.328995

"""

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "96eacc6ccfa5"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "track_features",
        sa.Column("track_id", sa.String(), nullable=False),
        sa.Column("musicbrainz_id", sa.String(), nullable=True),
        sa.Column("embedding", Vector(1024), nullable=False),
        sa.Column("bpm", sa.Float(), nullable=True),
        sa.Column("key", sa.String(), nullable=True),
        sa.Column("mood_label", sa.String(), nullable=True),
        sa.Column("source", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("track_id"),
    )


def downgrade() -> None:
    op.drop_table("track_features")
