import numpy as np
import numpy.typing as npt
import pytest

from ml.training.metrics import pr_auc, roc_auc


def make_arrays() -> tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]]:
    targets = np.array(
        [[1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 0]],
        dtype=np.float32,
    )
    scores = np.array(
        [[0.9, 0.1, 0.5], [0.2, 0.8, 0.4], [0.7, 0.9, 0.3], [0.1, 0.2, 0.6]],
        dtype=np.float32,
    )
    return targets, scores


def test_metrics_ignore_tags_without_positives() -> None:
    targets, scores = make_arrays()

    assert roc_auc(targets, scores) == pytest.approx(1.0)
    assert pr_auc(targets, scores) == pytest.approx(1.0)


def test_metrics_warn_about_excluded_tags(caplog: pytest.LogCaptureFixture) -> None:
    targets, scores = make_arrays()

    with caplog.at_level("WARNING"):
        roc_auc(targets, scores)

    assert "1 of 3 tags" in caplog.text


def test_metrics_raise_when_no_tag_is_scorable() -> None:
    targets = np.zeros((4, 2), dtype=np.float32)
    scores = np.full((4, 2), 0.5, dtype=np.float32)

    with pytest.raises(ValueError):
        roc_auc(targets, scores)
