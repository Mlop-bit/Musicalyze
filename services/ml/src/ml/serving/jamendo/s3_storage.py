import io
import tempfile
from pathlib import Path

import torch
from mypy_boto3_s3 import S3Client

from ml.core.artifact_store import download_model
from ml.core.config import Settings


def upload_jamendo_to_s3(
    track_id: str, embedding: torch.Tensor, client: S3Client, settings: Settings
) -> None:
    buffer = io.BytesIO()
    torch.save(embedding, buffer)
    data = buffer.getvalue()

    client.put_object(
        Bucket=settings.s3_bucket,
        Key=f"jamendo/embeddings/{track_id}.pt",
        Body=data,
    )


def download_jamendo_from_s3(track_id: str, settings: Settings) -> torch.Tensor:
    s3_key = f"jamendo/embeddings/{track_id}.pt"

    with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as tmp_file:
        file_path = Path(tmp_file.name)

    try:
        download_model(s3_key, file_path, settings)

        embedding = torch.load(
            file_path,
            weights_only=True,
        )

        return embedding

    finally:
        if file_path.exists():
            file_path.unlink()
