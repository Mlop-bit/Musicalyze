import torch


def moods_to_vector(moods: list[str], mood_to_index: dict[str, int]) -> torch.Tensor:
    target = torch.zeros(len(mood_to_index))

    for mood in moods:
        index = mood_to_index[mood]
        target[index] = 1.0

    return target
