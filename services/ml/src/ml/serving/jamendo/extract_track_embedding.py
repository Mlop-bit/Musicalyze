import librosa
import torch
from ml.core.muq import embed, load_model

def extract_track_embedding(audio_path_or_url: str) -> torch.Tensor:
    model = load_model()
    audio_np, sample_rate = librosa.load(audio_path_or_url, sr=None)
    waveform = torch.from_numpy(audio_np).unsqueeze(0)

    return embed(model, waveform)