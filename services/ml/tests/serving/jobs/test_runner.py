import uuid
from collections.abc import Callable
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np

from ml.core.config import Settings
from ml.serving.jobs.models import Job, JobKind, JobPhase
from ml.serving.jobs.runner import run_job
from ml.serving.jobs.track_resolution import ResolutionOutcome
from ml.serving.playlist.recommend import Recommendation

_MODULE = "ml.serving.jobs.runner"
_DIM = 4


def _descriptor(track_id: str) -> dict[str, str]:
    return {"track_id": track_id, "title": f"title {track_id}", "artist": "artist"}


def _job(kind: JobKind, payload: dict[str, object]) -> Job:
    return Job(id=uuid.uuid4(), user_id="u", kind=kind, payload=payload)


def _features(vector: list[float], tags: dict[str, float] | None = None) -> SimpleNamespace:
    return SimpleNamespace(embedding=vector, bpm=None, key=None, tag_scores=tags)


def _settings(max_new_candidates: int = 150) -> MagicMock:
    settings = MagicMock(spec=Settings)
    settings.max_new_candidates = max_new_candidates
    return settings


def _outcome(
    resolved: list[str], skipped: list[str] | None = None, dropped: int = 0
) -> ResolutionOutcome:
    return ResolutionOutcome(
        resolved_ids=resolved, skipped_ids=skipped or [], dropped_candidates=dropped
    )


def _lookup(
    table: dict[str, SimpleNamespace],
) -> Callable[[object, str], SimpleNamespace | None]:
    def get(session: object, track_id: str) -> SimpleNamespace | None:
        stored = table.get(track_id)
        return None if stored is None else SimpleNamespace(track_id=track_id, **vars(stored))

    return get


def test_reorder_job_returns_the_new_order_and_skipped_tracks() -> None:
    table = {
        "a": _features([1.0, 0.0, 0.0, 0.0]),
        "b": _features([0.0, 1.0, 0.0, 0.0]),
        "c": _features([0.9, 0.1, 0.0, 0.0]),
    }
    job = _job(
        JobKind.REORDER,
        {"tracks": [_descriptor(t) for t in "abcd"], "start_track_id": "a"},
    )

    with (
        patch(f"{_MODULE}.resolve_tracks", return_value=_outcome(["a", "b", "c"], ["d"])),
        patch(f"{_MODULE}.get_track_features", side_effect=_lookup(table)),
        patch(f"{_MODULE}.set_phase"),
        patch(f"{_MODULE}.set_progress"),
    ):
        result = run_job(MagicMock(), _settings(), job)

    assert result == {"order": ["a", "c", "b"], "skipped": ["d"]}


def test_split_job_returns_clusters_and_k() -> None:
    table = {
        "a": _features([1.0, 0.0, 0.0, 0.0], {"calm": 0.9}),
        "b": _features([0.99, 0.01, 0.0, 0.0], {"calm": 0.8}),
        "c": _features([0.0, 1.0, 0.0, 0.0], {"dark": 0.9}),
        "d": _features([0.01, 0.99, 0.0, 0.0], {"dark": 0.7}),
    }
    job = _job(JobKind.SPLIT, {"tracks": [_descriptor(t) for t in "abcd"], "k": 2})

    with (
        patch(f"{_MODULE}.resolve_tracks", return_value=_outcome(list("abcd"))),
        patch(f"{_MODULE}.get_track_features", side_effect=_lookup(table)),
        patch(f"{_MODULE}.set_phase"),
        patch(f"{_MODULE}.set_progress"),
    ):
        result = run_job(MagicMock(), _settings(), job)

    assert result["k"] == 2
    assert {cluster["name"] for cluster in result["clusters"]} == {"calm", "dark"}
    assert result["skipped"] == []


def test_split_job_without_k_uses_the_recommended_k() -> None:
    table = {
        "a": _features([1.0, 0.0, 0.0, 0.0]),
        "b": _features([0.0, 1.0, 0.0, 0.0]),
    }
    job = _job(JobKind.SPLIT, {"tracks": [_descriptor("a"), _descriptor("b")]})

    with (
        patch(f"{_MODULE}.resolve_tracks", return_value=_outcome(["a", "b"])),
        patch(f"{_MODULE}.get_track_features", side_effect=_lookup(table)),
        patch(f"{_MODULE}.set_phase"),
        patch(f"{_MODULE}.set_progress"),
    ):
        result = run_job(MagicMock(), _settings(), job)

    assert result["k"] == 1


