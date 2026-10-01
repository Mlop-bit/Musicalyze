import librosa
import torch

from ml.core.muq import embed, load_model


def extract_track_embedding(audio_path_or_url: str) -> torch.Tensor:
    model = load_model()
    audio_np, _sample_rate = librosa.load(audio_path_or_url, sr=None)
    waveform = torch.tensor(audio_np, dtype=torch.float32).unsqueeze(0)

    return embed(model, waveform)
