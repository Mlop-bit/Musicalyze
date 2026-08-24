DEV_SUBSET_CHUNK_COUNT = 2
TOTAL_CHUNK_COUNT = 100


def chunks_for_mode(mode: str) -> list[int]:
    if mode == "dev":
        return list(range(DEV_SUBSET_CHUNK_COUNT))
    if mode == "full":
        return list(range(TOTAL_CHUNK_COUNT))
    raise ValueError(f"unknown dataset mode: {mode}")
