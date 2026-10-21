from unittest.mock import MagicMock, patch

import torch

from ml.core.muq import embed, load_model


def test_embed_mean_pools_hidden_state_over_time() -> None:
    fake_output = MagicMock()
    fake_output.last_hidden_state = torch.arange(24, dtype=torch.float32).reshape(1, 4, 6)
    fake_model = MagicMock(return_value=fake_output)
    fake_model.parameters.return_value = iter([torch.zeros(1)])

    result = embed(fake_model, torch.zeros(1, 24000))

    expected = fake_output.last_hidden_state.mean(dim=1)
    assert torch.equal(result, expected)
    assert result.shape == (1, 6)


def test_embed_calls_model_with_output_hidden_states_true() -> None:
    fake_output = MagicMock()
    fake_output.last_hidden_state = torch.zeros(1, 4, 6)
    fake_model = MagicMock(return_value=fake_output)
    fake_model.parameters.return_value = iter([torch.zeros(1)])
    waveform = torch.zeros(1, 24000)

    embed(fake_model, waveform)

    fake_model.assert_called_once_with(waveform, output_hidden_states=True)


def test_load_model_builds_the_checkpoint_directly_on_the_resolved_device() -> None:
    load_model.cache_clear()
    fake_model = MagicMock()
    fake_model.eval.return_value = fake_model
    default_devices: list[str] = []

    def record_default_device(checkpoint: str) -> MagicMock:
        default_devices.append(torch.get_default_device().type)
        return fake_model

    with (
        patch("ml.core.muq.MuQ") as mock_muq_cls,
        patch("ml.core.muq.resolve_device", return_value="meta"),
    ):
        mock_muq_cls.from_pretrained.side_effect = record_default_device

        result = load_model()

        mock_muq_cls.from_pretrained.assert_called_once_with("OpenMuQ/MuQ-large-msd-iter")
        assert default_devices == ["meta"]
        fake_model.eval.assert_called_once()
        assert result is fake_model

    load_model.cache_clear()


def test_load_model_is_cached_across_calls() -> None:
    load_model.cache_clear()
    fake_model = MagicMock()
    fake_model.to.return_value = fake_model
    fake_model.eval.return_value = fake_model

    with (
        patch("ml.core.muq.MuQ") as mock_muq_cls,
        patch("ml.core.muq.resolve_device", return_value="cpu"),
    ):
        mock_muq_cls.from_pretrained.return_value = fake_model

        first = load_model()
        second = load_model()

        mock_muq_cls.from_pretrained.assert_called_once_with("OpenMuQ/MuQ-large-msd-iter")
        assert first is second

    load_model.cache_clear()
