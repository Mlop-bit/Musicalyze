from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from ml.serving.playlist.distance import bpm_distance, camelot_distance
from ml.serving.playlist.vectors import normalise_rows

BPM_WEIGHT = 0.15
KEY_WEIGHT = 0.1
MAX_IMPROVEMENT_PASSES = 50
MIN_GAIN = 1e-9


def reorder_tracks(
    track_ids: list[str],
    embeddings: NDArray[np.float32],
    bpms: list[float | None],
    keys: list[str | None],
    start_index: int = 0,
) -> list[str]:
    if not track_ids:
        return []
    distances = _distance_matrix(embeddings, bpms, keys)
    path = _shorten(distances, _greedy_path(distances, start_index))
    return [track_ids[index] for index in path]


def _distance_matrix(
    embeddings: NDArray[np.float32], bpms: list[float | None], keys: list[str | None]
) -> NDArray[np.float64]:
    normalised = normalise_rows(embeddings).astype(np.float64)
    matrix = 1.0 - normalised @ normalised.T
    matrix += BPM_WEIGHT * _imputed(_pairwise(bpms, bpm_distance))
    matrix += KEY_WEIGHT * _imputed(_pairwise(keys, camelot_distance))
    np.fill_diagonal(matrix, 0.0)
    return matrix


def _pairwise[T](values: list[T | None], metric: Callable[[T, T], float]) -> NDArray[np.float64]:
    count = len(values)
    matrix = np.full((count, count), np.nan)
    for row, first in enumerate(values):
        if first is None:
            continue
        for column, second in enumerate(values):
            if second is not None:
                matrix[row, column] = metric(first, second)
    return matrix


def _imputed(matrix: NDArray[np.float64]) -> NDArray[np.float64]:
    off_diagonal = ~np.isnan(matrix) & ~np.eye(len(matrix), dtype=bool)
    if not off_diagonal.any():
        return np.zeros_like(matrix)
    return np.where(np.isnan(matrix), matrix[off_diagonal].mean(), matrix)


def _greedy_path(distances: NDArray[np.float64], start: int) -> list[int]:
    visited = np.zeros(len(distances), dtype=bool)
    visited[start] = True
    path = [start]
    current = start
    for _ in range(len(distances) - 1):
        current = int(np.argmin(np.where(visited, np.inf, distances[current])))
        visited[current] = True
        path.append(current)
    return path


def _shorten(distances: NDArray[np.float64], path: list[int]) -> list[int]:
    order = np.array(path)
    count = len(order)
    for _ in range(MAX_IMPROVEMENT_PASSES):
        improved = False
        for first in range(1, count - 1):
            last = np.arange(first + 1, count)
            following = order[np.minimum(last + 1, count - 1)]
            has_following = last < count - 1
            removed = distances[order[first - 1], order[first]] + np.where(
                has_following, distances[order[last], following], 0.0
            )
            added = distances[order[first - 1], order[last]] + np.where(
                has_following, distances[order[first], following], 0.0
            )
            gain = removed - added
            best = int(np.argmax(gain))
            if gain[best] > MIN_GAIN:
                end = int(last[best])
                order[first : end + 1] = order[first : end + 1][::-1].copy()
                improved = True
        if not improved:
            break
    return [int(index) for index in order]
