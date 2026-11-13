from ml.serving.playlist.energy import energy_score


def test_returns_none_without_tag_scores() -> None:
    assert energy_score(None) is None
    assert energy_score({}) is None


def test_high_energy_tags_raise_the_score_and_low_energy_tags_lower_it() -> None:
    assert energy_score({"energetic": 0.5, "calm": 0.2, "love": 0.9}) == 0.3
    assert energy_score({"calm": 0.4, "sad": 0.1}) == -0.5


def test_unrelated_tags_do_not_change_the_score() -> None:
    assert energy_score({"love": 0.9, "film": 0.4}) == 0.0
