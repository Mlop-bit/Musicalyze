import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from ml.core.config import Settings
from ml.serving.api.app import app
from ml.serving.api.dependencies import get_session, get_settings
from ml.serving.jobs.models import Job, JobKind, JobPhase, JobStatus

_MODULE = "ml.serving.api.jobs"
_API_KEY = "secret-key"
_HEADERS = {"X-API-Key": _API_KEY}
_TRACK = {"track_id": "t1", "title": "Creep", "artist": "Radiohead"}


def _settings() -> Settings:
    return Settings.model_validate(
        {
            "s3_endpoint_url": "https://s3.example.com",
            "s3_region": "garage",
            "s3_bucket": "dev-bucket",
            "s3_access_key": "access",
            "s3_secret_key": "secret",
            "kv_account_id": "0" * 32,
            "kv_namespace_id": "1" * 32,
            "kv_api_token": "token",
            "db_host": "localhost",
            "db_port": 5432,
            "db_user": "user",
            "db_password": "password",
            "db_name": "name",
            "api_key": _API_KEY,
        }
    )


def _job(**overrides: object) -> Job:
    values: dict[str, object] = {
        "id": uuid.uuid4(),
        "user_id": "u1",
        "kind": JobKind.REORDER,
        "payload": {},
        "status": JobStatus.RUNNING,
        "phase": JobPhase.RESOLVING,
        "total": 10,
        "done": 4,
        "result": None,
        "error": None,
        "created_at": datetime(2026, 10, 22, tzinfo=UTC),
        "updated_at": datetime(2026, 10, 22, tzinfo=UTC),
    }
    values.update(overrides)
    return Job(**values)


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_settings] = _settings
    app.dependency_overrides[get_session] = lambda: MagicMock()
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_missing_api_key_is_unauthorised_and_enqueues_nothing(client: TestClient) -> None:
    with patch(f"{_MODULE}.enqueue_job") as enqueue:
        response = client.post("/jobs/reorder", json={"user_id": "u1", "tracks": [_TRACK]})

    assert response.status_code == 401
    enqueue.assert_not_called()


def test_wrong_api_key_is_unauthorised(client: TestClient) -> None:
    response = client.get("/jobs", params={"user_id": "u1"}, headers={"X-API-Key": "nope"})

    assert response.status_code == 401


def test_reorder_request_enqueues_and_returns_the_job_id(client: TestClient) -> None:
    created = _job()
    with patch(f"{_MODULE}.enqueue_job", return_value=created) as enqueue:
        response = client.post(
            "/jobs/reorder",
            json={"user_id": "u1", "tracks": [_TRACK], "start_track_id": "t1"},
            headers=_HEADERS,
        )

    assert response.status_code == 202
    assert response.json() == {"job_id": str(created.id)}
    args = enqueue.call_args.args
    assert args[1] == "u1"
    assert args[2] == JobKind.REORDER
    assert args[3]["start_track_id"] == "t1"
    assert "user_id" not in args[3]


def test_split_request_without_k_is_accepted(client: TestClient) -> None:
    with patch(f"{_MODULE}.enqueue_job", return_value=_job(kind=JobKind.SPLIT)) as enqueue:
        response = client.post(
            "/jobs/split", json={"user_id": "u1", "tracks": [_TRACK]}, headers=_HEADERS
        )

    assert response.status_code == 202
    assert enqueue.call_args.args[3]["k"] is None


def test_split_request_with_zero_k_is_rejected_with_422(client: TestClient) -> None:
    response = client.post(
        "/jobs/split", json={"user_id": "u1", "tracks": [_TRACK], "k": 0}, headers=_HEADERS
    )

    assert response.status_code == 422


def test_recommend_request_enqueues_with_the_candidates(client: TestClient) -> None:
    candidate = {"track_id": "t2", "title": "Karma Police", "artist": "Radiohead"}
    with patch(f"{_MODULE}.enqueue_job", return_value=_job(kind=JobKind.RECOMMEND)) as enqueue:
        response = client.post(
            "/jobs/recommend",
            json={"user_id": "u1", "seeds": [_TRACK], "candidates": [candidate], "tags": ["calm"]},
            headers=_HEADERS,
        )

    assert response.status_code == 202
    payload = enqueue.call_args.args[3]
    assert payload["candidates"][0]["track_id"] == "t2"
    assert payload["tags"] == ["calm"]


def test_get_job_returns_progress(client: TestClient) -> None:
    job = _job()
    with patch(f"{_MODULE}.get_job", return_value=job):
        response = client.get(f"/jobs/{job.id}", headers=_HEADERS)

    body = response.json()
    assert response.status_code == 200
    assert body["job_id"] == str(job.id)
    assert body["status"] == "running"
    assert body["phase"] == "resolving"
    assert (body["done"], body["total"]) == (4, 10)
    assert body["result"] is None


def test_get_unknown_job_is_404(client: TestClient) -> None:
    with patch(f"{_MODULE}.get_job", return_value=None):
        response = client.get(f"/jobs/{uuid.uuid4()}", headers=_HEADERS)

    assert response.status_code == 404


def test_list_jobs_returns_the_users_jobs(client: TestClient) -> None:
    jobs = [_job(), _job(kind=JobKind.SPLIT)]
    with patch(f"{_MODULE}.list_jobs", return_value=jobs):
        response = client.get("/jobs", params={"user_id": "u1"}, headers=_HEADERS)

    assert response.status_code == 200
    assert [item["kind"] for item in response.json()] == ["reorder", "split"]


def test_list_jobs_requires_user_id(client: TestClient) -> None:
    response = client.get("/jobs", headers=_HEADERS)

    assert response.status_code == 422


def test_health_needs_no_api_key(client: TestClient) -> None:
    assert client.get("/health").status_code == 200
