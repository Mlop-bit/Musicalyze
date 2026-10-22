from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from ml.serving.playlist.vectors import normalise_rows

MAX_RECOMMENDED_K = 8
MIN_RECOMMENDED_K = 3
MIN_TRACKS_FOR_SPLIT = 6
MIN_TRACKS_PER_CLUSTER = 3
PROJECTION_DIMENSIONS = 12
PROBABILITY_FLOOR = 1e-4
KMEANS_INITS = 10
KMEANS_SEED = 0


@dataclass(frozen=True)
class Cluster:
    name: str
    track_ids: list[str]


def recommended_k(
    embeddings: NDArray[np.float32], tag_scores: list[dict[str, float]] | None = None
) -> int:
    count = len(embeddings)
    if count < MIN_TRACKS_FOR_SPLIT:
        return 1
    features = _cluster_features(embeddings, tag_scores)
    largest_k = min(MAX_RECOMMENDED_K, count // MIN_TRACKS_PER_CLUSTER)
    best_k = 1
    best_score = -2.0
    for k in range(min(MIN_RECOMMENDED_K, largest_k), largest_k + 1):
        labels = _cluster_labels(features, k)
        if len(set(labels)) < 2:
            continue
        score = float(silhouette_score(features, labels))
        if score > best_score:
            best_k, best_score = k, score
    return best_k


def split_tracks(
    track_ids: list[str],
    embeddings: NDArray[np.float32],
    tag_scores: list[dict[str, float]],
    k: int | None,
) -> list[Cluster]:
    if not track_ids:
        return []
    features = _cluster_features(embeddings, tag_scores)
    chosen_k = recommended_k(embeddings, tag_scores) if k is None else k
    chosen_k = max(1, min(chosen_k, len(track_ids)))
    labels = _cluster_labels(features, chosen_k)
    groups: dict[int, list[int]] = {}
    for index, label in enumerate(labels):
        groups.setdefault(int(label), []).append(index)
    ordered_groups = sorted(groups.values(), key=lambda members: (-len(members), members[0]))
    used_names: set[str] = set()
    clusters: list[Cluster] = []
    for position, members in enumerate(ordered_groups, start=1):
        name = _cluster_name([tag_scores[index] for index in members], used_names, position)
        used_names.add(name)
        clusters.append(Cluster(name=name, track_ids=[track_ids[index] for index in members]))
    return clusters


def _cluster_features(
    embeddings: NDArray[np.float32], tag_scores: list[dict[str, float]] | None
) -> NDArray[np.float32]:
    projected = _projected(embeddings)
    tags = _centred_logits(tag_scores, len(embeddings))
    if tags is None:
        return projected
    return normalise_rows(np.hstack([projected, tags]))


def _projected(embeddings: NDArray[np.float32]) -> NDArray[np.float32]:
    normalised = normalise_rows(embeddings)
    dimensions = min(PROJECTION_DIMENSIONS, len(normalised) - 1, normalised.shape[1])
    if dimensions < 1:
        return normalised
    projected = PCA(n_components=dimensions, random_state=KMEANS_SEED).fit_transform(normalised)
    return normalise_rows(projected.astype(np.float32))


def _centred_logits(
    tag_scores: list[dict[str, float]] | None, count: int
) -> NDArray[np.float32] | None:
    if tag_scores is None or len(tag_scores) != count or count < 2:
        return None
    vocabulary = sorted(tag_scores[0])
    if not vocabulary or any(sorted(scores) != vocabulary for scores in tag_scores):
        return None
    probabilities = np.clip(
        np.array([[scores[tag] for tag in vocabulary] for scores in tag_scores]),
        PROBABILITY_FLOOR,
        1.0 - PROBABILITY_FLOOR,
    )
    logits = np.log(probabilities / (1.0 - probabilities))
    return normalise_rows((logits - logits.mean(axis=0)).astype(np.float32))


def _cluster_labels(normalised: NDArray[np.float32], k: int) -> list[int]:
    if k == 1:
        return [0] * len(normalised)
    model = KMeans(n_clusters=k, n_init=KMEANS_INITS, random_state=KMEANS_SEED)
    return [int(label) for label in model.fit_predict(normalised)]


def _cluster_name(
    member_scores: list[dict[str, float]], used_names: set[str], position: int
) -> str:
    totals: dict[str, float] = {}
    for scores in member_scores:
        for tag, score in scores.items():
            totals[tag] = totals.get(tag, 0.0) + score
    for tag, _ in sorted(totals.items(), key=lambda item: -item[1]):
        if tag not in used_names:
            return tag
    return f"Cluster {position}"
