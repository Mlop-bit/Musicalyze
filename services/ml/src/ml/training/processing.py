from pathlib import Path

import librosa
import torch
import torch.nn.functional as f

from ml.core.config import Settings
from ml.core.muq import MuQ, embed
from ml.training.s3_storage import download_artifact_from_s3, load_split_data_from_s3
from ml.training.track import Track


def extract_track_embedding(audio_path: str, model: MuQ) -> torch.Tensor:
    total_duration = librosa.get_duration(path=audio_path)
    target_duration = 30.0

    if total_duration >= target_duration:
        offset = (total_duration - target_duration) / 2.0
        audio_np, _sample_rate = librosa.load(
            audio_path, sr=24000, mono=True, offset=offset, duration=30
        )
        waveform = torch.tensor(audio_np, dtype=torch.float32).unsqueeze(0)

    else:
        audio_np, _sample_rate = librosa.load(audio_path, sr=24000, mono=True)
        waveform = torch.tensor(audio_np, dtype=torch.float32).unsqueeze(0)
        target_samples = int(target_duration * 24000)
        current_samples = waveform.shape[-1]

        if current_samples < target_samples:
            padding_needed = target_samples - current_samples
            waveform = f.pad(waveform, (0, padding_needed))

    return embed(model, waveform)


def moods_to_vector(moods: list[str], vocabulary: dict[str, int]) -> torch.Tensor:
    target = torch.zeros(len(vocabulary))

    for mood in moods:
        if mood in vocabulary:
            index = vocabulary[mood]
            target[index] = 1.0

    return target


def create_mood_to_index(tracks: list[Track]) -> dict[str, int]:
    all_moods: set[str] = set()

    for track in tracks:
        all_moods.update(track["moods"])

    mood_to_index = {mood: index for index, mood in enumerate(sorted(all_moods))}

    return mood_to_index


def ensure_data_downloaded(settings: Settings, output_dir: str) -> None:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    vocab_path = out_path / "vocabulary.json"
    train_path = out_path / "train_split.pt"
    valid_path = out_path / "valid_split.pt"
    test_path = out_path / "test_split.pt"

    if not vocab_path.exists():
        download_artifact_from_s3("vocabulary.json", output_dir, settings)

    if not train_path.exists():
        train_embeddings, train_targets = load_split_data_from_s3("train", settings)
        torch.save((train_embeddings, train_targets), train_path)

    if not valid_path.exists():
        valid_embeddings, valid_targets = load_split_data_from_s3("valid", settings)
        torch.save((valid_embeddings, valid_targets), valid_path)

    if not test_path.exists():
        test_embeddings, test_targets = load_split_data_from_s3("test", settings)
        torch.save((test_embeddings, test_targets), test_path)
