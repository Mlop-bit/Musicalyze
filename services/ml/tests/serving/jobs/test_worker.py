import uuid
from unittest.mock import MagicMock, patch

from ml.core.config import Settings
from ml.serving.jobs.models import Job, JobKind
from ml.worker import process_next_job

_MODULE = "ml.worker"


def _session() -> MagicMock:
    session = MagicMock()
    session.__enter__.return_value = session
    return session


def _settings() -> MagicMock:
    settings = MagicMock(spec=Settings)
    settings.job_lease_minutes = 20
    settings.job_max_attempts = 3
    return settings


def _job() -> Job:
    return Job(id=uuid.uuid4(), user_id="u", kind=JobKind.REORDER, payload={})


def test_process_next_job_completes_the_job() -> None:
    session = _session()
    job = _job()

    with (
        patch(f"{_MODULE}.claim_next_job", return_value=job),
        patch(f"{_MODULE}.run_job", return_value={"order": []}),
        patch(f"{_MODULE}.complete_job") as complete,
        patch(f"{_MODULE}.fail_job") as fail,
    ):
        processed = process_next_job(lambda: session, _settings())

    assert processed is True
    complete.assert_called_once_with(session, job.id, {"order": []})
    fail.assert_not_called()


def test_process_next_job_fails_the_job_on_error_with_the_message() -> None:
    session = _session()
    job = _job()

    with (
        patch(f"{_MODULE}.claim_next_job", return_value=job),
        patch(f"{_MODULE}.run_job", side_effect=RuntimeError("boom")),
        patch(f"{_MODULE}.complete_job") as complete,
        patch(f"{_MODULE}.fail_job") as fail,
    ):
        processed = process_next_job(lambda: session, _settings())

    assert processed is True
    fail.assert_called_once_with(session, job.id, "boom")
    complete.assert_not_called()
    session.rollback.assert_called_once()


def test_process_next_job_returns_false_when_idle() -> None:
    session = _session()

    with patch(f"{_MODULE}.claim_next_job", return_value=None):
        assert process_next_job(lambda: session, _settings()) is False
