import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.core.logging import configure_logging
from ml.serving.feature_store.repository import get_track_features
from ml.serving.feature_store.resolution import resolve_track


def main() -> None:
    track_id = sys.argv[1] if len(sys.argv) > 1 else "demo-track"
    artist = sys.argv[2] if len(sys.argv) > 2 else "Radiohead"
    title = sys.argv[3] if len(sys.argv) > 3 else "Creep"
    musicbrainz_id = sys.argv[4] if len(sys.argv) > 4 else None

    configure_logging()
    settings = Settings()
    engine = create_engine(settings.database_url)

    with Session(engine) as session:
        print(f"Resolving '{title}' by {artist} (track_id={track_id})...")
        resolve_track(
            session,
            settings,
            track_id,
            artist=artist,
            title=title,
            musicbrainz_id=musicbrainz_id,
        )
        session.commit()

        row = get_track_features(session, track_id)
        if row is None:
            print("No row was saved (Deezer had no match and no MBID enrichment ran).")
            return

        print("\nSaved feature store row:")
        print(f"  track_id       = {row.track_id}")
        print(f"  musicbrainz_id = {row.musicbrainz_id}")
        embedding_len = len(row.embedding) if row.embedding is not None else None
        print(f"  embedding      = {embedding_len}-dim vector")
        print(f"  bpm            = {row.bpm}")
        print(f"  key            = {row.key}")
        print(f"  mood_label     = {row.mood_label}")
        if row.mood_scores is not None:
            top_scores = sorted(row.mood_scores.items(), key=lambda item: item[1], reverse=True)[:5]
            print("  top mood scores:")
            for mood, score in top_scores:
                print(f"    {mood:<14} {score:.3f}")
        print(f"  source         = {row.source}")

    engine.dispose()


if __name__ == "__main__":
    main()
