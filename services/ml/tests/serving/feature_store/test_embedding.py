from unittest.mock import MagicMock, patch

import torch

from ml.serving.feature_store.embedding import (
    save_track_embedding,
    save_track_embedding_from_preview,
)


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
        save_track_embedding(fake_session, "track-1", waveform, duration_sec=245)

    mock_embed.assert_called_once_with(fake_model, waveform)
    mock_save_embedding.assert_called_once_with(
        fake_session, "track-1", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], duration_sec=245
    )


def test_save_track_embedding_from_preview_fetches_then_saves_the_waveform() -> None:
    fake_session = MagicMock()
    fake_waveform = torch.zeros(1, 24000)

    with (
        patch(
            "ml.serving.feature_store.embedding.fetch_waveform", return_value=fake_waveform
        ) as mock_fetch_waveform,
        patch(
            "ml.serving.feature_store.embedding.save_track_embedding"
        ) as mock_save_track_embedding,
    ):
        save_track_embedding_from_preview(
            fake_session, "track-1", "https://example.com/preview.mp3", duration_sec=245
        )

    mock_fetch_waveform.assert_called_once_with("https://example.com/preview.mp3")
    mock_save_track_embedding.assert_called_once_with(
        fake_session, "track-1", fake_waveform, duration_sec=245
    )
