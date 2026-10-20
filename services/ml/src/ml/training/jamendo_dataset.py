import torch
from torch.utils.data import Dataset


class JamendoDataset(Dataset[tuple[torch.Tensor, torch.Tensor]]):
    def __init__(self, embeddings: torch.Tensor, targets: torch.Tensor) -> None:
        self.embeddings = embeddings
        self.targets = targets

    def __len__(self) -> int:
        return len(self.embeddings)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.embeddings[index], self.targets[index]
