import csv
import json
from pathlib import Path

from ml.core.config import Settings
from ml.core.muq import MuQ, load_model
from ml.training.processing import extract_track_embedding, moods_to_vector
from ml.training.s3_storage import upload_jamendo_to_s3
from ml.training.track import Track


def load_jamendo(
    settings: Settings,
    train_file_path: str,
    valid_file_path: str,
    test_file_path: str,
    moodtheme_file_path: str,
    audio_dir: str,
    output_dir: str,
) -> None:
    output_path = Path(output_dir)

    tracks_moods = load_autotagging_moodtheme(moodtheme_file_path)
    vocabulary = create_mood_to_index(tracks_moods)
    with open(output_path / "vocabulary.json", "w", encoding="utf-8") as f:
        json.dump(vocabulary, f, indent=2)

    model = load_model()

    process_split(train_file_path, "train", audio_dir, vocabulary, model, settings)
    process_split(valid_file_path, "valid", audio_dir, vocabulary, model, settings)
    process_split(test_file_path, "test", audio_dir, vocabulary, model, settings)


def process_split(
    tsv_path: str,
    split_name: str,
    audio_dir: str,
    vocabulary: dict[str, int],
    model: MuQ,
    settings: Settings,
) -> None:
    tracks = load_autotagging_moodtheme(tsv_path)
    audio_path_base = Path(audio_dir)

    for track in tracks:
        audio_file_path = audio_path_base / track["path"].replace(".mp3", ".low.mp3")
        if not audio_file_path.exists():
            continue

        embedding = extract_track_embedding(str(audio_file_path), model)
        target = moods_to_vector(track["moods"], vocabulary)

        payload = {
            "track_id": track["track_id"],
            "embedding": embedding.squeeze(0).cpu(),
            "target": target,
        }

        upload_jamendo_to_s3(track["track_id"], split_name, payload, settings)


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
                "path": row[3],
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
