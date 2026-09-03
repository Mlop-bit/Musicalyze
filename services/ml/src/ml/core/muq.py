import warnings
from functools import lru_cache

import torch
from muq import MuQ

from ml.core.device import resolve_device

_CHECKPOINT = "OpenMuQ/MuQ-large-msd-iter"


@lru_cache(maxsize=1)
def load_model() -> MuQ:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"`torch\.nn\.utils\.weight_norm` is deprecated",
            category=FutureWarning,
        )
        model = MuQ.from_pretrained(_CHECKPOINT)
    return model.to(resolve_device()).eval()


def embed(model: MuQ, waveform: torch.Tensor) -> torch.Tensor:
    with torch.no_grad():
        output = model(waveform.to(next(model.parameters()).device), output_hidden_states=True)
    return output.last_hidden_state.mean(dim=1)
