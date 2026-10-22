from sqlalchemy import select

from ml.core.config import Settings
from ml.serving.feature_store.classification import save_classifier_mood_for_track
from ml.serving.feature_store.db import session_scope
from ml.serving.feature_store.models import TrackFeatures

BATCH_SIZE = 100


def main() -> None:
    settings = Settings()
    processed = 0
    with session_scope(settings) as session:
        track_ids = list(
            session.scalars(
                select(TrackFeatures.track_id).where(TrackFeatures.tag_scores.is_(None))
            )
        )
        for index, track_id in enumerate(track_ids, start=1):
            save_classifier_mood_for_track(session, settings, track_id)
            processed = index
            if index % BATCH_SIZE == 0:
                session.commit()
        session.commit()
    print(f"Backfilled tag scores for {processed} tracks")


if __name__ == "__main__":
    main()
