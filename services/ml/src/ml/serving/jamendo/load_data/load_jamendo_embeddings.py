from pathlib import Path

from ml.core.artifact_store import s3_client
from ml.core.config import Settings
from ml.core.muq import load_model
from ml.serving.jamendo.extract_track_embedding import extract_track_embedding
from ml.serving.jamendo.jamendo_dataset import JamendoDataset
from ml.serving.jamendo.upload_jamendo_to_s3 import upload_jamendo_to_s3


def load_jamendo_embeddings(
    train_files_path: str, jamendo_dataset: JamendoDataset, settings: Settings
) -> None:
    model = load_model()
    client = s3_client(settings)

    for track in jamendo_dataset.tracks:
        audio_path = Path(train_files_path) / track["path"].replace(
            ".mp3",
            ".low.mp3",
        )

        embedding = extract_track_embedding(str(audio_path), model)
        upload_jamendo_to_s3(track["track_id"], embedding, client, settings)
