import io

import httpx
import librosa
import torch

TARGET_SAMPLE_RATE = 24000
TIMEOUT = 10.0


def fetch_waveform(preview_url: str) -> torch.Tensor:
    response = httpx.get(preview_url, timeout=TIMEOUT, follow_redirects=True)
    response.raise_for_status()
    samples, _ = librosa.load(io.BytesIO(response.content), sr=TARGET_SAMPLE_RATE, mono=True)
    return torch.from_numpy(samples).unsqueeze(0)
