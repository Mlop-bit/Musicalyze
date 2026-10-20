import numpy as np
import numpy.typing as npt
from sklearn.metrics import average_precision_score, roc_auc_score


def roc_auc(targets: npt.NDArray[np.float32], scores: npt.NDArray[np.float32]) -> float:
    return float(roc_auc_score(targets, scores, average="macro"))


def pr_auc(targets: npt.NDArray[np.float32], scores: npt.NDArray[np.float32]) -> float:
    return float(average_precision_score(targets, scores, average="macro"))
