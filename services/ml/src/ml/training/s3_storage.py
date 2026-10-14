import json
import tempfile
from pathlib import Path

import torch

from ml.core.artifact_store import download_model, s3_client, upload_model
from ml.core.config import Settings


def upload_jamendo_to_s3(
    batch_name: str,
    split_name: str,
    payload: dict[str, torch.Tensor],
    settings: Settings,
) -> None:
    with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        torch.save(payload, tmp_path)

    try:
        s3_key = f"jamendo/{split_name}/{batch_name}.pt"
        upload_model(tmp_path, s3_key, settings)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def download_jamendo_from_s3(
    batch_name: str, split_name: str, settings: Settings
) -> dict[str, torch.Tensor]:
    s3_key = f"jamendo/{split_name}/{batch_name}.pt"

    with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as tmp_file:
        file_path = Path(tmp_file.name)

    try:
        download_model(s3_key, file_path, settings)

        payload = torch.load(
            file_path,
            weights_only=True,
        )

        return payload

    finally:
        if file_path.exists():
            file_path.unlink()


def get_existing_batch_from_s3(split_name: str, settings: Settings) -> set[int]:
    completed_indices: set[int] = set()
    client = s3_client(settings)
    prefix = f"jamendo/{split_name}/"

    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=settings.s3_bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj.get("Key")
            if not key:
                continue
            filename = key.split("/")[-1]
            if filename.startswith("batch_") and filename.endswith(".pt"):
                try:
                    idx = int(filename[6:-3])
                    completed_indices.add(idx)
                except ValueError:
                    continue

    return completed_indices


def upload_vocabulary_to_s3(vocabulary: dict[str, int], settings: Settings) -> None:
    with tempfile.NamedTemporaryFile(
        suffix=".json", mode="w", encoding="utf-8", delete=False
    ) as tmp_file:
        json.dump(vocabulary, tmp_file, indent=2)
        tmp_path = Path(tmp_file.name)

    try:
        s3_key = "jamendo/vocabulary.json"
        upload_model(tmp_path, s3_key, settings)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def download_vocabulary_from_s3(settings: Settings) -> dict[str, int]:
    s3_key = "jamendo/vocabulary.json"
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
        file_path = Path(tmp_file.name)

    try:
        download_model(s3_key, file_path, settings)
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    finally:
        if file_path.exists():
            file_path.unlink()


def load_split_data_from_s3(
    split_name: str, settings: Settings
) -> tuple[torch.Tensor, torch.Tensor]:
    batch_indices = sorted(list(get_existing_batch_from_s3(split_name, settings)))
    all_embeddings: list[torch.Tensor] = []
    all_targets: list[torch.Tensor] = []

    for idx in batch_indices:
        batch_name = f"batch_{idx:04d}"
        payload = download_jamendo_from_s3(batch_name, split_name, settings)
        all_embeddings.append(payload["embeddings"])
        all_targets.append(payload["targets"])

    return torch.cat(all_embeddings, dim=0), torch.cat(all_targets, dim=0)
