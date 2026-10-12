import torch
from torch.utils.data import Dataset

from ml.core.config import Settings
from ml.training.processing import moods_to_vector
from ml.training.s3_storage import download_jamendo_from_s3
from ml.training.track import Track


class JamendoDataset(Dataset[tuple[torch.Tensor, torch.Tensor]]):
    def __init__(
        self, tracks: list[Track], mood_to_index: dict[str, int], settings: Settings
    ) -> None:
        self.tracks = tracks
        self.mood_to_index = mood_to_index
        self.settings = settings

    def __len__(self) -> int:
        return len(self.tracks)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        track = self.tracks[index]

        embedding = download_jamendo_from_s3(
            track["track_id"],
            self.settings,
        )

        target = moods_to_vector(
            track["moods"],
            self.mood_to_index,
        )

        return embedding, target
