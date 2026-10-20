from pathlib import Path

import pytest
import torch

from ml.training.processing import save_atomically


def test_save_atomically_writes_the_final_file_and_no_temporary_file(tmp_path: Path) -> None:
    path = tmp_path / "train_split.pt"
    payload = (torch.ones(2, 3), torch.zeros(2, 4))

    save_atomically(payload, path)

    embeddings, targets = torch.load(path)
    assert torch.equal(embeddings, payload[0])
    assert torch.equal(targets, payload[1])
    assert [entry.name for entry in tmp_path.iterdir()] == ["train_split.pt"]


def test_save_atomically_leaves_no_final_file_when_saving_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "train_split.pt"

    def failing_save(*_args: object, **_kwargs: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(torch, "save", failing_save)

    with pytest.raises(OSError):
        save_atomically((torch.ones(1, 1), torch.ones(1, 1)), path)

    assert not path.exists()
