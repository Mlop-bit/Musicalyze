import torch
from torch.utils.data import Dataset

from ml.core.config import Settings


class JamendoDataset(Dataset[tuple[torch.Tensor, torch.Tensor]]):
    def __init__(
        self, track_records: list[dict[str, torch.Tensor | str]], settings: Settings
    ) -> None:
        self.track_records = track_records
        self.settings = settings

    def __len__(self) -> int:
        return len(self.track_records)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        record = self.track_records[index]

        embedding = record["embedding"]
        target = record["target"]

        assert isinstance(embedding, torch.Tensor)
        assert isinstance(target, torch.Tensor)

        return embedding, target
