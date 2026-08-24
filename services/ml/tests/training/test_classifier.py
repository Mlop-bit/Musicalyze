import torch
from torch.nn.functional import binary_cross_entropy_with_logits

from ml.training.classifier import MoodThemeClassifier


def test_forward_produces_one_logit_per_tag() -> None:
    model = MoodThemeClassifier(embedding_dim=1024, num_tags=56)
    batch = torch.zeros(4, 1024)

    output = model(batch)

    assert output.shape == (4, 56)


def test_gradients_flow_through_all_parameters() -> None:
    model = MoodThemeClassifier(embedding_dim=8, num_tags=3)
    batch = torch.randn(2, 8)
    target = torch.zeros(2, 3)

    output = model(batch)
    loss = binary_cross_entropy_with_logits(output, target)
    loss.backward()

    assert all(parameter.grad is not None for parameter in model.parameters())
