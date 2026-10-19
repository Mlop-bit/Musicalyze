from typing import Any

import httpx

from ml.core.config import Settings
from ml.core.rate_limiter import TokenBucket
from ml.serving.entity_resolution.recording import MusicBrainzRecording

BASE_URL = "https://musicbrainz.org/ws/2"
TIMEOUT = 10.0
SEARCH_LIMIT = 10
ISRC_LOOKUP_RELEVANCE = 100
APPLICATION_IDENTIFIER = "Musicalyze/0.1"

_rate_limiter = TokenBucket(capacity=1, refill_per_second=1.0)


def lookup_recordings_by_isrc(settings: Settings, isrc: str) -> list[MusicBrainzRecording]:
    payload = _get(
        settings, f"{BASE_URL}/isrc/{isrc}", {"fmt": "json", "inc": "artist-credits"}, 404
    )
    if payload is None:
        return []
    return [
        _to_recording(recording, relevance=ISRC_LOOKUP_RELEVANCE)
        for recording in payload.get("recordings", [])
    ]


def search_recordings(settings: Settings, artist: str, title: str) -> list[MusicBrainzRecording]:
    query = f'recording:"{_escape(title)}" AND artist:"{_escape(artist)}"'
    payload = _get(
        settings, f"{BASE_URL}/recording", {"query": query, "fmt": "json", "limit": SEARCH_LIMIT}
    )
    if payload is None:
        return []
    return [
        _to_recording(recording, relevance=recording["score"])
        for recording in payload.get("recordings", [])
    ]


def _get(
    settings: Settings,
    url: str,
    params: dict[str, str | int],
    not_found_status: int | None = None,
) -> dict[str, Any] | None:
    _rate_limiter.acquire()
    response = httpx.get(
        url, params=params, headers={"User-Agent": _user_agent(settings)}, timeout=TIMEOUT
    )
    if response.status_code == not_found_status:
        return None
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    return payload


def _user_agent(settings: Settings) -> str:
    if settings.musicbrainz_contact is None:
        return APPLICATION_IDENTIFIER
    return f"{APPLICATION_IDENTIFIER} ( {settings.musicbrainz_contact} )"


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _to_recording(data: dict[str, Any], relevance: int) -> MusicBrainzRecording:
    artist = "".join(
        f"{credit['name']}{credit.get('joinphrase', '')}" for credit in data["artist-credit"]
    )
    return MusicBrainzRecording(
        mbid=data["id"], title=data["title"], artist=artist, relevance=relevance
    )
