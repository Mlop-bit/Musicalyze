from ml.serving.playlist.recommend import Recommendation, merge_best_matches


def test_each_track_keeps_its_best_similarity_across_seeds() -> None:
    first = [Recommendation("a", 0.9), Recommendation("b", 0.5)]
    second = [Recommendation("b", 0.8), Recommendation("c", 0.6)]

    merged = merge_best_matches([first, second], limit=10)

    assert merged == [
        Recommendation("a", 0.9),
        Recommendation("b", 0.8),
        Recommendation("c", 0.6),
    ]


def test_the_result_is_cut_to_the_limit() -> None:
    matches = [Recommendation(name, similarity) for name, similarity in (("a", 0.9), ("b", 0.8))]

    assert merge_best_matches([matches], limit=1) == [Recommendation("a", 0.9)]


def test_ties_are_ordered_by_track_id() -> None:
    matches = [Recommendation("b", 0.7), Recommendation("a", 0.7)]

    assert [item.track_id for item in merge_best_matches([matches], limit=2)] == ["a", "b"]


def test_no_seeds_returns_nothing() -> None:
    assert merge_best_matches([], limit=5) == []
