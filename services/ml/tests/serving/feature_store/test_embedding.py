from unittest.mock import MagicMock, patch

import torch

from ml.serving.feature_store.embedding import save_track_embedding


def test_save_track_embedding_saves_the_mean_pooled_embedding_as_a_list() -> None:
    fake_session = MagicMock()
    fake_model = MagicMock()
    fake_embedding = torch.arange(6, dtype=torch.float32).reshape(1, 6)
    waveform = torch.zeros(1, 24000)

    with (
        patch("ml.serving.feature_store.embedding.load_model", return_value=fake_model),
        patch(
            "ml.serving.feature_store.embedding.embed", return_value=fake_embedding
        ) as mock_embed,
        patch("ml.serving.feature_store.embedding.save_embedding") as mock_save_embedding,
    ):
        save_track_embedding(fake_session, "track-1", waveform)

    mock_embed.assert_called_once_with(fake_model, waveform)
    mock_save_embedding.assert_called_once_with(
        fake_session, "track-1", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    )
