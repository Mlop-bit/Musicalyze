import torch

from ml.serving.classifier.loader import MoodClassifier


def predict_mood_scores(classifier: MoodClassifier, embedding: list[float]) -> dict[str, float]:
    with torch.no_grad():
        logits = classifier.model(torch.tensor([embedding], dtype=torch.float32))
        probabilities = [float(value) for value in torch.sigmoid(logits).squeeze(0)]
    return dict(zip(classifier.labels, probabilities, strict=True))


def top_mood_label(mood_scores: dict[str, float]) -> str:
    return max(mood_scores.items(), key=lambda item: item[1])[0]
