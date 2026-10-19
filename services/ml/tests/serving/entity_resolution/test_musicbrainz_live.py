import pytest

from ml.core.config import Settings
from ml.serving.entity_resolution.matching import select_recording
from ml.serving.entity_resolution.musicbrainz import (
    lookup_recordings_by_isrc,
    search_recordings,
)


def _settings() -> Settings:
    return Settings.model_validate(
        {
            "s3_endpoint_url": "https://s3.example.com",
            "s3_region": "garage",
            "s3_bucket": "dev-bucket",
            "s3_access_key": "test-access-key",
            "s3_secret_key": "test-secret-key",
            "kv_account_id": "0" * 32,
            "kv_namespace_id": "1" * 32,
            "kv_api_token": "test-token",
            "db_host": "localhost",
            "db_port": 5432,
            "db_user": "musicalyze",
            "db_password": "musicalyze",
            "db_name": "musicalyze",
        }
    )


@pytest.mark.live
def test_lookup_by_isrc_finds_a_known_recording() -> None:
    recordings = lookup_recordings_by_isrc(_settings(), "USQX91300108")

    assert recordings
    assert any(recording["title"] == "Get Lucky" for recording in recordings)


@pytest.mark.live
def test_lookup_by_isrc_returns_nothing_for_an_unregistered_isrc() -> None:
    assert lookup_recordings_by_isrc(_settings(), "ZZZZZ0000000") == []


@pytest.mark.live
def test_search_and_matching_resolve_a_known_track() -> None:
    recordings = search_recordings(_settings(), artist="Daft Punk", title="Get Lucky")

    assert select_recording(recordings, artist="Daft Punk", title="Get Lucky") is not None
