"""add tag scores

Revision ID: c3f1d7a9b2e4
Revises: a85c2bf6a4db
Create Date: 2026-10-22 15:10:00.000000

"""

from alembic import op
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "c3f1d7a9b2e4"
down_revision: str | None = "a85c2bf6a4db"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("track_features", Column("tag_scores", JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("track_features", "tag_scores")
