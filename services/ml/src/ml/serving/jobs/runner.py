from typing import Any

import numpy as np
from numpy.typing import NDArray
from sqlalchemy.orm import Session

from ml.core.config import Settings
from ml.serving.feature_store.models import TrackFeatures
from ml.serving.feature_store.repository import get_track_features, nearest_tracks
from ml.serving.jobs.models import Job, JobKind, JobPhase
from ml.serving.jobs.payloads import (
    RecommendPayload,
    ReorderPayload,
    SplitPayload,
    TrackDescriptor,
)
from ml.serving.jobs.repository import set_phase, set_progress
from ml.serving.jobs.track_resolution import ResolutionOutcome, resolve_tracks
from ml.serving.playlist.energy import energy_score
from ml.serving.playlist.ramp import ramp_tracks
from ml.serving.playlist.reorder import reorder_tracks
from ml.serving.playlist.split import split_tracks


def run_job(session: Session, settings: Settings, job: Job) -> dict[str, Any]:
    set_phase(session, job.id, JobPhase.RESOLVING, 0)
    session.commit()
    match job.kind:
        case JobKind.REORDER:
            return _run_reorder(session, settings, job, ReorderPayload.model_validate(job.payload))
        case JobKind.SPLIT:
            return _run_split(session, settings, job, SplitPayload.model_validate(job.payload))
        case JobKind.RECOMMEND:
            return _run_recommend(
                session, settings, job, RecommendPayload.model_validate(job.payload)
            )


def _resolve(
    session: Session,
    settings: Settings,
    job: Job,
    tracks: list[TrackDescriptor],
    offset: int = 0,
    new_limit: int | None = None,
) -> ResolutionOutcome:
    def report(done: int, total: int) -> None:
        set_progress(session, job.id, offset + done, offset + total)
        session.commit()

    return resolve_tracks(session, settings, tracks, report, new_limit=new_limit)


def _begin_computing(session: Session, job: Job) -> None:
    set_phase(session, job.id, JobPhase.COMPUTING, 0)
    session.commit()


def _load_features(session: Session, track_ids: list[str]) -> list[TrackFeatures]:
    loaded = [get_track_features(session, track_id) for track_id in track_ids]
    return [features for features in loaded if features is not None]


def _embeddings(features: list[TrackFeatures]) -> NDArray[np.float32]:
    if not features:
        return np.zeros((0, 0), dtype=np.float32)
    return np.array([list(item.embedding) for item in features], dtype=np.float32)


def _order_by_mode(features: list[TrackFeatures], payload: ReorderPayload) -> list[str]:
    track_ids = [item.track_id for item in features]
    if payload.mode != "similarity":
        energies = [energy_score(item.tag_scores) for item in features]
        return ramp_tracks(track_ids, energies, descending=payload.mode == "energetic_to_calm")
    start_index = (
        track_ids.index(payload.start_track_id) if payload.start_track_id in track_ids else 0
    )
    return reorder_tracks(
        track_ids,
        _embeddings(features),
        [item.bpm for item in features],
        [item.key for item in features],
        start_index=start_index,
    )


def _track_details(features: list[TrackFeatures], order: list[str]) -> list[dict[str, Any]]:
    by_id = {item.track_id: item for item in features}
    return [
        {
            "track_id": track_id,
            "mood_label": by_id[track_id].mood_label,
            "energy": energy_score(by_id[track_id].tag_scores),
        }
        for track_id in order
    ]


def _run_reorder(
    session: Session, settings: Settings, job: Job, payload: ReorderPayload
) -> dict[str, Any]:
    outcome = _resolve(session, settings, job, payload.tracks)
    _begin_computing(session, job)
    features = _load_features(session, outcome.resolved_ids)
    order = _order_by_mode(features, payload)
    return {
        "order": order,
        "skipped": outcome.skipped_ids,
        "details": _track_details(features, order),
        "mode": payload.mode,
    }


def _run_split(
    session: Session, settings: Settings, job: Job, payload: SplitPayload
) -> dict[str, Any]:
    outcome = _resolve(session, settings, job, payload.tracks)
    _begin_computing(session, job)
    features = _load_features(session, outcome.resolved_ids)
    clusters = split_tracks(
        [item.track_id for item in features],
        _embeddings(features),
        [item.tag_scores or {} for item in features],
        payload.k,
    )
    return {
        "clusters": [
            {"name": cluster.name, "track_ids": cluster.track_ids} for cluster in clusters
        ],
        "k": len(clusters),
        "skipped": outcome.skipped_ids,
    }


def _run_recommend(
    session: Session, settings: Settings, job: Job, payload: RecommendPayload
) -> dict[str, Any]:
    seed_outcome = _resolve(session, settings, job, payload.seeds)
    candidate_outcome = _resolve(
        session,
        settings,
        job,
        payload.candidates,
        offset=len(seed_outcome.resolved_ids) + len(seed_outcome.skipped_ids),
        new_limit=settings.max_new_candidates,
    )
    _begin_computing(session, job)
    seed_features = _load_features(session, seed_outcome.resolved_ids)
    recommendations = (
        nearest_tracks(
            session,
            [[float(value) for value in item.embedding] for item in seed_features],
            exclude_ids=[seed.track_id for seed in payload.seeds],
            tags=payload.tags,
            limit=payload.limit,
        )
        if seed_features
        else []
    )
    return {
        "recommendations": [
            {"track_id": item.track_id, "similarity": item.similarity} for item in recommendations
        ],
        "skipped": seed_outcome.skipped_ids + candidate_outcome.skipped_ids,
        "dropped_candidates": candidate_outcome.dropped_candidates,
    }
