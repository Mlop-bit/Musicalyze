import tempfile
from pathlib import Path

from ml.core.artifact_store import download_model
from ml.core.config import Settings


def download_jamendo_from_s3(track_id: str, settings: Settings) -> Path:
    s3_key = f"jamendo/embeddings/{track_id}.pt"

    with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as tmp_file:
        file_path = Path(tmp_file.name)

    download_model(s3_key, file_path, settings)

    return file_path
