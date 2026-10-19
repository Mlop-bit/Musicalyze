from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import average_precision_score, roc_auc_score
from torch.nn import BCEWithLogitsLoss
from torch.utils.data import DataLoader

from ml.core.config import Settings
from ml.core.device import resolve_device
from ml.training.classifier import MoodThemeClassifier
from ml.training.jamendo_dataset import JamendoDataset
from ml.training.processing import ensure_data_downloaded
from ml.training.s3_storage import upload_artifact_to_s3


def wrap_up_jamendo(
    settings: Settings,
    output_dir: str,
    batch_size: int = 32,
) -> dict:
    device = resolve_device()
    output_path = Path(output_dir)

    checkpoint_path = output_path / "best_model_checkpoint.pt"
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"No checkpoint found at {checkpoint_path}")

    checkpoint = torch.load(checkpoint_path, map_location=device)
    vocabulary = checkpoint["vocabulary"]
    num_tags = checkpoint["num_tags"]
    embedding_dim = checkpoint["embedding_dim"]

    model = MoodThemeClassifier(embedding_dim=embedding_dim, num_tags=num_tags).to(device)
    model.load_state_dict(checkpoint["weights"])
    model.eval()

    ensure_data_downloaded(settings, output_dir)
    test_embeddings, test_targets = torch.load(output_path / "test_split.pt")
    test_dataset = JamendoDataset(test_embeddings, test_targets)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    criterion = BCEWithLogitsLoss()
    test_loss = 0.0
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for embeddings, targets in test_loader:
            embeddings = embeddings.to(device)
            targets = targets.to(device)

            logits = model(embeddings)
            loss = criterion(logits, targets)
            test_loss += loss.item()

            preds = torch.sigmoid(logits).cpu().numpy()
            all_preds.append(preds)
            all_targets.append(targets.cpu().numpy())

    avg_test_loss = test_loss / len(test_loader)
    all_preds = np.vstack(all_preds)
    all_targets = np.vstack(all_targets)

    test_roc_auc = roc_auc_score(all_targets, all_preds, average="macro")
    test_pr_auc = average_precision_score(all_targets, all_preds, average="macro")

    final_metrics = {
        "test_loss": avg_test_loss,
        "test_roc_auc": test_roc_auc,
        "test_pr_auc": test_pr_auc,
    }

    print(f"Loss    : {avg_test_loss:.4f}")
    print(f"ROC-AUC : {test_roc_auc:.4f}")
    print(f"PR-AUC  : {test_pr_auc:.4f}")

    final_model_path = output_path / "mood_theme_classifier_final.pt"

    final_payload = {
        "weights": model.state_dict(),
        "vocabulary": vocabulary,
        "embedding_dim": embedding_dim,
        "num_tags": num_tags,
        "hyperparameters": checkpoint["hyperparameters"],
        "validation_metrics": checkpoint["validation_metrics"],
        "test_metrics": {
            "test_loss": avg_test_loss,
            "test_roc_auc": test_roc_auc,
            "test_pr_auc": test_pr_auc,
        },
    }

    torch.save(final_payload, final_model_path)
    upload_artifact_to_s3("mood_theme_classifier_final.pt", output_dir, settings)

    return final_metrics
