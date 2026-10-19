from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from ml.core.config import Settings
from ml.serving.entity_resolution.musicbrainz import (
    lookup_recordings_by_isrc,
    search_recordings,
)


def _settings(contact: str | None = None) -> Settings:
    values: dict[str, Any] = {
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
    if contact is not None:
        values["musicbrainz_contact"] = contact
    return Settings.model_validate(values)


def _response(payload: dict[str, Any], status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=response
        )
    return response


@pytest.fixture(autouse=True)
def rate_limiter() -> Generator[MagicMock]:
    with patch("ml.serving.entity_resolution.musicbrainz._rate_limiter") as mock_limiter:
        yield mock_limiter


def _credit(name: str, joinphrase: str = "") -> dict[str, Any]:
    return {"name": name, "joinphrase": joinphrase, "artist": {"name": name}}


def test_lookup_by_isrc_returns_the_recordings_with_joined_artist_credits() -> None:
    payload = {
        "recordings": [
            {
                "id": "mbid-1",
                "title": "Get Lucky",
                "artist-credit": [_credit("Daft Punk", " feat. "), _credit("Pharrell Williams")],
            }
        ]
    }

    with patch(
        "ml.serving.entity_resolution.musicbrainz.httpx.get", return_value=_response(payload)
    ) as mock_get:
        recordings = lookup_recordings_by_isrc(_settings(), "GB28K1100036")

    assert recordings == [
        {
            "mbid": "mbid-1",
            "title": "Get Lucky",
            "artist": "Daft Punk feat. Pharrell Williams",
            "relevance": 100,
        }
    ]
    assert mock_get.call_args.args[0] == "https://musicbrainz.org/ws/2/isrc/GB28K1100036"
    assert mock_get.call_args.kwargs["params"] == {"fmt": "json", "inc": "artist-credits"}


def test_lookup_by_isrc_returns_no_recordings_for_an_unknown_isrc() -> None:
    with patch(
        "ml.serving.entity_resolution.musicbrainz.httpx.get",
        return_value=_response({"error": "Not Found"}, status_code=404),
    ):
        assert lookup_recordings_by_isrc(_settings(), "XX0000000000") == []


def test_search_recordings_maps_the_search_score_to_relevance() -> None:
    payload = {
        "recordings": [
            {
                "id": "mbid-1",
                "score": 97,
                "title": "Get Lucky",
                "artist-credit": [_credit("Daft Punk")],
            }
        ]
    }

    with patch(
        "ml.serving.entity_resolution.musicbrainz.httpx.get", return_value=_response(payload)
    ) as mock_get:
        recordings = search_recordings(_settings(), artist="Daft Punk", title="Get Lucky")

    assert recordings == [
        {"mbid": "mbid-1", "title": "Get Lucky", "artist": "Daft Punk", "relevance": 97}
    ]
    assert mock_get.call_args.args[0] == "https://musicbrainz.org/ws/2/recording"
    assert mock_get.call_args.kwargs["params"] == {
        "query": 'recording:"Get Lucky" AND artist:"Daft Punk"',
        "fmt": "json",
        "limit": 10,
    }


def test_search_recordings_escapes_quotes_and_backslashes_in_the_query() -> None:
    with patch(
        "ml.serving.entity_resolution.musicbrainz.httpx.get",
        return_value=_response({"recordings": []}),
    ) as mock_get:
        search_recordings(_settings(), artist='AC\\DC "Live"', title='Say "Hi"')

    assert mock_get.call_args.kwargs["params"]["query"] == (
        'recording:"Say \\"Hi\\"" AND artist:"AC\\\\DC \\"Live\\""'
    )


def test_requests_wait_for_the_rate_limiter(rate_limiter: MagicMock) -> None:
    with patch(
        "ml.serving.entity_resolution.musicbrainz.httpx.get",
        return_value=_response({"recordings": []}),
    ):
        search_recordings(_settings(), artist="A", title="T")
        lookup_recordings_by_isrc(_settings(), "GB28K1100036")

    assert rate_limiter.acquire.call_count == 2


def test_requests_identify_the_application_and_the_configured_contact() -> None:
    with patch(
        "ml.serving.entity_resolution.musicbrainz.httpx.get",
        return_value=_response({"recordings": []}),
    ) as mock_get:
        search_recordings(_settings(contact="ops@example.com"), artist="A", title="T")

    assert mock_get.call_args.kwargs["headers"]["User-Agent"] == (
        "Musicalyze/0.1 ( ops@example.com )"
    )


def test_requests_identify_the_application_without_a_contact() -> None:
    with patch(
        "ml.serving.entity_resolution.musicbrainz.httpx.get",
        return_value=_response({"recordings": []}),
    ) as mock_get:
        search_recordings(_settings(), artist="A", title="T")

    assert mock_get.call_args.kwargs["headers"]["User-Agent"] == "Musicalyze/0.1"


def test_search_recordings_raises_when_musicbrainz_is_unavailable() -> None:
    with (
        patch(
            "ml.serving.entity_resolution.musicbrainz.httpx.get",
            return_value=_response({}, status_code=503),
        ),
        pytest.raises(httpx.HTTPStatusError),
    ):
        search_recordings(_settings(), artist="A", title="T")
