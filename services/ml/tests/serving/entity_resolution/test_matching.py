import pytest

from ml.serving.entity_resolution.matching import select_recording
from ml.serving.entity_resolution.recording import MusicBrainzRecording


def _recording(mbid: str, title: str, artist: str, relevance: int = 100) -> MusicBrainzRecording:
    return MusicBrainzRecording(mbid=mbid, title=title, artist=artist, relevance=relevance)


def test_select_recording_returns_the_mbid_of_an_exact_match() -> None:
    candidates = [_recording("mbid-1", "Get Lucky", "Daft Punk")]

    assert select_recording(candidates, artist="Daft Punk", title="Get Lucky") == "mbid-1"


def test_select_recording_returns_none_without_candidates() -> None:
    assert select_recording([], artist="Daft Punk", title="Get Lucky") is None


def test_select_recording_ignores_case_accents_and_punctuation() -> None:
    candidates = [_recording("mbid-1", "Déjà Vu!", "BEYONCÉ")]

    assert select_recording(candidates, artist="Beyonce", title="deja vu") == "mbid-1"


@pytest.mark.parametrize(
    ("spotify_title", "recording_title"),
    [
        ("Time (Remastered 2011)", "Time"),
        ("Time - 2011 Remaster", "Time"),
        ("Time [Deluxe Edition]", "Time"),
        ("Time feat. Guest Singer", "Time"),
        ("Time", "Time (feat. Guest Singer)"),
    ],
)
def test_select_recording_ignores_edition_and_featuring_suffixes(
    spotify_title: str, recording_title: str
) -> None:
    candidates = [_recording("mbid-1", recording_title, "Pink Floyd")]

    assert select_recording(candidates, artist="Pink Floyd", title=spotify_title) == "mbid-1"


def test_select_recording_rejects_a_candidate_with_a_different_title() -> None:
    candidates = [_recording("mbid-1", "Around the World", "Daft Punk")]

    assert select_recording(candidates, artist="Daft Punk", title="Get Lucky") is None


def test_select_recording_rejects_a_candidate_by_a_different_artist() -> None:
    candidates = [_recording("mbid-1", "Get Lucky", "Some Cover Band")]

    assert select_recording(candidates, artist="Daft Punk", title="Get Lucky") is None


def test_select_recording_accepts_a_credit_that_lists_additional_artists() -> None:
    candidates = [_recording("mbid-1", "Get Lucky", "Daft Punk feat. Pharrell Williams")]

    assert select_recording(candidates, artist="Daft Punk", title="Get Lucky") == "mbid-1"


def test_select_recording_picks_the_most_relevant_among_duplicates_of_the_same_song() -> None:
    candidates = [
        _recording("single", "Get Lucky", "Daft Punk", relevance=90),
        _recording("album", "Get Lucky", "Daft Punk", relevance=100),
        _recording("radio-edit", "Get Lucky", "Daft Punk", relevance=80),
    ]

    assert select_recording(candidates, artist="Daft Punk", title="Get Lucky") == "album"


def test_select_recording_prefers_the_closer_match_over_a_more_relevant_near_miss() -> None:
    candidates = [
        _recording("near-miss", "Cold Waters", "Major Lazer", relevance=100),
        _recording("exact", "Cold Water", "Major Lazer", relevance=60),
    ]

    assert select_recording(candidates, artist="Major Lazer", title="Cold Water") == "exact"


def test_select_recording_prefers_the_exact_artist_over_a_superset_credit() -> None:
    candidates = [
        _recording("superset", "Hold On", "Wilson Phillips Band", relevance=100),
        _recording("exact", "Hold On", "Wilson Phillips", relevance=70),
    ]

    assert select_recording(candidates, artist="Wilson Phillips", title="Hold On") == "exact"


def test_select_recording_returns_none_when_different_artists_match_equally_well() -> None:
    candidates = [
        _recording("mbid-1", "Hold On", "Wilson Phillips & Chynna"),
        _recording("mbid-2", "Hold On", "Wilson Phillips & Carnie"),
    ]

    assert select_recording(candidates, artist="Wilson Phillips", title="Hold On") is None
