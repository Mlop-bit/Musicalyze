import pytest

from ml.serving.playlist.distance import bpm_distance, camelot_distance


def test_camelot_distance_is_zero_for_equal_keys() -> None:
    assert camelot_distance("C major", "C major") == 0.0


def test_camelot_distance_is_zero_for_relative_keys() -> None:
    assert camelot_distance("C major", "A minor") == 0.0


def test_camelot_distance_is_one_for_opposite_keys() -> None:
    assert camelot_distance("C major", "F# major") == 1.0


def test_camelot_distance_counts_steps_around_the_wheel() -> None:
    assert camelot_distance("C major", "G major") == pytest.approx(1 / 6)


def test_camelot_distance_wraps_around_the_wheel() -> None:
    assert camelot_distance("C major", "F major") == pytest.approx(1 / 6)


def test_camelot_distance_is_one_for_an_unknown_key() -> None:
    assert camelot_distance("C major", "not a key") == 1.0


def test_bpm_distance_is_relative() -> None:
    assert bpm_distance(100.0, 120.0) == pytest.approx(20 / 120)


def test_bpm_distance_is_zero_for_equal_tempos() -> None:
    assert bpm_distance(90.0, 90.0) == 0.0
