from pathlib import Path

from ml.core.config import Settings
from ml.serving.jamendo.extract_track_embedding import extract_track_embedding
from ml.serving.jamendo.jamendo_dataset import JamendoDataset


def load_jamendo_embeddings(
    train_files_path: str, jamendo_dataset: JamendoDataset, settings: Settings
) -> None:

    for track in jamendo_dataset.tracks:
        audio_path = Path(train_files_path) / track["path"].replace(
            ".mp3",
            ".low.mp3",
        )
        embedding = extract_track_embedding(str(audio_path))

        print("Track :", track["track_id"])
        print("Audio :", audio_path)
        print("Embedding :", embedding.shape)
