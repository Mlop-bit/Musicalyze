import numpy as np
from numpy.typing import NDArray


def normalise_rows(embeddings: NDArray[np.float32]) -> NDArray[np.float32]:
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return (embeddings / np.where(norms == 0, 1.0, norms)).astype(np.float32)
