CAMELOT_WHEEL_SIZE = 12
MAX_CAMELOT_STEPS = CAMELOT_WHEEL_SIZE // 2

_MAJOR_NUMBERS: dict[str, int] = {
    "B": 1,
    "F#": 2,
    "Gb": 2,
    "C#": 3,
    "Db": 3,
    "G#": 4,
    "Ab": 4,
    "D#": 5,
    "Eb": 5,
    "A#": 6,
    "Bb": 6,
    "F": 7,
    "C": 8,
    "G": 9,
    "D": 10,
    "A": 11,
    "E": 12,
}

_MINOR_NUMBERS: dict[str, int] = {
    "G#": 1,
    "Ab": 1,
    "D#": 2,
    "Eb": 2,
    "A#": 3,
    "Bb": 3,
    "F": 4,
    "C": 5,
    "G": 6,
    "D": 7,
    "A": 8,
    "E": 9,
    "B": 10,
    "F#": 11,
    "Gb": 11,
    "C#": 12,
    "Db": 12,
}

_CAMELOT_NUMBERS: dict[str, int] = {
    **{f"{note} major": number for note, number in _MAJOR_NUMBERS.items()},
    **{f"{note} minor": number for note, number in _MINOR_NUMBERS.items()},
}


def camelot_distance(first: str, second: str) -> float:
    first_number = _CAMELOT_NUMBERS.get(first)
    second_number = _CAMELOT_NUMBERS.get(second)
    if first_number is None or second_number is None:
        return 1.0
    steps = abs(first_number - second_number)
    return min(steps, CAMELOT_WHEEL_SIZE - steps) / MAX_CAMELOT_STEPS


def bpm_distance(first: float, second: float) -> float:
    return min(abs(first - second) / max(first, second), 1.0)
