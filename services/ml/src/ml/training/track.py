from typing import TypedDict


class Track(TypedDict):
    track_id: str
    path: str
    moods: list[str]
