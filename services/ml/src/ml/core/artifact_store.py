from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import boto3
from botocore.config import Config

from ml.core.config import Settings

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client


def s3_client(settings: Settings) -> S3Client:
    return boto3.client(
        "s3",
        endpoint_url=str(settings.s3_endpoint_url),
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key.get_secret_value(),
        config=Config(
            s3={"addressing_style": "path"},
            retries={"mode": "standard"},
            connect_timeout=10,
            read_timeout=120,
        ),
    )


def upload_model(local_path: Path, key: str, settings: Settings) -> None:
    s3_client(settings).upload_file(str(local_path), settings.s3_bucket, key)


def download_model(key: str, local_path: Path, settings: Settings) -> None:
    s3_client(settings).download_file(settings.s3_bucket, key, str(local_path))
