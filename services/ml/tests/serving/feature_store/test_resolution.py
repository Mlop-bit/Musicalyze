from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

from ml.core.config import Settings
from ml.serving.feature_store.resolution import resolve_track


def _settings() -> Settings:
    return Settings.model_validate(
        {
            "s3_endpoint_url": "https://s3.example.com",
            "s3_region": "garage",
            "s3_bucket": "dev-bucket",
            "s3_access_key": "test-access-key",
            "s3_secret_key": "test-secret-key",
            "kv_account_id": "0" * 32,
            "kv_namespace_id": "1" * 32,
            "kv_api_token": "test-token",
            "db_host": "localhost",
            "db_port": 5432,
            "db_user": "musicalyze",
            "db_password": "musicalyze",
            "db_name": "musicalyze",
            "api_key": "test-api-key",
        }
    )


def test_resolve_track_saves_embedding_when_a_preview_is_found() -> None:
    fake_session = MagicMock()
    deezer_track = {
        "preview_url": "https://example.com/preview.mp3",
        "duration_sec": 245,
        "bpm": 120.0,
    }

    with (
        patch(
            "ml.serving.feature_store.resolution.search_deezer_track", return_value=deezer_track
        ) as mock_search,
        patch(
            "ml.serving.feature_store.resolution.save_track_embedding_from_preview"
        ) as mock_save_embedding,
        patch(
            "ml.serving.feature_store.resolution.save_acousticbrainz_enrichment"
        ) as mock_save_enrichment,
        patch("ml.serving.feature_store.resolution.resolve_musicbrainz_id", return_value=None),
    ):
        resolve_track(fake_session, _settings(), "track-1", isrc="isrc-1", artist="A", title="T")

    mock_search.assert_called_once_with(
        _settings(), isrc="isrc-1", artist="A", track="T", query=None
    )
    mock_save_embedding.assert_called_once_with(
        fake_session, "track-1", "https://example.com/preview.mp3", duration_sec=245, bpm=120.0
    )
    mock_save_enrichment.assert_not_called()


def test_resolve_track_does_not_raise_when_deezer_lookup_fails() -> None:
    fake_session = MagicMock()
    settings = _settings()

    with (
        patch(
            "ml.serving.feature_store.resolution.search_deezer_track",
            side_effect=ClientError({"Error": {"Code": "500", "Message": "boom"}}, "GetItem"),
        ) as mock_search,
        patch(
            "ml.serving.feature_store.resolution.save_track_embedding_from_preview"
        ) as mock_save_embedding,
        patch("ml.serving.feature_store.resolution.save_acousticbrainz_enrichment"),
    ):
        resolve_track(fake_session, settings, "track-1")

    mock_search.assert_called_once()
    mock_save_embedding.assert_not_called()


def test_resolve_track_does_not_raise_when_embedding_save_fails() -> None:
    fake_session = MagicMock()
    settings = _settings()
    deezer_track = {
        "preview_url": "https://example.com/preview.mp3",
        "duration_sec": 245,
        "bpm": 120.0,
    }

    with (
        patch("ml.serving.feature_store.resolution.search_deezer_track", return_value=deezer_track),
        patch(
            "ml.serving.feature_store.resolution.save_track_embedding_from_preview",
            side_effect=RuntimeError("model download failed"),
        ) as mock_save_embedding,
        patch("ml.serving.feature_store.resolution.save_acousticbrainz_enrichment"),
    ):
        resolve_track(fake_session, settings, "track-1")

    mock_save_embedding.assert_called_once()


def test_resolve_track_skips_embedding_when_no_preview_is_found() -> None:
    fake_session = MagicMock()

    with (
        patch("ml.serving.feature_store.resolution.search_deezer_track", return_value=None),
        patch(
            "ml.serving.feature_store.resolution.save_track_embedding_from_preview"
        ) as mock_save_embedding,
    ):
        resolve_track(fake_session, _settings(), "track-1")

    mock_save_embedding.assert_not_called()


def test_resolve_track_skips_embedding_when_preview_url_is_null() -> None:
    fake_session = MagicMock()

    with (
        patch(
            "ml.serving.feature_store.resolution.search_deezer_track",
            return_value={"preview_url": None, "duration_sec": None},
        ),
        patch(
            "ml.serving.feature_store.resolution.save_track_embedding_from_preview"
        ) as mock_save_embedding,
    ):
        resolve_track(fake_session, _settings(), "track-1")

    mock_save_embedding.assert_not_called()


