import logging
from dataclasses import dataclass

import librosa
import numpy as np
import torch
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
MIN_PLAUSIBLE_BPM = 40.0
MAX_PLAUSIBLE_BPM = 220.0


@dataclass(frozen=True)
class AudioEstimate:
    bpm: float | None
    key: str | None


def _estimate_key(samples: NDArray[np.float32], sample_rate: int) -> str | None:
    chroma = librosa.feature.chroma_cqt(y=samples, sr=sample_rate).mean(axis=1)
    if not np.any(chroma):
        return None
    best_score = -np.inf
    best_key: str | None = None
    for mode, profile in (("major", MAJOR_PROFILE), ("minor", MINOR_PROFILE)):
        for tonic in range(len(NOTE_NAMES)):
            score = float(np.corrcoef(chroma, np.roll(profile, tonic))[0, 1])
            if score > best_score:
                best_score = score
                best_key = f"{NOTE_NAMES[tonic]} {mode}"
    return best_key


def _estimate_bpm(samples: NDArray[np.float32], sample_rate: int) -> float | None:
    onset_envelope: NDArray[np.float32] = librosa.onset.onset_strength(  # type: ignore[no-untyped-call]
        y=samples, sr=sample_rate
    )
    bpm = float(librosa.feature.tempo(onset_envelope=onset_envelope, sr=sample_rate)[0])
    return bpm if MIN_PLAUSIBLE_BPM <= bpm <= MAX_PLAUSIBLE_BPM else None


def estimate_tempo_and_key(waveform: torch.Tensor, sample_rate: int) -> AudioEstimate:
    samples = waveform.squeeze().numpy().astype(np.float32)
    try:
        return AudioEstimate(
            bpm=_estimate_bpm(samples, sample_rate), key=_estimate_key(samples, sample_rate)
        )
    except Exception:
        logger.warning("Tempo and key estimation failed", exc_info=True)
        return AudioEstimate(bpm=None, key=None)
