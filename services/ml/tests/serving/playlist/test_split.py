import numpy as np
from numpy.typing import NDArray

from ml.serving.playlist.split import (
    MIN_TRACKS_FOR_SPLIT,
    recommended_k,
    split_tracks,
)

_DIM = 16
_TAGS = ("calm", "dark", "happy")


def _blobs(blob_count: int, per_blob: int) -> NDArray[np.float32]:
    rng = np.random.default_rng(0)
    rows = np.zeros((blob_count * per_blob, _DIM), dtype=np.float32)
    for blob in range(blob_count):
        for member in range(per_blob):
            row = rng.normal(scale=0.02, size=_DIM)
            row[blob] += 1.0
            rows[blob * per_blob + member] = row
    return rows


def _scores(blob_count: int, per_blob: int) -> list[dict[str, float]]:
    scores: list[dict[str, float]] = []
    for blob in range(blob_count):
        for _ in range(per_blob):
            scores.append({tag: (0.9 if index == blob else 0.1) for index, tag in enumerate(_TAGS)})
    return scores


def _ids(count: int) -> list[str]:
    return [f"t{index}" for index in range(count)]


def test_recommended_k_finds_three_blobs() -> None:
    assert recommended_k(_blobs(3, 5)) == 3


def test_recommended_k_is_one_below_the_minimum_track_count() -> None:
    assert recommended_k(_blobs(1, MIN_TRACKS_FOR_SPLIT - 1)) == 1


def test_recommended_k_is_at_least_three_when_there_are_enough_tracks() -> None:
    assert recommended_k(_blobs(2, 5)) == 3


def test_recommended_k_can_be_two_for_a_small_playlist() -> None:
    assert recommended_k(_blobs(2, 3)) == 2


def test_split_with_given_k_returns_that_many_clusters() -> None:
    clusters = split_tracks(_ids(15), _blobs(3, 5), _scores(3, 5), k=3)

    assert len(clusters) == 3
    assert sorted(len(cluster.track_ids) for cluster in clusters) == [5, 5, 5]


def test_split_without_k_uses_the_recommended_k() -> None:
    clusters = split_tracks(_ids(15), _blobs(3, 5), _scores(3, 5), k=None)

    assert len(clusters) == 3


def test_k_larger_than_track_count_is_clamped() -> None:
    clusters = split_tracks(_ids(3), _blobs(3, 1), _scores(3, 1), k=10)

    assert len(clusters) == 3


def test_clusters_are_named_by_the_top_mean_tag() -> None:
    clusters = split_tracks(_ids(15), _blobs(3, 5), _scores(3, 5), k=3)

    names_by_members = {tuple(cluster.track_ids): cluster.name for cluster in clusters}
    assert names_by_members[("t0", "t1", "t2", "t3", "t4")] == "calm"
    assert names_by_members[("t5", "t6", "t7", "t8", "t9")] == "dark"
    assert names_by_members[("t10", "t11", "t12", "t13", "t14")] == "happy"


def test_duplicate_names_take_the_next_best_tag() -> None:
    first = {"calm": 0.9, "dark": 0.5}
    second = {"calm": 0.8, "dark": 0.6}
    scores = [first] * 4 + [second] * 3

    clusters = split_tracks(_ids(7), _blobs(2, 4)[:7], scores, k=2)

    assert [cluster.name for cluster in clusters] == ["calm", "dark"]


def test_cluster_without_tag_scores_gets_a_numbered_name() -> None:
    clusters = split_tracks(_ids(2), _blobs(2, 1), [{}, {}], k=2)

    assert sorted(cluster.name for cluster in clusters) == ["Cluster 1", "Cluster 2"]


def test_no_tracks_returns_no_clusters() -> None:
    assert split_tracks([], np.zeros((0, _DIM), dtype=np.float32), [], k=None) == []


def test_single_track_returns_one_cluster() -> None:
    clusters = split_tracks(["a"], _blobs(1, 1), [{"calm": 0.7, "dark": 0.2}], k=None)

    assert len(clusters) == 1
    assert clusters[0].name == "calm"
    assert clusters[0].track_ids == ["a"]


def test_every_track_is_in_exactly_one_cluster() -> None:
    track_ids = _ids(15)

    clusters = split_tracks(track_ids, _blobs(3, 5), _scores(3, 5), k=3)

    members = [track_id for cluster in clusters for track_id in cluster.track_ids]
    assert sorted(members) == sorted(track_ids)


def test_tag_scores_separate_tracks_that_the_embeddings_do_not() -> None:
    rng = np.random.default_rng(1)
    embeddings = rng.normal(size=(12, _DIM)).astype(np.float32)
    scores = [
        {"calm": 0.9, "dark": 0.05} if index < 6 else {"calm": 0.05, "dark": 0.9}
        for index in range(12)
    ]

    clusters = split_tracks(_ids(12), embeddings, scores, k=2)

    members = {frozenset(cluster.track_ids) for cluster in clusters}
    assert members == {frozenset(_ids(12)[:6]), frozenset(_ids(12)[6:])}


def test_incomplete_tag_scores_fall_back_to_the_embeddings() -> None:
    scores: list[dict[str, float]] = [{} for _ in range(15)]

    clusters = split_tracks(_ids(15), _blobs(3, 5), scores, k=3)

    assert sorted(len(cluster.track_ids) for cluster in clusters) == [5, 5, 5]
