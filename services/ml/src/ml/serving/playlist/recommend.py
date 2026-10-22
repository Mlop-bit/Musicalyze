from dataclasses import dataclass


@dataclass(frozen=True)
class Recommendation:
    track_id: str
    similarity: float


def merge_best_matches(
    matches_per_seed: list[list[Recommendation]], limit: int
) -> list[Recommendation]:
    best: dict[str, Recommendation] = {}
    for matches in matches_per_seed:
        for match in matches:
            current = best.get(match.track_id)
            if current is None or match.similarity > current.similarity:
                best[match.track_id] = match
    ranked = sorted(best.values(), key=lambda item: (-item.similarity, item.track_id))
    return ranked[:limit]
