import json
from collections.abc import Generator
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from ml.core.config import Settings
from ml.serving.entity_resolution.recording import MusicBrainzRecording
from ml.serving.entity_resolution.resolver import (
    UNRESOLVED_CACHE_TTL_SECONDS,
    resolve_musicbrainz_id,
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
            "api_key": "test-api-key",
        }
    )


def _recording(
    mbid: str, title: str = "Get Lucky", artist: str = "Daft Punk"
) -> MusicBrainzRecording:
    return MusicBrainzRecording(mbid=mbid, title=title, artist=artist, relevance=100)


@dataclass
class Mocks:
    get_cached: MagicMock
    set_cached: MagicMock
    lookup_by_isrc: MagicMock
    search: MagicMock


@pytest.fixture
def mocks() -> Generator[Mocks]:
    module = "ml.serving.entity_resolution.resolver"
    with (
        patch(f"{module}.get_cached_value", return_value=None) as get_cached,
        patch(f"{module}.set_cached_value") as set_cached,
        patch(f"{module}.lookup_recordings_by_isrc", return_value=[]) as lookup_by_isrc,
        patch(f"{module}.search_recordings", return_value=[]) as search,
    ):
        yield Mocks(get_cached, set_cached, lookup_by_isrc, search)


def test_a_cached_musicbrainz_id_is_returned_without_calling_musicbrainz(mocks: Mocks) -> None:
    mocks.get_cached.return_value = json.dumps({"mbid": "cached-mbid"})

    result = resolve_musicbrainz_id(_settings(), isrc="USQX91300108", artist="A", title="T")

    assert result == "cached-mbid"
    mocks.lookup_by_isrc.assert_not_called()
    mocks.search.assert_not_called()
    mocks.set_cached.assert_not_called()


def test_a_cached_unresolved_result_is_returned_without_calling_musicbrainz(mocks: Mocks) -> None:
    mocks.get_cached.return_value = json.dumps({"mbid": None})

    result = resolve_musicbrainz_id(_settings(), isrc="USQX91300108", artist="A", title="T")

    assert result is None
    mocks.lookup_by_isrc.assert_not_called()
    mocks.search.assert_not_called()


def test_an_isrc_match_is_used_and_cached_permanently(mocks: Mocks) -> None:
    mocks.lookup_by_isrc.return_value = [_recording("isrc-mbid"), _recording("other")]

    result = resolve_musicbrainz_id(_settings(), isrc="USQX91300108", artist="A", title="T")

    assert result == "isrc-mbid"
    mocks.search.assert_not_called()
    mocks.set_cached.assert_called_once()
    assert json.loads(mocks.set_cached.call_args.args[1]) == {"mbid": "isrc-mbid"}
    assert mocks.set_cached.call_args.kwargs["expiration_ttl"] is None


def test_the_title_and_artist_search_is_used_when_the_isrc_finds_nothing(mocks: Mocks) -> None:
    mocks.search.return_value = [_recording("search-mbid")]

    result = resolve_musicbrainz_id(
        _settings(), isrc="USQX91300108", artist="Daft Punk", title="Get Lucky"
    )

    assert result == "search-mbid"
    mocks.lookup_by_isrc.assert_called_once_with(_settings(), "USQX91300108")
    mocks.search.assert_called_once_with(_settings(), "Daft Punk", "Get Lucky")


def test_the_title_and_artist_search_is_used_when_there_is_no_isrc(mocks: Mocks) -> None:
    mocks.search.return_value = [_recording("search-mbid")]

    result = resolve_musicbrainz_id(_settings(), artist="Daft Punk", title="Get Lucky")

    assert result == "search-mbid"
    mocks.lookup_by_isrc.assert_not_called()


def test_a_search_result_that_does_not_match_leaves_the_track_unresolved(mocks: Mocks) -> None:
    mocks.search.return_value = [_recording("wrong", title="Around the World")]

    result = resolve_musicbrainz_id(_settings(), artist="Daft Punk", title="Get Lucky")

    assert result is None


def test_an_unresolved_result_is_cached_with_an_expiry(mocks: Mocks) -> None:
    resolve_musicbrainz_id(_settings(), artist="Daft Punk", title="Get Lucky")

    assert json.loads(mocks.set_cached.call_args.args[1]) == {"mbid": None}
    assert mocks.set_cached.call_args.kwargs["expiration_ttl"] == UNRESOLVED_CACHE_TTL_SECONDS


def test_nothing_is_looked_up_or_cached_without_an_isrc_or_an_artist_and_title(
    mocks: Mocks,
) -> None:
    result = resolve_musicbrainz_id(_settings(), artist="Daft Punk")

    assert result is None
    mocks.get_cached.assert_not_called()
    mocks.lookup_by_isrc.assert_not_called()
    mocks.search.assert_not_called()
    mocks.set_cached.assert_not_called()


def test_a_musicbrainz_failure_propagates_and_caches_nothing(mocks: Mocks) -> None:
    mocks.search.side_effect = RuntimeError("musicbrainz unavailable")

    with pytest.raises(RuntimeError):
        resolve_musicbrainz_id(_settings(), artist="Daft Punk", title="Get Lucky")

    mocks.set_cached.assert_not_called()


def test_the_cache_key_is_stable_and_safe_for_a_url_path(mocks: Mocks) -> None:
    resolve_musicbrainz_id(_settings(), artist="AC/DC", title="Back In Black?")
    resolve_musicbrainz_id(_settings(), artist="AC/DC", title="Back In Black?")

    first_key, second_key = (call.args[0] for call in mocks.get_cached.call_args_list)
    assert first_key == second_key
    assert first_key.startswith("musicbrainz-resolve:")
    assert "/" not in first_key.removeprefix("musicbrainz-resolve:")
    assert " " not in first_key
