from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.serving.classifier.loader import load_mood_classifier
from ml.serving.classifier.predict import predict_mood_scores, top_mood_label
from ml.serving.feature_store.repository import get_track_features, save_classifier_mood


def save_classifier_mood_for_track(session: Session, settings: Settings, track_id: str) -> None:
    features = get_track_features(session, track_id)
    if features is None or features.mood_label is not None:
        return
    classifier = load_mood_classifier(settings)
    mood_scores = predict_mood_scores(classifier, list(features.embedding))
    save_classifier_mood(session, track_id, mood_scores, top_mood_label(mood_scores))
