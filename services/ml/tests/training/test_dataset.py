import pytest

from ml.training.dataset import chunks_for_mode


def test_dev_mode_returns_first_two_chunks() -> None:
    assert chunks_for_mode("dev") == [0, 1]


def test_full_mode_returns_all_hundred_chunks() -> None:
    result = chunks_for_mode("full")

    assert len(result) == 100
    assert result[0] == 0
    assert result[-1] == 99


def test_unknown_mode_raises_value_error() -> None:
    with pytest.raises(ValueError, match="unknown dataset mode"):
        chunks_for_mode("bogus")