def test_resolve_track_saves_acousticbrainz_enrichment_when_mbid_is_known() -> None:
    fake_session = MagicMock()
    settings = _settings()

    with (
        patch("ml.serving.feature_store.resolution.search_deezer_track", return_value=None),
        patch(
            "ml.serving.feature_store.resolution.save_acousticbrainz_enrichment"
        ) as mock_save_enrichment,
    ):
        resolve_track(fake_session, settings, "track-1", musicbrainz_id="mbid-1")

    mock_save_enrichment.assert_called_once_with(fake_session, "track-1", "mbid-1", settings)


def test_resolve_track_does_not_raise_when_acousticbrainz_enrichment_fails() -> None:
    fake_session = MagicMock()
    settings = _settings()

    with (
        patch("ml.serving.feature_store.resolution.search_deezer_track", return_value=None),
        patch(
            "ml.serving.feature_store.resolution.save_acousticbrainz_enrichment",
            side_effect=ClientError(
                {"Error": {"Code": "403", "Message": "Forbidden"}}, "HeadObject"
            ),
        ) as mock_save_enrichment,
    ):
        resolve_track(fake_session, settings, "track-1", musicbrainz_id="mbid-1")

    mock_save_enrichment.assert_called_once_with(fake_session, "track-1", "mbid-1", settings)


def test_resolve_track_skips_acousticbrainz_enrichment_without_a_mbid() -> None:
    fake_session = MagicMock()

    with (
        patch("ml.serving.feature_store.resolution.search_deezer_track", return_value=None),
        patch(
            "ml.serving.feature_store.resolution.save_acousticbrainz_enrichment"
        ) as mock_save_enrichment,
    ):
        resolve_track(fake_session, _settings(), "track-1")

    mock_save_enrichment.assert_not_called()


def test_resolve_track_looks_up_the_musicbrainz_id_when_none_is_given() -> None:
    fake_session = MagicMock()
    settings = _settings()

    with (
        patch("ml.serving.feature_store.resolution.search_deezer_track", return_value=None),
        patch(
            "ml.serving.feature_store.resolution.resolve_musicbrainz_id", return_value="mbid-1"
        ) as mock_resolve,
        patch(
            "ml.serving.feature_store.resolution.save_acousticbrainz_enrichment"
        ) as mock_save_enrichment,
    ):
        resolve_track(
            fake_session, settings, "track-1", isrc="isrc-1", artist="Daft Punk", title="Get Lucky"
        )

    mock_resolve.assert_called_once_with(
        settings, isrc="isrc-1", artist="Daft Punk", title="Get Lucky"
    )
    mock_save_enrichment.assert_called_once_with(fake_session, "track-1", "mbid-1", settings)


def test_resolve_track_does_not_look_up_the_musicbrainz_id_when_one_is_given() -> None:
    with (
        patch("ml.serving.feature_store.resolution.search_deezer_track", return_value=None),
        patch("ml.serving.feature_store.resolution.resolve_musicbrainz_id") as mock_resolve,
        patch("ml.serving.feature_store.resolution.save_acousticbrainz_enrichment"),
    ):
        resolve_track(MagicMock(), _settings(), "track-1", musicbrainz_id="mbid-1")

    mock_resolve.assert_not_called()


def test_resolve_track_skips_enrichment_when_the_musicbrainz_id_is_unresolved() -> None:
    with (
        patch("ml.serving.feature_store.resolution.search_deezer_track", return_value=None),
        patch("ml.serving.feature_store.resolution.resolve_musicbrainz_id", return_value=None),
        patch(
            "ml.serving.feature_store.resolution.save_acousticbrainz_enrichment"
        ) as mock_save_enrichment,
    ):
        resolve_track(MagicMock(), _settings(), "track-1", artist="A", title="T")

    mock_save_enrichment.assert_not_called()


def test_resolve_track_does_not_raise_when_the_musicbrainz_lookup_fails() -> None:
    with (
        patch("ml.serving.feature_store.resolution.search_deezer_track", return_value=None),
        patch(
            "ml.serving.feature_store.resolution.resolve_musicbrainz_id",
            side_effect=RuntimeError("musicbrainz unavailable"),
        ),
        patch(
            "ml.serving.feature_store.resolution.save_acousticbrainz_enrichment"
        ) as mock_save_enrichment,
    ):
        resolve_track(MagicMock(), _settings(), "track-1", artist="A", title="T")

    mock_save_enrichment.assert_not_called()
