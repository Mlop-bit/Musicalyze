import logging

from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.serving.entity_resolution.resolver import resolve_musicbrainz_id
from ml.serving.feature_store.classification import save_classifier_mood_for_track
from ml.serving.feature_store.embedding import save_track_embedding_from_preview
from ml.serving.feature_store.enrichment import save_acousticbrainz_enrichment
from ml.serving.preview.deezer import search_deezer_track

logger = logging.getLogger(__name__)


def resolve_track(
    session: Session,
    settings: Settings,
    track_id: str,
    isrc: str | None = None,
    artist: str | None = None,
    title: str | None = None,
    musicbrainz_id: str | None = None,
    query: str | None = None,
) -> None:
    try:
        deezer_track = search_deezer_track(
            settings, isrc=isrc, artist=artist, track=title, query=query
        )
        if deezer_track is not None and deezer_track["preview_url"] is not None:
            save_track_embedding_from_preview(
                session,
                track_id,
                deezer_track["preview_url"],
                duration_sec=deezer_track["duration_sec"],
            )
    except Exception:
        logger.warning(
            "Deezer preview embedding failed for track_id=%s, continuing without it",
            track_id,
            exc_info=True,
        )

    if musicbrainz_id is None:
        musicbrainz_id = _find_musicbrainz_id(settings, track_id, isrc, artist, title)

    if musicbrainz_id is not None:
        try:
            save_acousticbrainz_enrichment(session, track_id, musicbrainz_id, settings)
        except Exception:
            logger.warning(
                "AcousticBrainz enrichment failed for track_id=%s musicbrainz_id=%s, "
                "continuing without it",
                track_id,
                musicbrainz_id,
                exc_info=True,
            )

    try:
        save_classifier_mood_for_track(session, settings, track_id)
    except Exception:
        logger.warning(
            "Classifier mood prediction failed for track_id=%s, continuing without it",
            track_id,
            exc_info=True,
        )


def _find_musicbrainz_id(
    settings: Settings,
    track_id: str,
    isrc: str | None,
    artist: str | None,
    title: str | None,
) -> str | None:
    try:
        return resolve_musicbrainz_id(settings, isrc=isrc, artist=artist, title=title)
    except Exception:
        logger.warning(
            "MusicBrainz lookup failed for track_id=%s, continuing without it",
            track_id,
            exc_info=True,
        )
        return None
