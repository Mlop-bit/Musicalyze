import csv
from pathlib import Path

from ml.core.config import Settings
from ml.core.muq import load_model
from ml.training.jamendo_dataset import JamendoDataset
from ml.training.processing import extract_track_embedding
from ml.training.s3_storage import upload_jamendo_to_s3
from ml.training.track import Track


def load_jamendo(
    settings: Settings,
    moodtheme_train_file_path: str,
    moodtheme_file_path: str,
    train_files_path: str,
) -> JamendoDataset:
    tracks_moods = load_autotagging_moodtheme(moodtheme_file_path)
    mood_to_index = create_mood_to_index(tracks_moods)
    train_tracks = load_autotagging_moodtheme(moodtheme_train_file_path)
    jamendo_dataset = JamendoDataset(train_tracks, mood_to_index, settings)

    load_jamendo_embeddings(train_files_path, jamendo_dataset, settings)

    return jamendo_dataset


def load_autotagging_moodtheme(input_file: str) -> list[Track]:
    tracks: list[Track] = []

    with open(input_file, encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="\t")

        header = next(reader, None)
        if header is None:
            return tracks

        for row in reader:
            tags = row[5:]

            mood_tags = [
                tag.replace("mood/theme---", "", 1)
                for tag in tags
                if tag.startswith("mood/theme---")
            ]

            track: Track = {
                "track_id": row[0],
                "path": row[1],
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

    for track in jamendo_dataset.tracks:
        audio_path = Path(train_files_path) / track["path"].replace(
            ".mp3",
            ".low.mp3",
        )

        embedding = extract_track_embedding(str(audio_path), model)
        upload_jamendo_to_s3(track["track_id"], embedding, settings)
