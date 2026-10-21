from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import torch

from ml.core.artifact_store import download_model
from ml.core.config import Settings
from ml.training.classifier import MoodThemeClassifier

CLASSIFIER_KEY = "jamendo/mood_theme_classifier_final.pt"


@dataclass(frozen=True)
class MoodClassifier:
    model: MoodThemeClassifier
    labels: tuple[str, ...]


def load_mood_classifier(settings: Settings) -> MoodClassifier:
    cache_dir = settings.classifier_cache_dir
    local_path = cache_dir / Path(CLASSIFIER_KEY).name
    if not local_path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        partial_path = local_path.with_suffix(".tmp")
        download_model(CLASSIFIER_KEY, partial_path, settings)
        partial_path.replace(local_path)
    return read_classifier(local_path)


@lru_cache(maxsize=1)
def read_classifier(path: Path) -> MoodClassifier:
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    model = MoodThemeClassifier(
        embedding_dim=checkpoint["embedding_dim"], num_tags=checkpoint["num_tags"]
    )
    model.load_state_dict(checkpoint["weights"])
    model.eval()
    vocabulary: dict[str, int] = checkpoint["vocabulary"]
    labels = tuple(label for label, _ in sorted(vocabulary.items(), key=lambda item: item[1]))
    return MoodClassifier(model=model, labels=labels)
