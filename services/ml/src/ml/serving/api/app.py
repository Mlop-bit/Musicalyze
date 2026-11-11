from fastapi import FastAPI

from ml.serving.api.jobs import router as jobs_router
from ml.serving.api.tracks import router as tracks_router

app = FastAPI(title="Musicalyze ML Service")
app.include_router(jobs_router)
app.include_router(tracks_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
