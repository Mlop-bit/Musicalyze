import torch
from sqlalchemy.orm import Session

from ml.core.muq import embed, load_model
from ml.serving.feature_store.repository import save_embedding


def save_track_embedding(session: Session, track_id: str, waveform: torch.Tensor) -> None:
    model = load_model()
    embedding = embed(model, waveform)
    save_embedding(session, track_id, embedding.squeeze(0).tolist())
