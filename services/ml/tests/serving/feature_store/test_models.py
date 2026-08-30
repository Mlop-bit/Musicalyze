from pgvector.sqlalchemy import Vector

from ml.serving.feature_store.models import TrackFeatures


def test_table_name_is_track_features() -> None:
    assert TrackFeatures.__tablename__ == "track_features"


def test_track_id_is_the_primary_key() -> None:
    column = TrackFeatures.__table__.c.track_id
    assert column.primary_key is True
    assert column.nullable is False


def test_embedding_is_a_required_pgvector_column() -> None:
    column = TrackFeatures.__table__.c.embedding
    assert isinstance(column.type, Vector)
    assert column.type.dim == 1024
    assert column.nullable is False


def test_enrichment_columns_are_nullable() -> None:
    table = TrackFeatures.__table__
    for name in ("musicbrainz_id", "bpm", "key", "mood_label", "source"):
        assert table.c[name].nullable is True
