import re
import unicodedata
from dataclasses import dataclass

from rapidfuzz import fuzz

from ml.serving.entity_resolution.recording import MusicBrainzRecording

TITLE_MIN_SCORE = 90.0
ARTIST_MIN_SCORE = 85.0
AMBIGUITY_MARGIN = 1.0

_BRACKETED = re.compile(r"\([^)]*\)|\[[^\]]*\]")
_REMASTER_SUFFIX = re.compile(r"\s-\s[^-]*remaster.*$")
_FEATURING = re.compile(r"\b(?:feat|ft|featuring)\b.*$")
_NON_WORD = re.compile(r"[^\w\s]")


@dataclass(frozen=True)
class _ScoredRecording:
    mbid: str
    relevance: int
    normalized_title: str
    normalized_artist: str
    rank_score: float


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    lowered = without_accents.casefold()
    without_brackets = _BRACKETED.sub(" ", lowered)
    without_remaster = _REMASTER_SUFFIX.sub("", without_brackets)
    without_featuring = _FEATURING.sub("", without_remaster)
    words = _NON_WORD.sub(" ", without_featuring).split()
    return " ".join(words)


def select_recording(candidates: list[MusicBrainzRecording], artist: str, title: str) -> str | None:
    normalized_artist = normalize(artist)
    normalized_title = normalize(title)

    scored = [
        scored_recording
        for candidate in candidates
        if (scored_recording := _score(candidate, normalized_artist, normalized_title)) is not None
    ]
    if not scored:
        return None

    scored.sort(key=lambda recording: (recording.rank_score, recording.relevance), reverse=True)
    best = scored[0]
    if any(_is_conflicting(best, other) for other in scored[1:]):
        return None
    return best.mbid


def _score(
    candidate: MusicBrainzRecording, normalized_artist: str, normalized_title: str
) -> _ScoredRecording | None:
    candidate_title = normalize(candidate["title"])
    candidate_artist = normalize(candidate["artist"])

    title_ratio = fuzz.ratio(normalized_title, candidate_title)
    if title_ratio < TITLE_MIN_SCORE:
        return None
    if fuzz.token_set_ratio(normalized_artist, candidate_artist) < ARTIST_MIN_SCORE:
        return None

    artist_ratio = fuzz.ratio(normalized_artist, candidate_artist)
    return _ScoredRecording(
        mbid=candidate["mbid"],
        relevance=candidate["relevance"],
        normalized_title=candidate_title,
        normalized_artist=candidate_artist,
        rank_score=title_ratio + artist_ratio,
    )


def _is_conflicting(best: _ScoredRecording, other: _ScoredRecording) -> bool:
    is_close = best.rank_score - other.rank_score < AMBIGUITY_MARGIN
    is_same_song = (
        best.normalized_title == other.normalized_title
        and best.normalized_artist == other.normalized_artist
    )
    return is_close and not is_same_song
