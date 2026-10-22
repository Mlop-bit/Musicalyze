from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

TrackId = Annotated[str, Field(min_length=1)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TrackDescriptor(StrictModel):
    track_id: TrackId
    title: str
    artist: str
    isrc: str | None = None
    musicbrainz_id: str | None = None


class ReorderPayload(StrictModel):
    tracks: list[TrackDescriptor]
    start_track_id: str | None = None


class SplitPayload(StrictModel):
    tracks: list[TrackDescriptor]
    k: int | None = Field(default=None, ge=1)


class RecommendPayload(StrictModel):
    seeds: list[TrackDescriptor]
    candidates: list[TrackDescriptor]
    tags: list[str] | None = None
    limit: int = Field(default=20, ge=1, le=100)
