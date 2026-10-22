import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ml.serving.api.auth import require_api_key
from ml.serving.api.dependencies import get_session
from ml.serving.api.schemas import (
    JobCreated,
    JobView,
    RecommendRequest,
    ReorderRequest,
    SplitRequest,
    to_job_view,
)
from ml.serving.jobs.models import JobKind
from ml.serving.jobs.repository import enqueue_job, get_job, list_jobs

router = APIRouter(prefix="/jobs", dependencies=[Depends(require_api_key)])

SessionDependency = Annotated[Session, Depends(get_session)]


def _enqueue(
    session: Session, kind: JobKind, request: ReorderRequest | SplitRequest | RecommendRequest
) -> JobCreated:
    payload = request.model_dump(exclude={"user_id"})
    job = enqueue_job(session, request.user_id, kind, payload)
    session.commit()
    return JobCreated(job_id=job.id)


@router.post("/reorder", status_code=status.HTTP_202_ACCEPTED)
def create_reorder_job(request: ReorderRequest, session: SessionDependency) -> JobCreated:
    return _enqueue(session, JobKind.REORDER, request)


@router.post("/split", status_code=status.HTTP_202_ACCEPTED)
def create_split_job(request: SplitRequest, session: SessionDependency) -> JobCreated:
    return _enqueue(session, JobKind.SPLIT, request)


@router.post("/recommend", status_code=status.HTTP_202_ACCEPTED)
def create_recommend_job(request: RecommendRequest, session: SessionDependency) -> JobCreated:
    return _enqueue(session, JobKind.RECOMMEND, request)


@router.get("/{job_id}")
def read_job(job_id: uuid.UUID, session: SessionDependency) -> JobView:
    job = get_job(session, job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "job not found")
    return to_job_view(job)


@router.get("")
def read_user_jobs(
    user_id: Annotated[str, Query(min_length=1)], session: SessionDependency
) -> list[JobView]:
    return [to_job_view(job) for job in list_jobs(session, user_id)]
