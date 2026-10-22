import json
import sys
import threading
import time
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.serving.jobs.models import JobKind
from ml.serving.jobs.repository import enqueue_job, get_job
from ml.worker import process_next_job

POLL_SECONDS = 0.25
USER_ID = "benchmark"


def main() -> None:
    kind = JobKind(sys.argv[1])
    payload = json.loads(Path(sys.argv[2]).read_text())
    settings = Settings.model_validate({})
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        job_id = enqueue_job(session, USER_ID, kind, payload).id
        session.commit()

    phase_starts: dict[str, float] = {}
    stop = threading.Event()

    def watch() -> None:
        with Session(engine) as watcher:
            while not stop.is_set():
                watcher.expire_all()
                job = get_job(watcher, job_id)
                if job is not None and job.phase is not None:
                    phase_starts.setdefault(job.phase.value, time.perf_counter())
                time.sleep(POLL_SECONDS)

    watcher_thread = threading.Thread(target=watch)
    watcher_thread.start()
    started = time.perf_counter()
    process_next_job(lambda: Session(engine), settings)
    finished = time.perf_counter()
    stop.set()
    watcher_thread.join()

    with Session(engine) as session:
        job = get_job(session, job_id)
        assert job is not None
        print(f"status={job.status.value} done={job.done}/{job.total} error={job.error}")
        print(json.dumps(job.result, indent=2))
    ordered = sorted(phase_starts.items(), key=lambda item: item[1])
    boundaries = [start for _, start in ordered] + [finished]
    for (phase, start), end in zip(ordered, boundaries[1:], strict=True):
        print(f"{phase}: {end - start:.1f}s")
    print(f"total: {finished - started:.1f}s")
    engine.dispose()


if __name__ == "__main__":
    main()
