import logging

import numpy as np
import numpy.typing as npt
from sklearn.metrics import average_precision_score, roc_auc_score

logger = logging.getLogger(__name__)


def scorable_columns(targets: npt.NDArray[np.float32]) -> npt.NDArray[np.bool_]:
    positives = targets.sum(axis=0)
    return (positives > 0) & (positives < targets.shape[0])


def restrict_to_scorable_tags(
    targets: npt.NDArray[np.float32], scores: npt.NDArray[np.float32]
) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]]:
    mask = scorable_columns(targets)
    excluded = int((~mask).sum())
    if excluded > 0:
        logger.warning(
            "%d of %d tags have no positive or no negative sample and are excluded from the metric",
            excluded,
            mask.shape[0],
        )
    return targets[:, mask], scores[:, mask]


def roc_auc(targets: npt.NDArray[np.float32], scores: npt.NDArray[np.float32]) -> float:
    scorable_targets, scorable_scores = restrict_to_scorable_tags(targets, scores)
    return float(roc_auc_score(scorable_targets, scorable_scores, average="macro"))


def pr_auc(targets: npt.NDArray[np.float32], scores: npt.NDArray[np.float32]) -> float:
    scorable_targets, scorable_scores = restrict_to_scorable_tags(targets, scores)
    return float(average_precision_score(scorable_targets, scorable_scores, average="macro"))
