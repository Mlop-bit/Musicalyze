import json
import tempfile
from pathlib import Path

import torch

from ml.core.artifact_store import download_model, upload_model
from ml.core.config import Settings


def upload_jamendo_to_s3(
    batch_name: str,
    split_name: str,
    payload: dict[str, torch.Tensor | list[str]],
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
) -> dict[str, torch.Tensor | list[str]]:
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
