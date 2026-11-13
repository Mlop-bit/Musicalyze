import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.serving.api.auth import require_api_key
from ml.serving.api.dependencies import get_session, get_settings
from ml.serving.api.schemas import TrackSearchRequest, TrackSearchResult
from ml.serving.feature_store.repository import get_track_features
from ml.serving.feature_store.resolution import resolve_track

router = APIRouter(prefix="/tracks", dependencies=[Depends(require_api_key)])
SessionDependency = Annotated[Session, Depends(get_session)]
SettingsDependency = Annotated[Settings, Depends(get_settings)]


@router.post("/search", response_model=TrackSearchResult)
def search_track(
    request: TrackSearchRequest,
    session: SessionDependency,
    settings: SettingsDependency,
) -> TrackSearchResult:
    if not request.musicbrainz_id and not request.query and not (request.artist or request.title):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Provide a title, an artist, or a MusicBrainz ID.",
        )

    track_id = f"search-{uuid.uuid4()}"
    resolve_track(
        session,
        settings,
        track_id,
        artist=request.artist,
        title=request.title,
        musicbrainz_id=request.musicbrainz_id,
        query=request.query,
    )
    session.commit()
    row = get_track_features(session, track_id)
    if row is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "No audio features were found for this track. "
            "Try another search or add a MusicBrainz ID.",
        )
    return TrackSearchResult(
        track_id=row.track_id,
        musicbrainz_id=row.musicbrainz_id,
        bpm=row.bpm,
        key=row.key,
        mood_label=row.mood_label,
        mood_scores=row.mood_scores,
        source=row.source,
    )
