from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.serving.jobs.models import Job, JobKind, JobPhase, JobStatus
from ml.serving.jobs.repository import (
    claim_next_job,
    complete_job,
    enqueue_job,
    fail_job,
    get_job,
    increment_done,
    list_jobs,
    set_phase,
)

_USER = "test-user"
_OTHER_USER = "test-other-user"
_LEASE_MINUTES = 20
_MAX_ATTEMPTS = 3


def _wipe(session: Session) -> None:
    session.execute(delete(Job).where(Job.user_id.like("test-%")))
    session.commit()


@pytest.fixture
def session() -> Iterator[Session]:
    settings = Settings.model_validate({})
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        foreign_queued = session.scalar(
            select(func.count())
            .select_from(Job)
            .where(Job.status == JobStatus.QUEUED, Job.user_id.not_like("test-%"))
        )
        if foreign_queued:
            pytest.skip("queued jobs of real users exist in this database")
        _wipe(session)
        yield session
        session.rollback()
        _wipe(session)
    engine.dispose()


@pytest.mark.live
def test_enqueue_job_creates_a_queued_job(session: Session) -> None:
    job = enqueue_job(session, _USER, JobKind.REORDER, {"tracks": []})
    session.commit()

    stored = get_job(session, job.id)

    assert stored is not None
    assert stored.status == JobStatus.QUEUED
    assert stored.kind == JobKind.REORDER
    assert stored.payload == {"tracks": []}
    assert stored.done == 0
    assert stored.total == 0
    assert stored.attempts == 0


@pytest.mark.live
def test_claim_next_job_returns_oldest_queued_and_marks_running(session: Session) -> None:
    first = enqueue_job(session, _USER, JobKind.SPLIT, {})
    session.commit()
    enqueue_job(session, _USER, JobKind.REORDER, {})
    session.commit()

    claimed = claim_next_job(session, _LEASE_MINUTES, _MAX_ATTEMPTS)
    session.commit()

    assert claimed is not None
    assert claimed.id == first.id
    assert claimed.status == JobStatus.RUNNING
    assert claimed.attempts == 1
    assert claimed.locked_at is not None


@pytest.mark.live
def test_claim_next_job_returns_none_when_nothing_is_queued(session: Session) -> None:
    assert claim_next_job(session, _LEASE_MINUTES, _MAX_ATTEMPTS) is None


@pytest.mark.live
def test_two_sessions_never_claim_the_same_job(session: Session) -> None:
    enqueue_job(session, _USER, JobKind.REORDER, {})
    session.commit()
    engine = create_engine(Settings.model_validate({}).database_url)
    with Session(engine) as other:
        first = claim_next_job(session, _LEASE_MINUTES, _MAX_ATTEMPTS)
        second = claim_next_job(other, _LEASE_MINUTES, _MAX_ATTEMPTS)
        other.rollback()
    engine.dispose()
    session.commit()

    assert first is not None
    assert second is None


@pytest.mark.live
def test_expired_lease_is_requeued(session: Session) -> None:
    job = enqueue_job(session, _USER, JobKind.REORDER, {})
    job.status = JobStatus.RUNNING
    job.attempts = 1
    job.locked_at = datetime.now(UTC) - timedelta(hours=1)
    session.commit()

    claimed = claim_next_job(session, _LEASE_MINUTES, _MAX_ATTEMPTS)
    session.commit()

    assert claimed is not None
    assert claimed.id == job.id
    assert claimed.attempts == 2


@pytest.mark.live
def test_job_over_max_attempts_is_failed(session: Session) -> None:
    job = enqueue_job(session, _USER, JobKind.REORDER, {})
    job.status = JobStatus.RUNNING
    job.attempts = _MAX_ATTEMPTS
    job.locked_at = datetime.now(UTC) - timedelta(hours=1)
    session.commit()

    claimed = claim_next_job(session, _LEASE_MINUTES, _MAX_ATTEMPTS)
    session.commit()
    session.refresh(job)

    assert claimed is None
    assert job.status == JobStatus.FAILED
    assert job.error == "lease expired too many times"


@pytest.mark.live
def test_progress_and_completion_are_recorded(session: Session) -> None:
    job = enqueue_job(session, _USER, JobKind.SPLIT, {})
    session.commit()

    set_phase(session, job.id, JobPhase.RESOLVING, total=3)
    increment_done(session, job.id)
    increment_done(session, job.id)
    session.commit()
    session.refresh(job)
    assert (job.phase, job.total, job.done) == (JobPhase.RESOLVING, 3, 2)

    complete_job(session, job.id, {"clusters": []})
    session.commit()
    session.refresh(job)
    assert job.status == JobStatus.SUCCEEDED
    assert job.result == {"clusters": []}


@pytest.mark.live
def test_fail_job_records_the_error(session: Session) -> None:
    job = enqueue_job(session, _USER, JobKind.REORDER, {})
    session.commit()

    fail_job(session, job.id, "boom")
    session.commit()
    session.refresh(job)

    assert job.status == JobStatus.FAILED
    assert job.error == "boom"


@pytest.mark.live
def test_list_jobs_filters_by_user_newest_first(session: Session) -> None:
    older = enqueue_job(session, _USER, JobKind.REORDER, {})
    session.commit()
    newer = enqueue_job(session, _USER, JobKind.SPLIT, {})
    session.commit()
    enqueue_job(session, _OTHER_USER, JobKind.SPLIT, {})
    session.commit()

    jobs = list_jobs(session, _USER)

    assert [job.id for job in jobs] == [newer.id, older.id]
