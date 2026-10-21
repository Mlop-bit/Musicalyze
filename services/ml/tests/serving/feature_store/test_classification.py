from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from ml.core.config import Settings
from ml.serving.feature_store.classification import save_classifier_mood_for_track


def _features(mood_label: str | None) -> SimpleNamespace:
    return SimpleNamespace(embedding=[0.1, 0.2], mood_label=mood_label)


def test_saves_the_top_label_when_the_track_has_no_mood() -> None:
    session = MagicMock()
    scores = {"calm": 0.2, "dark": 0.8}

    with (
        patch(
            "ml.serving.feature_store.classification.get_track_features",
            return_value=_features(None),
        ),
        patch("ml.serving.feature_store.classification.load_mood_classifier"),
        patch("ml.serving.feature_store.classification.predict_mood_scores", return_value=scores),
        patch("ml.serving.feature_store.classification.save_classifier_mood") as mock_save,
    ):
        save_classifier_mood_for_track(session, MagicMock(spec=Settings), "track-1")

    mock_save.assert_called_once_with(session, "track-1", scores, "dark")


def test_keeps_the_existing_mood_label() -> None:
    with (
        patch(
            "ml.serving.feature_store.classification.get_track_features",
            return_value=_features("happy"),
        ),
        patch("ml.serving.feature_store.classification.load_mood_classifier") as mock_load,
        patch("ml.serving.feature_store.classification.save_classifier_mood") as mock_save,
    ):
        save_classifier_mood_for_track(MagicMock(), MagicMock(spec=Settings), "track-1")

    mock_load.assert_not_called()
    mock_save.assert_not_called()


def test_does_nothing_when_the_track_has_no_row() -> None:
    with (
        patch("ml.serving.feature_store.classification.get_track_features", return_value=None),
        patch("ml.serving.feature_store.classification.save_classifier_mood") as mock_save,
    ):
        save_classifier_mood_for_track(MagicMock(), MagicMock(spec=Settings), "track-1")

    mock_save.assert_not_called()
