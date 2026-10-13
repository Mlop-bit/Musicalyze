import librosa
import torch

from ml.core.muq import MuQ, embed


def extract_track_embedding(audio_path: str, model: MuQ) -> torch.Tensor:
    total_duration = librosa.get_duration(path=audio_path)
    target_duration = 30.0
    offset = (total_duration - target_duration) / 2.0

    if total_duration < target_duration:
        raise ValueError(
            f"Audio file '{audio_path}' is too short ({total_duration:.2f}s). "
            f"Minimum required duration is {target_duration}s."
        )

    audio_np, _sample_rate = librosa.load(
        audio_path, sr=24000, mono=True, offset=offset, duration=30
    )
    waveform = torch.tensor(audio_np, dtype=torch.float32).unsqueeze(0)

    return embed(model, waveform)


def moods_to_vector(moods: list[str], vocabulary: dict[str, int]) -> torch.Tensor:
    target = torch.zeros(len(vocabulary))

    for mood in moods:
        if mood in vocabulary:
            index = vocabulary[mood]
            target[index] = 1.0

    return target
