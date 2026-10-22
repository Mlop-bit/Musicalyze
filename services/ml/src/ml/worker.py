import logging
import time
from collections.abc import Callable

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.serving.jobs.repository import claim_next_job, complete_job, fail_job
from ml.serving.jobs.runner import run_job

logger = logging.getLogger(__name__)


def process_next_job(session_factory: Callable[[], Session], settings: Settings) -> bool:
    with session_factory() as session:
        job = claim_next_job(session, settings.job_lease_minutes, settings.job_max_attempts)
        session.commit()
        if job is None:
            return False
        job_id = job.id
        try:
            result = run_job(session, settings, job)
            complete_job(session, job_id, result)
        except Exception as error:
            logger.exception("Job %s failed", job_id)
            session.rollback()
            fail_job(session, job_id, str(error) or type(error).__name__)
        session.commit()
    return True


def main() -> None:
    settings = Settings.model_validate({})
    engine = create_engine(settings.database_url)
    try:
        while True:
            if not process_next_job(lambda: Session(engine), settings):
                time.sleep(settings.worker_poll_seconds)
    except KeyboardInterrupt:
        logger.info("Worker stopped")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
