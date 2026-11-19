import torch
from sqlalchemy.orm import Session

from ml.core.muq import embed, load_model
from ml.serving.feature_store.repository import save_audio_estimates, save_embedding
from ml.serving.preview.audio import TARGET_SAMPLE_RATE, fetch_waveform
from ml.serving.preview.audio_features import estimate_tempo_and_key


def save_track_embedding(
    session: Session,
    track_id: str,
    waveform: torch.Tensor,
    duration_sec: int | None = None,
    bpm: float | None = None,
) -> None:
    model = load_model()
    embedding = embed(model, waveform)
    save_embedding(session, track_id, embedding.squeeze(0).tolist(), duration_sec=duration_sec)
    estimate = estimate_tempo_and_key(waveform, TARGET_SAMPLE_RATE)
    save_audio_estimates(session, track_id, bpm if bpm is not None else estimate.bpm, estimate.key)


def save_track_embedding_from_preview(
    session: Session,
    track_id: str,
    preview_url: str,
    duration_sec: int | None = None,
    bpm: float | None = None,
) -> None:
    waveform = fetch_waveform(preview_url)
    save_track_embedding(session, track_id, waveform, duration_sec=duration_sec, bpm=bpm)
