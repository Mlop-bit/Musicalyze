import logging
import tempfile
from pathlib import Path

import torch

from ml.core.artifact_store import download_model, s3_client, upload_model
from ml.core.config import Settings

logger = logging.getLogger(__name__)

DOWNLOAD_LOG_INTERVAL = 50


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


def upload_artifact_to_s3(file_name: str, output_dir: str, settings: Settings) -> None:
    path = Path(output_dir) / file_name
    if not path.exists():
        raise FileNotFoundError(f"File not found for upload: {path}")

    try:
        s3_key = f"jamendo/{file_name}"
        upload_model(path, s3_key, settings)
    except Exception as e:
        raise RuntimeError(f"Failed to upload artifact '{file_name}' to S3: {e}") from e


def download_artifact_from_s3(file_name: str, output_dir: str, settings: Settings) -> None:
    out_path = Path(output_dir) / file_name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    s3_key = f"jamendo/{file_name}"

    temporary_path = out_path.with_name(f"{out_path.name}.tmp")

    try:
        download_model(s3_key, temporary_path, settings)
        temporary_path.replace(out_path)
    except Exception as e:
        temporary_path.unlink(missing_ok=True)
        raise RuntimeError(f"Failed to download artifact '{file_name}' from S3: {e}") from e


def load_split_data_from_s3(
    split_name: str, settings: Settings
) -> tuple[torch.Tensor, torch.Tensor]:
    batch_indices = sorted(list(get_existing_batch_from_s3(split_name, settings)))
    if not batch_indices:
        raise ValueError(
            f"No batches found on S3 for split '{split_name}'. "
            f"Make sure process_split has been run successfully."
        )

    logger.info("[%s] downloading %d batches from S3", split_name, len(batch_indices))

    all_embeddings: list[torch.Tensor] = []
    all_targets: list[torch.Tensor] = []

    for position, idx in enumerate(batch_indices, start=1):
        batch_name = f"batch_{idx:04d}"
        payload = download_jamendo_from_s3(batch_name, split_name, settings)
        all_embeddings.append(payload["embeddings"])
        all_targets.append(payload["targets"])
        if position % DOWNLOAD_LOG_INTERVAL == 0 or position == len(batch_indices):
            logger.info("[%s] downloaded %d/%d batches", split_name, position, len(batch_indices))

    return torch.cat(all_embeddings, dim=0), torch.cat(all_targets, dim=0)
