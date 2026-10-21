from ml.serving.classifier.loader import MoodClassifier
from ml.serving.classifier.predict import predict_mood_scores, top_mood_label
from ml.training.classifier import MoodThemeClassifier


def _classifier() -> MoodClassifier:
    model = MoodThemeClassifier(embedding_dim=4, num_tags=3)
    model.eval()
    return MoodClassifier(model=model, labels=("calm", "dark", "happy"))


def test_predict_mood_scores_returns_a_probability_for_every_label() -> None:
    scores = predict_mood_scores(_classifier(), [0.1, 0.2, 0.3, 0.4])

    assert set(scores) == {"calm", "dark", "happy"}
    assert all(0.0 <= value <= 1.0 for value in scores.values())


def test_top_mood_label_returns_the_highest_scoring_label() -> None:
    assert top_mood_label({"calm": 0.2, "dark": 0.7, "happy": 0.1}) == "dark"
