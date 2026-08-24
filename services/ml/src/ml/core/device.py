from typing import Literal

import torch

Device = Literal["cuda", "mps", "cpu"]


def resolve_device() -> Device:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"
