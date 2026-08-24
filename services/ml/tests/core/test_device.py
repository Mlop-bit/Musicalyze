from unittest.mock import patch

from ml.core.device import resolve_device


def test_resolve_device_prefers_cuda_when_available() -> None:
    with patch("torch.cuda.is_available", return_value=True):
        assert resolve_device() == "cuda"


def test_resolve_device_prefers_mps_when_cuda_unavailable() -> None:
    with (
        patch("torch.cuda.is_available", return_value=False),
        patch("torch.backends.mps.is_available", return_value=True),
    ):
        assert resolve_device() == "mps"


def test_resolve_device_falls_back_to_cpu() -> None:
    with (
        patch("torch.cuda.is_available", return_value=False),
        patch("torch.backends.mps.is_available", return_value=False),
    ):
        assert resolve_device() == "cpu"
