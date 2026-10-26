from pathlib import Path
from unittest.mock import patch

import pytest
import torch

from ml.core.config import Settings
from ml.serving.classifier.loader import CLASSIFIER_KEY, load_mood_classifier, read_classifier
from ml.training.classifier import MoodThemeClassifier


def _settings(cache_dir: Path) -> Settings:
    return Settings.model_validate(
        {
            "s3_endpoint_url": "https://s3.example.com",
            "s3_region": "garage",
            "s3_bucket": "dev-bucket",
            "s3_access_key": "test-access-key",
            "s3_secret_key": "test-secret-key",
            "kv_account_id": "0" * 32,
            "kv_namespace_id": "1" * 32,
            "kv_api_token": "test-token",
            "db_host": "localhost",
            "db_port": 5432,
            "db_user": "musicalyze",
            "db_password": "musicalyze",
            "db_name": "musicalyze",
            "api_key": "test-api-key",
            "classifier_cache_dir": cache_dir,
        }
    )


@pytest.fixture(autouse=True)
def clear_classifier_cache() -> None:
    read_classifier.cache_clear()


def _write_checkpoint(path: Path) -> None:
    model = MoodThemeClassifier(embedding_dim=4, num_tags=3)
    torch.save(
        {
            "weights": model.state_dict(),
            "vocabulary": {"happy": 2, "calm": 0, "dark": 1},
            "embedding_dim": 4,
            "num_tags": 3,
        },
        path,
    )


def test_load_mood_classifier_orders_labels_by_vocabulary_index(tmp_path: Path) -> None:
    def fake_download(key: str, local_path: Path, settings: Settings) -> None:
        _write_checkpoint(local_path)

    with patch("ml.serving.classifier.loader.download_model", side_effect=fake_download):
        classifier = load_mood_classifier(_settings(tmp_path))

    assert classifier.labels == ("calm", "dark", "happy")
    assert not classifier.model.training


def test_load_mood_classifier_downloads_only_when_not_cached(tmp_path: Path) -> None:
    def fake_download(key: str, local_path: Path, settings: Settings) -> None:
        _write_checkpoint(local_path)

    with patch(
        "ml.serving.classifier.loader.download_model", side_effect=fake_download
    ) as mock_download:
        settings = _settings(tmp_path)
        load_mood_classifier(settings)
        load_mood_classifier(settings)

    mock_download.assert_called_once()
    assert mock_download.call_args.args[0] == CLASSIFIER_KEY
    assert not list(tmp_path.glob("*.tmp"))
