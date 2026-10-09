import csv
from pathlib import Path

from ml.core.artifact_store import s3_client
from ml.core.config import Settings
from ml.core.muq import load_model
from ml.serving.jamendo.jamendo_dataset import JamendoDataset
from ml.serving.jamendo.processing import extract_track_embedding
from ml.serving.jamendo.s3_storage import upload_jamendo_to_s3
from ml.serving.jamendo.track import Track


def load_jamendo(
    settings: Settings,
    moodtheme_train_file_path: str,
    moodtheme_file_path: str,
    train_files_path: str,
) -> JamendoDataset:
    # Load dataset
    tracks_moods = load_autotagging_moodtheme(moodtheme_file_path)
    mood_to_index = create_mood_to_index(tracks_moods)
    train_tracks = load_autotagging_moodtheme(moodtheme_train_file_path)
    jamendo_dataset = JamendoDataset(train_tracks, mood_to_index, settings)

    load_jamendo_embeddings(train_files_path, jamendo_dataset, settings)

    return jamendo_dataset


def load_autotagging_moodtheme(input_file: str) -> list[Track]:
    tracks: list[Track] = []

    with open(input_file, encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            tags = row["TAGS"].split("\t")

            mood_tags = [
                tag.replace("mood/theme---", "") for tag in tags if tag.startswith("mood/theme---")
            ]

            track: Track = {
                "track_id": row["TRACK_ID"],
                "path": row["PATH"],
                "moods": mood_tags,
            }

            tracks.append(track)

    return tracks


def create_mood_to_index(tracks: list[Track]) -> dict[str, int]:
    all_moods: set[str] = set()

    for track in tracks:
        all_moods.update(track["moods"])

    mood_to_index = {mood: index for index, mood in enumerate(sorted(all_moods))}

    return mood_to_index


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
