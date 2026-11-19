import numpy as np
import torch
from numpy.typing import NDArray

from ml.serving.preview.audio_features import estimate_tempo_and_key

SAMPLE_RATE = 24000
SECONDS = 20


def _as_waveform(samples: NDArray[np.float32]) -> torch.Tensor:
    return torch.tensor(samples.tolist()).unsqueeze(0)


def _chord(frequencies: list[float]) -> torch.Tensor:
    time = np.arange(SAMPLE_RATE * SECONDS, dtype=np.float32) / SAMPLE_RATE
    wave = np.zeros_like(time)
    for frequency in frequencies:
        wave += np.sin(2 * np.pi * frequency * time).astype(np.float32)
    return _as_waveform((wave / len(frequencies)).astype(np.float32))


def _clicks(bpm: float) -> torch.Tensor:
    samples = np.zeros(SAMPLE_RATE * SECONDS, dtype=np.float32)
    step = int(SAMPLE_RATE * 60 / bpm)
    for start in range(0, len(samples) - 200, step):
        samples[start : start + 200] = np.hanning(200)
    return _as_waveform(samples)


def test_detects_a_c_major_triad() -> None:
    estimate = estimate_tempo_and_key(_chord([261.63, 329.63, 392.0]), SAMPLE_RATE)

    assert estimate.key == "C major"


def test_detects_the_tempo_of_a_click_track() -> None:
    estimate = estimate_tempo_and_key(_clicks(120), SAMPLE_RATE)

    assert estimate.bpm is not None
    assert abs(estimate.bpm - 120) < 4


def test_silence_has_no_key_and_does_not_raise() -> None:
    estimate = estimate_tempo_and_key(torch.zeros(1, SAMPLE_RATE * 5), SAMPLE_RATE)

    assert estimate.key is None
