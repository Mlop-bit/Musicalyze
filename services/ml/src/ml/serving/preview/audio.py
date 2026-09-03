import tempfile

import httpx
import librosa
import torch

TARGET_SAMPLE_RATE = 24000
TIMEOUT = 10.0


def fetch_waveform(preview_url: str) -> torch.Tensor:
    response = httpx.get(preview_url, timeout=TIMEOUT, follow_redirects=True)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".mp3") as preview_file:
        preview_file.write(response.content)
        preview_file.flush()
        samples, _ = librosa.load(preview_file.name, sr=TARGET_SAMPLE_RATE, mono=True)

    return torch.from_numpy(samples).unsqueeze(0)
