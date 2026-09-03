from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import torch

from ml.serving.preview.audio import TARGET_SAMPLE_RATE, fetch_waveform


def test_fetch_waveform_downloads_and_decodes_the_preview() -> None:
    fake_response = MagicMock()
    fake_response.content = b"fake mp3 bytes"
    fake_samples = np.array([0.0, 0.5, -0.5], dtype=np.float32)
    written_paths: list[str] = []

    def _fake_load(path: str, sr: int, mono: bool) -> tuple[np.ndarray, int]:
        assert Path(path).read_bytes() == b"fake mp3 bytes"
        written_paths.append(path)
        return fake_samples, sr if mono else sr

    with (
        patch("ml.serving.preview.audio.httpx.get", return_value=fake_response) as mock_get,
        patch("ml.serving.preview.audio.librosa.load", side_effect=_fake_load) as mock_load,
    ):
        waveform = fetch_waveform("https://example.com/preview.mp3")

    mock_get.assert_called_once()
    assert mock_get.call_args.args[0] == "https://example.com/preview.mp3"
    fake_response.raise_for_status.assert_called_once()

    assert written_paths[0].endswith(".mp3")
    _, load_kwargs = mock_load.call_args
    assert load_kwargs["sr"] == TARGET_SAMPLE_RATE
    assert load_kwargs["mono"] is True

    assert isinstance(waveform, torch.Tensor)
    assert waveform.shape == (1, 3)
    assert torch.allclose(waveform, torch.tensor([[0.0, 0.5, -0.5]]))
