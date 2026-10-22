from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from ml.core.config import Settings
from ml.serving.jobs.payloads import TrackDescriptor
from ml.serving.jobs.track_resolution import ResolutionOutcome, resolve_tracks

_MODULE = "ml.serving.jobs.track_resolution"


def _track(track_id: str) -> TrackDescriptor:
    return TrackDescriptor(track_id=track_id, title=f"title {track_id}", artist="artist")


class _Store:
    def __init__(self, stored: set[str], unresolvable: set[str] | None = None) -> None:
        self.stored = stored
        self.unresolvable = unresolvable or set()
        self.resolve_calls: list[str] = []

    def get(self, session: object, track_id: str) -> SimpleNamespace | None:
        return SimpleNamespace(track_id=track_id) if track_id in self.stored else None

    def resolve(self, session: object, settings: object, track_id: str, **kwargs: object) -> None:
        self.resolve_calls.append(track_id)
        if track_id not in self.unresolvable:
            self.stored.add(track_id)


def _run(
    store: _Store,
    tracks: list[TrackDescriptor],
    new_limit: int | None = None,
    progress: list[tuple[int, int]] | None = None,
) -> ResolutionOutcome:
    recorded = progress if progress is not None else []
    with (
        patch(f"{_MODULE}.get_track_features", side_effect=store.get),
        patch(f"{_MODULE}.resolve_track", side_effect=store.resolve),
    ):
        return resolve_tracks(
            MagicMock(),
            MagicMock(spec=Settings),
            tracks,
            lambda done, total: recorded.append((done, total)),
            new_limit=new_limit,
        )


def test_duplicate_tracks_are_resolved_once() -> None:
    store = _Store(set())

    outcome = _run(store, [_track("a"), _track("b"), _track("a")])

    assert store.resolve_calls == ["a", "b"]
    assert outcome.resolved_ids == ["a", "b"]


def test_already_resolved_tracks_are_not_resolved_again() -> None:
    store = _Store({"a"})

    outcome = _run(store, [_track("a"), _track("b")])

    assert store.resolve_calls == ["b"]
    assert outcome.resolved_ids == ["a", "b"]


def test_progress_reports_done_over_total_for_every_track() -> None:
    store = _Store({"a"})
    progress: list[tuple[int, int]] = []

    _run(store, [_track("a"), _track("b"), _track("c")], progress=progress)

    assert progress == [(1, 3), (2, 3), (3, 3)]


def test_new_limit_drops_the_remaining_new_tracks() -> None:
    store = _Store({"a"})
    progress: list[tuple[int, int]] = []

    outcome = _run(
        store,
        [_track("a"), _track("b"), _track("c"), _track("d")],
        new_limit=1,
        progress=progress,
    )

    assert store.resolve_calls == ["b"]
    assert outcome.resolved_ids == ["a", "b"]
    assert outcome.dropped_candidates == 2
    assert progress[-1] == (2, 2)


def test_tracks_without_an_embedding_are_skipped() -> None:
    store = _Store(set(), unresolvable={"b"})

    outcome = _run(store, [_track("a"), _track("b")])

    assert outcome.resolved_ids == ["a"]
    assert outcome.skipped_ids == ["b"]


def test_a_resolve_failure_for_one_track_does_not_stop_the_others() -> None:
    store = _Store(set())

    def failing_resolve(session: object, settings: object, track_id: str, **kwargs: object) -> None:
        if track_id == "a":
            raise RuntimeError("boom")
        store.resolve(session, settings, track_id)

    session = MagicMock()
    with (
        patch(f"{_MODULE}.get_track_features", side_effect=store.get),
        patch(f"{_MODULE}.resolve_track", side_effect=failing_resolve),
    ):
        outcome = resolve_tracks(
            session, MagicMock(spec=Settings), [_track("a"), _track("b")], lambda done, total: None
        )

    assert outcome.resolved_ids == ["b"]
    assert outcome.skipped_ids == ["a"]
    session.rollback.assert_called_once()


def test_each_resolved_track_is_committed() -> None:
    store = _Store(set())
    session = MagicMock()
    with (
        patch(f"{_MODULE}.get_track_features", side_effect=store.get),
        patch(f"{_MODULE}.resolve_track", side_effect=store.resolve),
    ):
        resolve_tracks(
            session, MagicMock(spec=Settings), [_track("a"), _track("b")], lambda done, total: None
        )

    assert session.commit.call_count == 2


def test_negative_new_limit_is_rejected() -> None:
    with pytest.raises(ValueError):
        resolve_tracks(MagicMock(), MagicMock(spec=Settings), [], lambda done, total: None, -1)
