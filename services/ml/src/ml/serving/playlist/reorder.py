import numpy as np
from numpy.typing import NDArray

from ml.serving.playlist.distance import bpm_distance, camelot_distance

BPM_WEIGHT = 0.15
KEY_WEIGHT = 0.1


def reorder_tracks(
    track_ids: list[str],
    embeddings: NDArray[np.float32],
    bpms: list[float | None],
    keys: list[str | None],
    start_index: int = 0,
) -> list[str]:
    if not track_ids:
        return []
    normalised = _normalise(embeddings)
    remaining = list(range(len(track_ids)))
    current = start_index
    remaining.remove(current)
    order = [current]
    while remaining:
        distances = [
            _distance(normalised, bpms, keys, current, candidate) for candidate in remaining
        ]
        current = remaining[int(np.argmin(distances))]
        remaining.remove(current)
        order.append(current)
    return [track_ids[index] for index in order]


def _normalise(embeddings: NDArray[np.float32]) -> NDArray[np.float32]:
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return (embeddings / np.where(norms == 0, 1.0, norms)).astype(np.float32)


def _distance(
    normalised: NDArray[np.float32],
    bpms: list[float | None],
    keys: list[str | None],
    current: int,
    candidate: int,
) -> float:
    distance = 1.0 - float(normalised[current] @ normalised[candidate])
    current_bpm, candidate_bpm = bpms[current], bpms[candidate]
    if current_bpm is not None and candidate_bpm is not None:
        distance += BPM_WEIGHT * bpm_distance(current_bpm, candidate_bpm)
    current_key, candidate_key = keys[current], keys[candidate]
    if current_key is not None and candidate_key is not None:
        distance += KEY_WEIGHT * camelot_distance(current_key, candidate_key)
    return distance
