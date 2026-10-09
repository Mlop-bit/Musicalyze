import io

import torch
from mypy_boto3_s3 import S3Client

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
