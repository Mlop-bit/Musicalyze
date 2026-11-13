import statistics


def ramp_tracks(
    track_ids: list[str], energies: list[float | None], descending: bool = False
) -> list[str]:
    known = [energy for energy in energies if energy is not None]
    fallback = statistics.median(known) if known else 0.0
    ranked = sorted(
        zip(track_ids, energies, strict=True),
        key=lambda pair: fallback if pair[1] is None else pair[1],
        reverse=descending,
    )
    return [track_id for track_id, _ in ranked]
