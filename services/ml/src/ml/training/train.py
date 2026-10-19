import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import average_precision_score, roc_auc_score
from torch.nn import BCEWithLogitsLoss
from torch.optim import AdamW
from torch.utils.data import DataLoader

from ml.core.config import Settings
from ml.core.device import resolve_device
from ml.training.classifier import MoodThemeClassifier
from ml.training.experiment_log import create_writer
from ml.training.jamendo_dataset import JamendoDataset
from ml.training.processing import ensure_data_downloaded
from ml.training.s3_storage import upload_artifact_to_s3


def train_jamendo(
    settings: Settings,
    output_dir: str,
    epochs: int = 20,
    batch_size: int = 32,
    lr: float = 1e-3,
    patience: int = 5,
) -> None:
    device = resolve_device()
    writer = create_writer("mood_classifier_run")

    output_path = Path(output_dir)
    ensure_data_downloaded(settings, output_dir)

    with open(output_path / "vocabulary.json", encoding="utf-8") as f:
        vocabulary = json.load(f)
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

    best_val_loss = float("inf")
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
        all_preds = []
        all_targets = []

        with torch.no_grad():
            for embeddings, targets in valid_loader:
                embeddings = embeddings.to(device)
                targets = targets.to(device)

                logits = model(embeddings)
                loss = criterion(logits, targets)
                valid_loss += loss.item()

                preds = torch.sigmoid(logits).cpu().numpy()
                all_preds.append(preds)
                all_targets.append(targets.cpu().numpy())

        avg_valid_loss = valid_loss / len(valid_loader)
        writer.add_scalar("loss/valid", avg_valid_loss, epoch)
        all_preds = np.vstack(all_preds)
        all_targets = np.vstack(all_targets)

        val_roc_auc = None
        val_pr_auc = None
        try:
            val_roc_auc = roc_auc_score(all_targets, all_preds, average="macro")
            val_pr_auc = average_precision_score(all_targets, all_preds, average="macro")

            writer.add_scalar("metrics/roc_auc", val_roc_auc, epoch)
            writer.add_scalar("metrics/pr_auc", val_pr_auc, epoch)
        except ValueError:
            pass

        if avg_valid_loss < best_val_loss:
            best_val_loss = avg_valid_loss
            best_val_roc_auc = val_roc_auc
            best_val_pr_auc = val_pr_auc
            patience_counter = 0

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
                    "best_val_loss": best_val_loss,
                    "roc_auc": best_val_roc_auc,
                    "pr_auc": best_val_pr_auc,
                },
            }
            torch.save(checkpoint, output_path / "best_model_checkpoint.pt")
            upload_artifact_to_s3("best_model_checkpoint.pt", output_dir, settings)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print("Early stopping triggered.")
                break

    writer.close()