def test_recommend_job_excludes_seeds_and_applies_the_cap() -> None:
    table = {"seed": _features([1.0, 0.0, 0.0, 0.0])}
    job = _job(
        JobKind.RECOMMEND,
        {
            "seeds": [_descriptor("seed")],
            "candidates": [_descriptor("x"), _descriptor("y")],
            "tags": ["calm"],
            "limit": 5,
        },
    )
    resolve = MagicMock(side_effect=[_outcome(["seed"]), _outcome(["x"], ["y"], dropped=3)])

    with (
        patch(f"{_MODULE}.resolve_tracks", resolve),
        patch(f"{_MODULE}.get_track_features", side_effect=_lookup(table)),
        patch(f"{_MODULE}.nearest_tracks", return_value=[Recommendation("x", 0.9)]) as nearest,
        patch(f"{_MODULE}.set_phase"),
        patch(f"{_MODULE}.set_progress"),
    ):
        result = run_job(MagicMock(), _settings(max_new_candidates=7), job)

    assert resolve.call_args_list[1].kwargs["new_limit"] == 7
    assert resolve.call_args_list[0].kwargs.get("new_limit") is None
    assert nearest.call_args.args[1] == [[1.0, 0.0, 0.0, 0.0]]
    assert nearest.call_args.kwargs["exclude_ids"] == ["seed"]
    assert nearest.call_args.kwargs["tags"] == ["calm"]
    assert nearest.call_args.kwargs["limit"] == 5
    assert result == {
        "recommendations": [{"track_id": "x", "similarity": 0.9}],
        "skipped": ["y"],
        "dropped_candidates": 3,
    }


def test_recommend_job_with_no_seed_embedding_returns_nothing() -> None:
    job = _job(
        JobKind.RECOMMEND,
        {"seeds": [_descriptor("seed")], "candidates": [], "limit": 5},
    )
    resolve = MagicMock(side_effect=[_outcome([], ["seed"]), _outcome([])])

    with (
        patch(f"{_MODULE}.resolve_tracks", resolve),
        patch(f"{_MODULE}.get_track_features", return_value=None),
        patch(f"{_MODULE}.nearest_tracks") as nearest,
        patch(f"{_MODULE}.set_phase"),
        patch(f"{_MODULE}.set_progress"),
    ):
        result = run_job(MagicMock(), _settings(), job)

    nearest.assert_not_called()
    assert result["recommendations"] == []
    assert result["skipped"] == ["seed"]


def test_job_phase_moves_from_resolving_to_computing() -> None:
    job = _job(JobKind.REORDER, {"tracks": [_descriptor("a")]})
    set_phase = MagicMock()

    with (
        patch(f"{_MODULE}.resolve_tracks", return_value=_outcome(["a"])),
        patch(
            f"{_MODULE}.get_track_features",
            side_effect=_lookup({"a": _features(list(np.ones(_DIM)))}),
        ),
        patch(f"{_MODULE}.set_phase", set_phase),
        patch(f"{_MODULE}.set_progress"),
    ):
        run_job(MagicMock(), _settings(), job)

    assert [call.args[2] for call in set_phase.call_args_list] == [
        JobPhase.RESOLVING,
        JobPhase.COMPUTING,
    ]


def test_resolution_progress_is_written_to_the_job() -> None:
    job = _job(JobKind.REORDER, {"tracks": [_descriptor("a")]})
    set_progress = MagicMock()

    def resolve(
        session: object,
        settings: object,
        tracks: object,
        on_progress: Callable[[int, int], None],
        **kwargs: object,
    ) -> ResolutionOutcome:
        on_progress(1, 1)
        return _outcome(["a"])

    with (
        patch(f"{_MODULE}.resolve_tracks", side_effect=resolve),
        patch(
            f"{_MODULE}.get_track_features",
            side_effect=_lookup({"a": _features(list(np.ones(_DIM)))}),
        ),
        patch(f"{_MODULE}.set_phase"),
        patch(f"{_MODULE}.set_progress", set_progress),
    ):
        run_job(MagicMock(), _settings(), job)

    assert set_progress.call_args.args[2:] == (1, 1)
