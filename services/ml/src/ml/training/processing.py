import librosa
import torch

from ml.core.muq import MuQ, embed


def extract_track_embedding(audio_path_or_url: str, model: MuQ) -> torch.Tensor:
    audio_np, _sample_rate = librosa.load(audio_path_or_url, sr=24000, mono=True, duration=30)
    waveform = torch.tensor(audio_np, dtype=torch.float32).unsqueeze(0)

    return embed(model, waveform)


def moods_to_vector(moods: list[str], mood_to_index: dict[str, int]) -> torch.Tensor:
    target = torch.zeros(len(mood_to_index))

    for mood in moods:
        index = mood_to_index[mood]
        target[index] = 1.0

    return target
