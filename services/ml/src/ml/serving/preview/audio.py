import tempfile
from pathlib import Path

import httpx
import librosa
import torch

TARGET_SAMPLE_RATE = 24000
TIMEOUT = 10.0


def fetch_waveform(preview_url: str) -> torch.Tensor:
    response = httpx.get(preview_url, timeout=TIMEOUT, follow_redirects=True)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as preview_file:
        preview_file.write(response.content)
    preview_path = Path(preview_file.name)

    try:
        samples, _ = librosa.load(str(preview_path), sr=TARGET_SAMPLE_RATE, mono=True)
    finally:
        preview_path.unlink(missing_ok=True)

    return torch.from_numpy(samples).unsqueeze(0)
