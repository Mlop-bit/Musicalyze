from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.serving.classifier.loader import load_mood_classifier
from ml.serving.classifier.predict import predict_mood_scores, top_mood_label
from ml.serving.feature_store.repository import (
    get_track_features,
    save_classifier_mood,
    save_tag_scores,
)


def save_classifier_mood_for_track(session: Session, settings: Settings, track_id: str) -> None:
    features = get_track_features(session, track_id)
    if features is None:
        return
    needs_mood_label = features.mood_label is None
    needs_tag_scores = features.tag_scores is None
    if not needs_mood_label and not needs_tag_scores:
        return
    classifier = load_mood_classifier(settings)
    scores = predict_mood_scores(classifier, list(features.embedding))
    if needs_tag_scores:
        save_tag_scores(session, track_id, scores)
    if needs_mood_label:
        save_classifier_mood(session, track_id, scores, top_mood_label(scores))
