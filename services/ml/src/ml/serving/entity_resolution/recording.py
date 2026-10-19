from typing import TypedDict


class MusicBrainzRecording(TypedDict):
    mbid: str
    title: str
    artist: str
    relevance: int
