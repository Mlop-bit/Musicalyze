import csv
import json
from pathlib import Path

import torch

from ml.core.config import Settings
from ml.core.muq import MuQ, load_model
from ml.training.processing import create_mood_to_index, extract_track_embedding, moods_to_vector
from ml.training.s3_storage import (
    get_existing_batch_from_s3,
    upload_jamendo_to_s3,
    upload_vocabulary_to_s3,
)
from ml.training.track import Track


def load_jamendo(
    settings: Settings,
    train_file_path: str,
    valid_file_path: str,
    test_file_path: str,
    moodtheme_file_path: str,
    audio_dir: str,
    output_dir: str,
    batch_size: int,
) -> None:
    output_path = Path(output_dir)

    tracks_moods = load_autotagging_moodtheme(moodtheme_file_path)
    vocabulary = create_mood_to_index(tracks_moods)
    with open(output_path / "vocabulary.json", "w", encoding="utf-8") as f:
        json.dump(vocabulary, f, indent=2)
    upload_vocabulary_to_s3(vocabulary, settings)

    model = load_model()

    process_split(train_file_path, "train", audio_dir, vocabulary, model, batch_size, settings)
    process_split(valid_file_path, "valid", audio_dir, vocabulary, model, batch_size, settings)
    process_split(test_file_path, "test", audio_dir, vocabulary, model, batch_size, settings)


def process_split(
    tsv_path: str,
    split_name: str,
    audio_dir: str,
    vocabulary: dict[str, int],
    model: MuQ,
    batch_size: int,
    settings: Settings,
) -> None:
    tracks = load_autotagging_moodtheme(tsv_path)
    audio_path_base = Path(audio_dir)

    completed_batch_indices = get_existing_batch_from_s3(split_name, settings)

    for batch_index, i in enumerate(range(0, len(tracks), batch_size)):
        if batch_index in completed_batch_indices:
            continue

        chunk_tracks = tracks[i : i + batch_size]
        batch_embeddings: list[torch.Tensor] = []
        batch_targets: list[torch.Tensor] = []

        for track in chunk_tracks:
            audio_file_path = audio_path_base / track["path"].replace(".mp3", ".low.mp3")
            if not audio_file_path.exists():
                continue

            embedding = extract_track_embedding(str(audio_file_path), model)
            target = moods_to_vector(track["moods"], vocabulary)

            batch_embeddings.append(embedding.squeeze(0).cpu())
            batch_targets.append(target)

        if batch_embeddings:
            batch_payload = {
                "embeddings": torch.stack(batch_embeddings),
                "targets": torch.stack(batch_targets),
            }
            upload_jamendo_to_s3(f"batch_{batch_index:04d}", split_name, batch_payload, settings)

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
