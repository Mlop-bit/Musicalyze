import uuid
from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, Field

from ml.serving.jobs.models import Job, JobKind, JobPhase, JobStatus
from ml.serving.jobs.payloads import RecommendPayload, ReorderPayload, SplitPayload

UserId = Annotated[str, Field(min_length=1)]


class ReorderRequest(ReorderPayload):
    user_id: UserId


class SplitRequest(SplitPayload):
    user_id: UserId


class RecommendRequest(RecommendPayload):
    user_id: UserId


class TrackSearchRequest(BaseModel):
    query: str | None = Field(default=None, min_length=1)
    artist: str | None = Field(default=None, min_length=1)
    title: str | None = Field(default=None, min_length=1)
    musicbrainz_id: str | None = Field(default=None, min_length=1)


class TrackSearchResult(BaseModel):
    track_id: str
    musicbrainz_id: str | None
    bpm: float | None
    key: str | None
    mood_label: str | None
    mood_scores: dict[str, float] | None
    source: str | None


class JobCreated(BaseModel):
    job_id: uuid.UUID


class JobView(BaseModel):
    job_id: uuid.UUID
    kind: JobKind
    status: JobStatus
    phase: JobPhase | None
    done: int
    total: int
    error: str | None
    result: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


def to_job_view(job: Job) -> JobView:
    return JobView(
        job_id=job.id,
        kind=job.kind,
        status=job.status,
        phase=job.phase,
        done=job.done,
        total=job.total,
        error=job.error,
        result=job.result,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
