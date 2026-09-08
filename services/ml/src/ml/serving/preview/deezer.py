import json
from typing import Any, TypedDict

import httpx

from ml.core.cache import get_cached_value, set_cached_value
from ml.core.config import Settings

BASE_URL = "https://api.deezer.com"
TIMEOUT = 10.0
# Deezer signs preview URLs with a short-lived expiry, so caching a search
# result longer than that would serve back a dead link.
SEARCH_CACHE_TTL_SECONDS = 120
# Deezer's API blocks requests carrying a generic HTTP client user agent.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


class DeezerTrack(TypedDict):
    method: str
    deezer_id: int | None
    isrc: str | None
    title: str | None
    artist: str | None
    bpm: float | None
    duration_sec: int | None
    release_date: str | None
    popularity_rank: int | None
    explicit_lyrics: bool | None
    gain_db: float | None
    genres: list[str]
    preview_url: str | None


def search_deezer_track(
    settings: Settings,
    isrc: str | None = None,
    artist: str | None = None,
    track: str | None = None,
    query: str | None = None,
) -> DeezerTrack | None:
    cache_key = f"deezer-search:{isrc or ''}|{artist or ''}|{track or ''}|{query or ''}"
    cached = get_cached_value(cache_key, settings)
    if cached is not None:
        return json.loads(cached)

    result = _search_deezer_track(isrc, artist, track, query)
    set_cached_value(
        cache_key, json.dumps(result), settings, expiration_ttl=SEARCH_CACHE_TTL_SECONDS
    )
    return result


def _search_deezer_track(
    isrc: str | None,
    artist: str | None,
    track: str | None,
    query: str | None,
) -> DeezerTrack | None:
    if isrc:
        response = httpx.get(f"{BASE_URL}/track/isrc:{isrc}", headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        if "error" not in payload:
            return _to_deezer_track(payload, "ISRC search")

    search_query = _build_query(artist, track, query)
    if search_query is None:
        return None

    search_response = httpx.get(
        f"{BASE_URL}/search", params={"q": search_query}, headers=HEADERS, timeout=TIMEOUT
    )
    search_response.raise_for_status()
    results = search_response.json().get("data", [])
    if not results:
        return None

    track_response = httpx.get(
        f"{BASE_URL}/track/{results[0]['id']}", headers=HEADERS, timeout=TIMEOUT
    )
    track_response.raise_for_status()
    return _to_deezer_track(track_response.json(), f"flexible search ({search_query!r})")


def _build_query(artist: str | None, track: str | None, query: str | None) -> str | None:
    if artist and track:
        return f'artist:"{artist}" track:"{track}"'
    if artist:
        return f'artist:"{artist}"'
    if track:
        return f'track:"{track}"'
    return query


def _to_deezer_track(data: dict[str, Any], method: str) -> DeezerTrack:
    album_id = data.get("album", {}).get("id")
    genres: list[str] = []
    if album_id:
        album_response = httpx.get(f"{BASE_URL}/album/{album_id}", headers=HEADERS, timeout=TIMEOUT)
        album_response.raise_for_status()
        genres = [
            genre["name"] for genre in album_response.json().get("genres", {}).get("data", [])
        ]

    return DeezerTrack(
        method=method,
        deezer_id=data.get("id"),
        isrc=data.get("isrc"),
        title=data.get("title"),
        artist=data.get("artist", {}).get("name"),
        # Deezer reports 0 when the label never submitted a BPM for this track.
        bpm=data.get("bpm") or None,
        duration_sec=data.get("duration"),
        release_date=data.get("release_date"),
        # Deezer's own popularity scale: 0 to 1,000,000, where 1,000,000 is the best rank.
        popularity_rank=data.get("rank"),
        explicit_lyrics=data.get("explicit_lyrics"),
        gain_db=data.get("gain"),
        genres=genres,
        # Deezer preview URLs are geo/licensing-restricted and are frequently missing or dead.
        preview_url=data.get("preview"),
    )
