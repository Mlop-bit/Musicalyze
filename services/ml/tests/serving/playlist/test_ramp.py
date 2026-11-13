from ml.serving.playlist.ramp import ramp_tracks


def test_orders_from_calm_to_energetic() -> None:
    assert ramp_tracks(["a", "b", "c"], [0.5, -0.4, 0.1]) == ["b", "c", "a"]


def test_descending_orders_from_energetic_to_calm() -> None:
    assert ramp_tracks(["a", "b", "c"], [0.5, -0.4, 0.1], descending=True) == ["a", "c", "b"]


def test_tracks_without_energy_sit_at_the_median() -> None:
    assert ramp_tracks(["a", "b", "c"], [0.8, None, -0.8]) == ["c", "b", "a"]


def test_all_unknown_energies_keep_the_original_order() -> None:
    assert ramp_tracks(["a", "b", "c"], [None, None, None]) == ["a", "b", "c"]


def test_empty_input_returns_an_empty_order() -> None:
    assert ramp_tracks([], []) == []
