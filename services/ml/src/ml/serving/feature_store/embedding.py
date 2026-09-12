import torch
from sqlalchemy.orm import Session

from ml.core.muq import embed, load_model
from ml.serving.feature_store.repository import save_embedding
from ml.serving.preview.audio import fetch_waveform


def save_track_embedding(
    session: Session, track_id: str, waveform: torch.Tensor, duration_sec: int | None = None
) -> None:
    model = load_model()
    embedding = embed(model, waveform)
    save_embedding(session, track_id, embedding.squeeze(0).tolist(), duration_sec=duration_sec)


def save_track_embedding_from_preview(
    session: Session, track_id: str, preview_url: str, duration_sec: int | None = None
) -> None:
    waveform = fetch_waveform(preview_url)
    save_track_embedding(session, track_id, waveform, duration_sec=duration_sec)
