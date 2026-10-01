import tempfile
from pathlib import Path

import torch
from ml.core.config import Settings
from ml.core.artifact_store import upload_model


def upload_jamendo_to_s3(
    track_id: str, embedding: torch.Tensor, settings: Settings
) -> None:
    with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        torch.save(embedding, tmp_path)

    try:
        s3_key = f"jamendo/embeddings/{track_id}.pt"
        upload_model(tmp_path, s3_key, settings)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()