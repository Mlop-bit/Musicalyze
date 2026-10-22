# Musicalyze

## Problem statement
Spotify removed its Audio Features, Audio Analysis, Recommendations and Related Artists endpoints for new applications in November 2024. Musicalyze investigates how acoustic and semantic track information can be reconstructed independently from public data and audio previews, and how it can be used to split, reorder and recommend playlist tracks.

## Background
The ubiquity of streaming music has led users to accumulate extensive, unstructured track libraries. These collections typically lack stylistic coherence and optimal sequencing, complicating both playlist curation and targeted music discovery. This challenge is currently exacerbated by API restrictions: as of November 2024, Spotify deprecated the endpoints providing acoustic features (e.g., tempo, energy, key) and algorithmic recommendations for new applications. Consequently, external applications can no longer rely on native platform metadata for audio analysis.

This project proposes a Spotify-integrated web application that independently reconstructs this acoustic metadata to circumvent current API limitations. The architecture combines an open-source pretrained music model (MuQ) with public datasets (AcousticBrainz, MTG-Jamendo). Leveraging this consolidated data, the application automatically segments playlists into mood-coherent subsets, computes optimal track sequences, and generates targeted recommendations. These functions are driven by a custom-trained mood and genre classifier, establishing a self-sufficient Music Information Retrieval (MIR) pipeline independent of proprietary third-party services.


## Objectives
- Build an independent data pipeline to reconstruct missing acoustic metadata using a combination of public music datasets and a pretrained model
- Train and evaluate a custom mood and genre classifier using these reconstructed acoustic representations.
- Develop a web application that applies the classification outputs to automate playlist segmentation, track sequencing, and music recommendation.

## Specification
- Has to run on any recent browser.
- ?

## Prerequisites
- Python 3.13 with [`uv`](https://docs.astral.sh/uv/) and [`just`](https://just.systems/)
- Node.js 20.9 or later with `pnpm`
- Docker (for the PostgreSQL + `pgvector` database defined in `compose.yaml`), or your own PostgreSQL with the `pgvector` extension
- An S3-compatible bucket (the project uses a self-hosted Garage instance) and a Cloudflare Workers KV namespace

## Installation
To install this project, simply clone the repository using the following command:
```
https://github.com/Mlop-bit/AIProject.git
```

## Project initialisation
1. Create a `.env` file in the project’s `services/ml/` folder.
2. Please enter the following variables :

| Variable                     | Description |
| ---------------------------- | ----------- |
| `MUSICALYZE_S3_ENDPOINT_URL` |             |
| `MUSICALYZE_S3_REGION`       |             |
| `MUSICALYZE_S3_BUCKET`       |             |
| `MUSICALYZE_S3_ACCESS_KEY`   |             |
| `MUSICALYZE_S3_SECRET_KEY`   |             |
| `MUSICALYZE_KV_ACCOUNT_ID`   |             |
| `MUSICALYZE_KV_NAMESPACE_ID` |             |
| `MUSICALYZE_KV_API_TOKEN`    |             |
| `MUSICALYZE_DB_HOST`         | PostgreSQL host of the feature store |
| `MUSICALYZE_DB_PORT`         | PostgreSQL port |
| `MUSICALYZE_DB_USER`         | PostgreSQL user |
| `MUSICALYZE_DB_PASSWORD`     | PostgreSQL password |
| `MUSICALYZE_DB_NAME`         | PostgreSQL database name |
| `MUSICALYZE_MUSICBRAINZ_CONTACT` | Optional contact address added to the MusicBrainz User-Agent |
| `MUSICALYZE_API_KEY`         | Shared secret the web backend sends in the `X-API-Key` header of every job request |
| `MUSICALYZE_MAX_NEW_CANDIDATES` | Optional cap on new recommendation candidates resolved per request (default 150) |

3. Fill in the `.env` file in the project's `apps/web/` folder (a placeholder already exists there - replace the fake value).
4. Please enter the following variable :

| Variable                      | Description |
| ------------------------------ | ----------- |
| `MUSICALYZE_GITHUB_TOKEN`      | Classic GitHub PAT with the `repo` scope, generated from your own account, used to read commit history for the `/changelog` page. Fine-grained PATs only work here if you're an org member with fine-grained access enabled; collaborators on another user's personal repo must use a classic token. |

## Project launch
```
just db-up      # starts the PostgreSQL + pgvector container using the MUSICALYZE_DB_* values of services/ml/.env
just sync       # installs the Python environment (cpu or cu130 extra, auto-detected)
just migrate    # applies the feature store migrations
just check      # ruff, pyright and pytest
```
The ML service itself can also run as a container with `docker compose --env-file services/ml/.env --profile ml up`. The end-to-end demo, run from `services/ml` with `uv run python scripts/demo_resolve_track.py [track_id artist title musicbrainz_id]`, resolves a track through Deezer, MusicBrainz, AcousticBrainz and the trained classifier. The classifier is trained with `services/ml/scripts/run_training.py <dataset directory>`.

### Jobs

Reorder, split and recommend run as background jobs stored in PostgreSQL. Start the API (`cd services/ml && uv run uvicorn ml.serving.api.app:app`) and, in another terminal, the worker (`just worker`), which runs on the same machine as the MuQ model. Every request carries the `X-API-Key` header and answers `202` with a job id; `GET /jobs/{job_id}` returns the status, the phase (`resolving` or `computing`), the progress as `done`/`total` and, once finished, the result. `GET /jobs?user_id=...` lists the jobs of one user.

```
curl -X POST localhost:8000/jobs/reorder -H "X-API-Key: $MUSICALYZE_API_KEY" -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "tracks": [{"track_id": "t1", "title": "Creep", "artist": "Radiohead"}]}'
curl -X POST localhost:8000/jobs/split -H "X-API-Key: $MUSICALYZE_API_KEY" -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "tracks": [...], "k": 3}'
curl -X POST localhost:8000/jobs/recommend -H "X-API-Key: $MUSICALYZE_API_KEY" -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "seeds": [...], "candidates": [...], "tags": ["calm"], "limit": 20}'
curl localhost:8000/jobs/<job_id> -H "X-API-Key: $MUSICALYZE_API_KEY"
```

Omit `k` to let the system choose the number of playlists. The web backend supplies the candidate tracks for `recommend`; at most `MUSICALYZE_MAX_NEW_CANDIDATES` of them that are not yet in the feature store are resolved per request.
