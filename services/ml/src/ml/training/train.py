import json
import logging
from pathlib import Path

import numpy as np
import numpy.typing as npt
import torch
from torch.nn import BCEWithLogitsLoss
from torch.optim import AdamW
from torch.utils.data import DataLoader

from ml.core.config import Settings
from ml.core.device import resolve_device
from ml.core.logging import configure_logging
from ml.training.classifier import MoodThemeClassifier
from ml.training.experiment_log import create_writer
from ml.training.jamendo_dataset import JamendoDataset
from ml.training.metrics import pr_auc, roc_auc
from ml.training.processing import ensure_data_downloaded
from ml.training.s3_storage import upload_artifact_to_s3

logger = logging.getLogger(__name__)


def train_jamendo(
    settings: Settings,
    output_dir: str,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 1e-3,
    patience: int = 8,
) -> None:
    configure_logging()
    device = resolve_device()
    writer = create_writer("mood_classifier_run")

    output_path = Path(output_dir)
    ensure_data_downloaded(settings, output_dir)

    with open(output_path / "vocabulary.json", encoding="utf-8") as f:
        vocabulary: dict[str, int] = json.load(f)
    num_classes = len(vocabulary)
    train_embeddings, train_targets = torch.load(output_path / "train_split.pt")
    valid_embeddings, valid_targets = torch.load(output_path / "valid_split.pt")

    train_dataset = JamendoDataset(train_embeddings, train_targets)
    valid_dataset = JamendoDataset(valid_embeddings, valid_targets)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    valid_loader = DataLoader(valid_dataset, batch_size=batch_size, shuffle=False)

    model = MoodThemeClassifier(embedding_dim=1024, num_tags=num_classes).to(device)
    criterion = BCEWithLogitsLoss()
    optimizer = AdamW(model.parameters(), lr=lr)

    best_selection_score = -1.0
    patience_counter = 0

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0

        for embeddings, targets in train_loader:
            embeddings = embeddings.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            logits = model(embeddings)
            loss = criterion(logits, targets)

            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        avg_train_loss = train_loss / len(train_loader)
        writer.add_scalar("loss/train", avg_train_loss, epoch)

        model.eval()
        valid_loss = 0.0
        all_preds: list[npt.NDArray[np.float32]] = []
        all_targets: list[npt.NDArray[np.float32]] = []

        with torch.no_grad():
            for embeddings, targets in valid_loader:
                embeddings = embeddings.to(device)
                targets = targets.to(device)

                logits = model(embeddings)
                loss = criterion(logits, targets)
                valid_loss += loss.item()

                preds = torch.sigmoid(logits).cpu().numpy().astype(np.float32)
                all_preds.append(preds)
                targets_np = targets.detach().cpu().numpy().astype(np.float32)
                all_targets.append(targets_np)

        avg_valid_loss = valid_loss / len(valid_loader)
        writer.add_scalar("loss/valid", avg_valid_loss, epoch)
        preds_array = np.vstack(all_preds).astype(np.float32)
        targets_array = np.vstack(all_targets).astype(np.float32)

        val_roc_auc: float | None = None
        val_pr_auc: float | None = None
        try:
            val_roc_auc = roc_auc(targets_array, preds_array)
            val_pr_auc = pr_auc(targets_array, preds_array)

            writer.add_scalar("metrics/roc_auc", val_roc_auc, epoch)
            writer.add_scalar("metrics/pr_auc", val_pr_auc, epoch)
        except ValueError:
            logger.warning(
                "epoch %d: ROC-AUC and PR-AUC could not be computed", epoch + 1, exc_info=True
            )

        selection_score = val_pr_auc if val_pr_auc is not None else -1.0
        is_best = selection_score > best_selection_score
        patience_counter = 0 if is_best else patience_counter + 1

        metrics_text = (
            "n/a"
            if val_roc_auc is None or val_pr_auc is None
            else f"roc_auc={val_roc_auc:.4f} pr_auc={val_pr_auc:.4f}"
        )
        logger.info(
            "epoch %d/%d train_loss=%.4f valid_loss=%.4f %s patience=%d/%d",
            epoch + 1,
            epochs,
            avg_train_loss,
            avg_valid_loss,
            metrics_text,
            patience_counter,
            patience,
        )

        if is_best:
            best_selection_score = selection_score

            checkpoint = {
                "weights": model.state_dict(),
                "vocabulary": vocabulary,
                "embedding_dim": 1024,
                "num_tags": num_classes,
                "hyperparameters": {
                    "epochs": epochs,
                    "batch_size": batch_size,
                    "lr": lr,
                    "patience": patience,
                },
                "validation_metrics": {
                    "val_loss": avg_valid_loss,
                    "roc_auc": val_roc_auc,
                    "pr_auc": val_pr_auc,
                },
            }
            torch.save(checkpoint, output_path / "best_model_checkpoint.pt")
            upload_artifact_to_s3("best_model_checkpoint.pt", output_dir, settings)
            logger.info("epoch %d: new best pr_auc, checkpoint saved and uploaded to S3", epoch + 1)
        elif patience_counter >= patience:
            logger.info("early stopping triggered at epoch %d", epoch + 1)
            break

    writer.close()
