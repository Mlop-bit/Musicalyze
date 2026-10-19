import hashlib
import json

from ml.core.cache import get_cached_value, set_cached_value
from ml.core.config import Settings
from ml.serving.entity_resolution.matching import select_recording
from ml.serving.entity_resolution.musicbrainz import lookup_recordings_by_isrc, search_recordings

UNRESOLVED_CACHE_TTL_SECONDS = 7 * 24 * 60 * 60
CACHE_KEY_PREFIX = "musicbrainz-resolve"


def resolve_musicbrainz_id(
    settings: Settings,
    isrc: str | None = None,
    artist: str | None = None,
    title: str | None = None,
) -> str | None:
    if not isrc and not (artist and title):
        return None

    cache_key = _cache_key(isrc, artist, title)
    cached = get_cached_value(cache_key, settings)
    if cached is not None:
        mbid: str | None = json.loads(cached)["mbid"]
        return mbid

    mbid = _resolve(settings, isrc, artist, title)
    set_cached_value(
        cache_key,
        json.dumps({"mbid": mbid}),
        settings,
        expiration_ttl=None if mbid is not None else UNRESOLVED_CACHE_TTL_SECONDS,
    )
    return mbid


def _resolve(
    settings: Settings, isrc: str | None, artist: str | None, title: str | None
) -> str | None:
    if isrc:
        recordings = lookup_recordings_by_isrc(settings, isrc)
        if recordings:
            return recordings[0]["mbid"]

    if artist and title:
        return select_recording(search_recordings(settings, artist, title), artist, title)

    return None


def _cache_key(isrc: str | None, artist: str | None, title: str | None) -> str:
    fingerprint = json.dumps([isrc or "", artist or "", title or ""])
    digest = hashlib.sha256(fingerprint.encode()).hexdigest()
    return f"{CACHE_KEY_PREFIX}:{digest}"
