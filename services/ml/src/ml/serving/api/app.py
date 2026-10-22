from fastapi import FastAPI

from ml.serving.api.jobs import router as jobs_router

app = FastAPI(title="Musicalyze ML Service")
app.include_router(jobs_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
