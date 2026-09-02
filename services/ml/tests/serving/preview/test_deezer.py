from typing import Any
from unittest.mock import MagicMock, patch

from ml.serving.preview.deezer import search_deezer_track


def _response(payload: dict[str, Any]) -> MagicMock:
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    return response


def test_search_by_isrc_returns_the_matched_track() -> None:
    track_payload = {"id": 1, "title": "Get Lucky", "artist": {"name": "Daft Punk"}, "bpm": 116.0}

    with patch(
        "ml.serving.preview.deezer.httpx.get", return_value=_response(track_payload)
    ) as mock_get:
        result = search_deezer_track(isrc="GB28K1100036")

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

    with patch(
        "ml.serving.preview.deezer.httpx.get",
        side_effect=[isrc_error_response, search_response, track_response],
    ) as mock_get:
        result = search_deezer_track(isrc="unknown-isrc", artist="Daft Punk", track="Get Lucky")

    assert result is not None
    assert result["title"] == "Get Lucky"
    assert 'artist:"Daft Punk" track:"Get Lucky"' in result["method"]
    search_call = mock_get.call_args_list[1]
    assert search_call.kwargs["params"] == {"q": 'artist:"Daft Punk" track:"Get Lucky"'}


def test_search_returns_none_when_nothing_matches() -> None:
    with patch("ml.serving.preview.deezer.httpx.get", return_value=_response({"data": []})):
        result = search_deezer_track(query="a query with no results")

    assert result is None


def test_search_returns_none_without_any_criteria() -> None:
    result = search_deezer_track()

    assert result is None


def test_track_details_include_genres_from_the_album() -> None:
    track_payload = {"id": 1, "title": "Get Lucky", "album": {"id": 99}}
    album_payload = {"genres": {"data": [{"name": "Disco"}, {"name": "Funk"}]}}

    with patch(
        "ml.serving.preview.deezer.httpx.get",
        side_effect=[_response(track_payload), _response(album_payload)],
    ):
        result = search_deezer_track(isrc="GB28K1100036")

    assert result is not None
    assert result["genres"] == ["Disco", "Funk"]


def test_track_details_skip_album_lookup_when_no_album_id() -> None:
    track_payload = {"id": 1, "title": "Get Lucky"}

    with patch(
        "ml.serving.preview.deezer.httpx.get", return_value=_response(track_payload)
    ) as mock_get:
        result = search_deezer_track(isrc="GB28K1100036")

    assert result is not None
    assert result["genres"] == []
    mock_get.assert_called_once()


def test_bpm_of_zero_is_reported_as_unknown() -> None:
    track_payload = {"id": 1, "bpm": 0}

    with patch("ml.serving.preview.deezer.httpx.get", return_value=_response(track_payload)):
        result = search_deezer_track(isrc="GB28K1100036")

    assert result is not None
    assert result["bpm"] is None
