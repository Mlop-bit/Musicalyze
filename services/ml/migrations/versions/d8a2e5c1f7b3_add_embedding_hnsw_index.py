"""add embedding hnsw index

Revision ID: d8a2e5c1f7b3
Revises: c3f1d7a9b2e4
Create Date: 2026-10-22 15:40:00.000000

"""

from alembic import op

revision: str = "d8a2e5c1f7b3"
down_revision: str | None = "c3f1d7a9b2e4"
branch_labels: str | None = None
depends_on: str | None = None

INDEX_NAME = "ix_track_features_embedding_hnsw"


def upgrade() -> None:
    op.execute(
        f"CREATE INDEX {INDEX_NAME} ON track_features USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute(f"DROP INDEX {INDEX_NAME}")
