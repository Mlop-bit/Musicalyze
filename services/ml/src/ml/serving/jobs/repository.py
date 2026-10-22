import uuid
from datetime import timedelta
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from ml.serving.jobs.models import Job, JobKind, JobPhase, JobStatus

LEASE_EXPIRED_ERROR = "lease expired too many times"


def enqueue_job(session: Session, user_id: str, kind: JobKind, payload: dict[str, Any]) -> Job:
    job = Job(user_id=user_id, kind=kind, payload=payload)
    session.add(job)
    session.flush()
    session.refresh(job)
    return job


def claim_next_job(session: Session, lease_minutes: int, max_attempts: int) -> Job | None:
    expired = (Job.status == JobStatus.RUNNING) & (
        Job.locked_at < func.now() - timedelta(minutes=lease_minutes)
    )
    session.execute(
        update(Job)
        .where(expired, Job.attempts >= max_attempts)
        .values(status=JobStatus.FAILED, error=LEASE_EXPIRED_ERROR)
    )
    session.execute(update(Job).where(expired).values(status=JobStatus.QUEUED))
    job = session.execute(
        select(Job)
        .where(Job.status == JobStatus.QUEUED)
        .order_by(Job.created_at)
        .limit(1)
        .with_for_update(skip_locked=True)
    ).scalar_one_or_none()
    if job is None:
        return None
    job.status = JobStatus.RUNNING
    job.attempts += 1
    job.locked_at = func.now()
    session.flush()
    session.refresh(job)
    return job


def set_phase(session: Session, job_id: uuid.UUID, phase: JobPhase, total: int) -> None:
    session.execute(
        update(Job)
        .where(Job.id == job_id)
        .values(phase=phase, total=total, done=0, locked_at=func.now())
    )


def increment_done(session: Session, job_id: uuid.UUID) -> None:
    session.execute(
        update(Job).where(Job.id == job_id).values(done=Job.done + 1, locked_at=func.now())
    )


def complete_job(session: Session, job_id: uuid.UUID, result: dict[str, Any]) -> None:
    session.execute(
        update(Job).where(Job.id == job_id).values(status=JobStatus.SUCCEEDED, result=result)
    )


def fail_job(session: Session, job_id: uuid.UUID, error: str) -> None:
    session.execute(
        update(Job).where(Job.id == job_id).values(status=JobStatus.FAILED, error=error)
    )


def get_job(session: Session, job_id: uuid.UUID) -> Job | None:
    return session.get(Job, job_id)


def list_jobs(session: Session, user_id: str) -> list[Job]:
    return list(
        session.scalars(select(Job).where(Job.user_id == user_id).order_by(Job.created_at.desc()))
    )
