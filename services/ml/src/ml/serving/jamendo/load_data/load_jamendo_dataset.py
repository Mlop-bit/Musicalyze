import csv

from ml.core.config import Settings
from ml.serving.jamendo.jamendo_dataset import JamendoDataset
from ml.serving.jamendo.track import Track


def load_jamendo_dataset(
    moodtheme_train_file_path: str, moodtheme_file_path: str, settings: Settings
) -> JamendoDataset:
    tracks_moods = load_autotagging_moodtheme(moodtheme_file_path)
    mood_to_index = create_mood_to_index(tracks_moods)

    train_tracks = load_autotagging_moodtheme(moodtheme_train_file_path)

    jamendo_dataset = JamendoDataset(train_tracks, mood_to_index, settings)

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
