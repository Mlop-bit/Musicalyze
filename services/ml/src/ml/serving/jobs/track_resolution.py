import logging
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.serving.feature_store.repository import get_track_features
from ml.serving.feature_store.resolution import resolve_track
from ml.serving.jobs.payloads import TrackDescriptor

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResolutionOutcome:
    resolved_ids: list[str]
    skipped_ids: list[str]
    dropped_candidates: int


def resolve_tracks(
    session: Session,
    settings: Settings,
    tracks: list[TrackDescriptor],
    on_progress: Callable[[int, int], None],
    new_limit: int | None = None,
) -> ResolutionOutcome:
    if new_limit is not None and new_limit < 0:
        raise ValueError("new_limit must not be negative")
    first_seen: dict[str, TrackDescriptor] = {}
    for track in tracks:
        first_seen.setdefault(track.track_id, track)
    unique = list(first_seen.values())
    already_stored = {
        track.track_id for track in unique if get_track_features(session, track.track_id)
    }
    new_tracks = [track for track in unique if track.track_id not in already_stored]
    dropped = new_tracks[new_limit:] if new_limit is not None else []
    dropped_ids = {track.track_id for track in dropped}
    considered = [track for track in unique if track.track_id not in dropped_ids]
    for done, track in enumerate(considered, start=1):
        if track.track_id not in already_stored:
            _resolve_one(session, settings, track)
        on_progress(done, len(considered))
    resolved_ids: list[str] = []
    skipped_ids: list[str] = []
    for track in considered:
        stored = get_track_features(session, track.track_id) is not None
        (resolved_ids if stored else skipped_ids).append(track.track_id)
    return ResolutionOutcome(
        resolved_ids=resolved_ids, skipped_ids=skipped_ids, dropped_candidates=len(dropped)
    )


def _resolve_one(session: Session, settings: Settings, track: TrackDescriptor) -> None:
    try:
        resolve_track(
            session,
            settings,
            track.track_id,
            isrc=track.isrc,
            artist=track.artist,
            title=track.title,
            musicbrainz_id=track.musicbrainz_id,
        )
        session.commit()
    except Exception:
        session.rollback()
        logger.warning("Resolving track_id=%s failed, skipping it", track.track_id, exc_info=True)
