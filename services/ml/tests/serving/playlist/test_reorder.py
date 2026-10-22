import numpy as np
from numpy.typing import NDArray

from ml.serving.playlist.reorder import reorder_tracks

_DIM = 8


def _embeddings(angles: list[float]) -> NDArray[np.float32]:
    rows = np.zeros((len(angles), _DIM), dtype=np.float32)
    for index, angle in enumerate(angles):
        rows[index, 0] = np.cos(angle)
        rows[index, 1] = np.sin(angle)
    return rows


def _no_metadata(count: int) -> tuple[list[float | None], list[str | None]]:
    return [None] * count, [None] * count


def test_orders_points_along_an_arc_from_the_start() -> None:
    bpms, keys = _no_metadata(4)

    order = reorder_tracks(["d", "b", "a", "c"], _embeddings([0.9, 0.3, 0.0, 0.6]), bpms, keys)

    assert order == ["d", "c", "b", "a"]


def test_starts_at_the_requested_index() -> None:
    bpms, keys = _no_metadata(3)

    order = reorder_tracks(["a", "b", "c"], _embeddings([0.0, 0.3, 0.6]), bpms, keys, start_index=1)

    assert order[0] == "b"
    assert sorted(order) == ["a", "b", "c"]


def test_empty_input_returns_nothing() -> None:
    assert reorder_tracks([], np.zeros((0, _DIM), dtype=np.float32), [], []) == []


def test_single_track_is_returned_unchanged() -> None:
    bpms, keys = _no_metadata(1)

    assert reorder_tracks(["a"], _embeddings([0.0]), bpms, keys) == ["a"]


def test_bpm_breaks_a_near_tie() -> None:
    embeddings = _embeddings([0.0, 0.2, -0.2])

    order = reorder_tracks(["start", "slow", "fast"], embeddings, [120.0, 60.0, 118.0], [None] * 3)

    assert order == ["start", "fast", "slow"]


def test_key_breaks_a_near_tie() -> None:
    embeddings = _embeddings([0.0, 0.2, -0.2])
    keys: list[str | None] = ["C major", "F# major", "A minor"]

    order = reorder_tracks(["start", "far", "near"], embeddings, [None] * 3, keys)

    assert order == ["start", "near", "far"]


def test_missing_bpm_or_key_falls_back_to_the_embedding() -> None:
    embeddings = _embeddings([0.0, 0.3, 0.6])

    order = reorder_tracks(
        ["a", "b", "c"], embeddings, [None, 100.0, None], [None, None, "C major"]
    )

    assert order == ["a", "b", "c"]


def test_every_track_appears_exactly_once() -> None:
    rng = np.random.default_rng(0)
    embeddings = rng.normal(size=(20, _DIM)).astype(np.float32)
    track_ids = [f"t{index}" for index in range(20)]
    bpms, keys = _no_metadata(20)

    order = reorder_tracks(track_ids, embeddings, bpms, keys)

    assert sorted(order) == sorted(track_ids)


def test_unknown_tempo_does_not_beat_a_close_known_tempo() -> None:
    embeddings = _embeddings([0.0, 0.2, 0.2, 0.2])

    order = reorder_tracks(
        ["start", "unknown", "close", "far"],
        embeddings,
        [120.0, None, 118.0, 60.0],
        [None] * 4,
    )

    assert order[1] == "close"


def _greedy_length(embeddings: NDArray[np.float32]) -> float:
    normalised = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    distances = 1.0 - normalised @ normalised.T
    remaining = set(range(1, len(embeddings)))
    current, total = 0, 0.0
    while remaining:
        following = min(remaining, key=lambda candidate: distances[current, candidate])
        total += float(distances[current, following])
        remaining.remove(following)
        current = following
    return total


def _path_length(embeddings: NDArray[np.float32], order: list[str]) -> float:
    normalised = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    indices = [int(name) for name in order]
    return float(
        sum(1.0 - normalised[a] @ normalised[b] for a, b in zip(indices, indices[1:], strict=False))
    )


def test_improvement_step_never_lengthens_the_greedy_path() -> None:
    shorter = 0
    for seed in range(10):
        embeddings = np.random.default_rng(seed).normal(size=(25, _DIM)).astype(np.float32)
        track_ids = [str(index) for index in range(25)]
        bpms, keys = _no_metadata(25)

        order = reorder_tracks(track_ids, embeddings, bpms, keys)

        assert order[0] == "0"
        length, greedy = _path_length(embeddings, order), _greedy_length(embeddings)
        assert length <= greedy + 1e-6
        shorter += length < greedy - 1e-6
    assert shorter > 0
