import json
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch

from ml.core.config import Settings
from ml.serving.preview.deezer import search_deezer_track


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


def _response(payload: dict[str, Any]) -> MagicMock:
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    return response


@contextmanager
def _patch_cache_miss() -> Generator[None]:
    with (
        patch("ml.serving.preview.deezer.get_cached_value", return_value=None),
        patch("ml.serving.preview.deezer.set_cached_value"),
    ):
        yield


def test_search_by_isrc_returns_the_matched_track() -> None:
    track_payload = {"id": 1, "title": "Get Lucky", "artist": {"name": "Daft Punk"}, "bpm": 116.0}

    with (
        patch(
            "ml.serving.preview.deezer.httpx.get", return_value=_response(track_payload)
        ) as mock_get,
        _patch_cache_miss(),
    ):
        result = search_deezer_track(_settings(), isrc="GB28K1100036")

    assert result is not None
    assert result["method"] == "ISRC search"
    assert result["title"] == "Get Lucky"
    assert result["artist"] == "Daft Punk"
    mock_get.assert_called_once()
    assert mock_get.call_args.args[0] == "https://api.deezer.com/track/isrc:GB28K1100036"


def test_search_falls_back_to_query_search_when_isrc_is_not_found() -> None:
    isrc_error_response = _response({"error": {"message": "no data"}})
    search_response = _response({"data": [{"id": 42}]})
    track_response = _response({"id": 42, "title": "Get Lucky"})

    with (
        patch(
            "ml.serving.preview.deezer.httpx.get",
            side_effect=[isrc_error_response, search_response, track_response],
        ) as mock_get,
        _patch_cache_miss(),
    ):
        result = search_deezer_track(
            _settings(), isrc="unknown-isrc", artist="Daft Punk", track="Get Lucky"
        )

    assert result is not None
    assert result["title"] == "Get Lucky"
    assert 'artist:"Daft Punk" track:"Get Lucky"' in result["method"]
    search_call = mock_get.call_args_list[1]
    assert search_call.kwargs["params"] == {"q": 'artist:"Daft Punk" track:"Get Lucky"'}


def test_search_returns_none_when_nothing_matches() -> None:
    with (
        patch("ml.serving.preview.deezer.httpx.get", return_value=_response({"data": []})),
        _patch_cache_miss(),
    ):
        result = search_deezer_track(_settings(), query="a query with no results")

    assert result is None


def test_search_returns_none_without_any_criteria() -> None:
    with _patch_cache_miss():
        result = search_deezer_track(_settings())

    assert result is None


def test_track_details_include_genres_from_the_album() -> None:
    track_payload = {"id": 1, "title": "Get Lucky", "album": {"id": 99}}
    album_payload = {"genres": {"data": [{"name": "Disco"}, {"name": "Funk"}]}}

    with (
        patch(
            "ml.serving.preview.deezer.httpx.get",
            side_effect=[_response(track_payload), _response(album_payload)],
        ),
        _patch_cache_miss(),
    ):
        result = search_deezer_track(_settings(), isrc="GB28K1100036")

    assert result is not None
    assert result["genres"] == ["Disco", "Funk"]


def test_track_details_skip_album_lookup_when_no_album_id() -> None:
    track_payload = {"id": 1, "title": "Get Lucky"}

    with (
        patch(
            "ml.serving.preview.deezer.httpx.get", return_value=_response(track_payload)
        ) as mock_get,
        _patch_cache_miss(),
    ):
        result = search_deezer_track(_settings(), isrc="GB28K1100036")

    assert result is not None
    assert result["genres"] == []
    mock_get.assert_called_once()


def test_bpm_of_zero_is_reported_as_unknown() -> None:
    track_payload = {"id": 1, "bpm": 0}

    with (
        patch("ml.serving.preview.deezer.httpx.get", return_value=_response(track_payload)),
        _patch_cache_miss(),
    ):
        result = search_deezer_track(_settings(), isrc="GB28K1100036")

    assert result is not None
    assert result["bpm"] is None


def test_search_returns_the_cached_value_without_calling_deezer() -> None:
    cached_track = {"method": "ISRC search", "title": "Cached Track"}

    with (
        patch("ml.serving.preview.deezer.httpx.get") as mock_get,
        patch("ml.serving.preview.deezer.get_cached_value", return_value=json.dumps(cached_track)),
        patch("ml.serving.preview.deezer.set_cached_value") as mock_set_cached_value,
    ):
        result = search_deezer_track(_settings(), isrc="GB28K1100036")

    assert result == cached_track
    mock_get.assert_not_called()
    mock_set_cached_value.assert_not_called()


def test_search_caches_the_result_under_a_key_built_from_the_criteria() -> None:
    track_payload = {"id": 1, "title": "Get Lucky"}

    with (
        patch("ml.serving.preview.deezer.httpx.get", return_value=_response(track_payload)),
        patch("ml.serving.preview.deezer.get_cached_value", return_value=None),
        patch("ml.serving.preview.deezer.set_cached_value") as mock_set_cached_value,
    ):
        result = search_deezer_track(_settings(), isrc="GB28K1100036")

    mock_set_cached_value.assert_called_once()
    cache_key, cached_value, _ = mock_set_cached_value.call_args.args
    assert cache_key == "deezer-search:GB28K1100036|||"
    assert json.loads(cached_value) == result
