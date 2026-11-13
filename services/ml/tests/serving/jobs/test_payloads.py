import pytest
from pydantic import ValidationError

from ml.serving.jobs.payloads import (
    RecommendPayload,
    ReorderPayload,
    SplitPayload,
    TrackDescriptor,
)

_TRACK = {"track_id": "t1", "title": "Creep", "artist": "Radiohead"}


def test_track_descriptor_optional_fields_default_to_none() -> None:
    track = TrackDescriptor.model_validate(_TRACK)

    assert track.isrc is None
    assert track.musicbrainz_id is None


def test_track_descriptor_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TrackDescriptor.model_validate({**_TRACK, "popularity": 80})


def test_track_descriptor_rejects_an_empty_track_id() -> None:
    with pytest.raises(ValidationError):
        TrackDescriptor.model_validate({**_TRACK, "track_id": ""})


def test_reorder_payload_start_track_is_optional() -> None:
    payload = ReorderPayload.model_validate({"tracks": [_TRACK]})

    assert payload.start_track_id is None


def test_split_payload_k_is_optional() -> None:
    assert SplitPayload.model_validate({"tracks": [_TRACK]}).k is None


def test_split_payload_rejects_zero_k() -> None:
    with pytest.raises(ValidationError):
        SplitPayload.model_validate({"tracks": [_TRACK], "k": 0})


def test_recommend_payload_defaults() -> None:
    payload = RecommendPayload.model_validate({"seeds": [_TRACK], "candidates": []})

    assert payload.limit == 20
    assert payload.tags is None


def test_recommend_payload_rejects_zero_limit() -> None:
    with pytest.raises(ValidationError):
        RecommendPayload.model_validate({"seeds": [_TRACK], "candidates": [], "limit": 0})


def test_reorder_payload_defaults_to_similarity_and_rejects_unknown_modes() -> None:
    assert ReorderPayload(tracks=[]).mode == "similarity"
    with pytest.raises(ValidationError):
        ReorderPayload.model_validate({"tracks": [], "mode": "random"})
