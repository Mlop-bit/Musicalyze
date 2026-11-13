HIGH_ENERGY_TAGS = frozenset(
    {
        "action",
        "dramatic",
        "energetic",
        "epic",
        "fast",
        "fun",
        "groovy",
        "heavy",
        "party",
        "powerful",
        "sport",
        "upbeat",
    }
)

LOW_ENERGY_TAGS = frozenset(
    {
        "ambiental",
        "ballad",
        "calm",
        "dream",
        "mellow",
        "meditative",
        "melancholic",
        "relaxing",
        "sad",
        "slow",
        "soft",
        "soundscape",
    }
)


def energy_score(tag_scores: dict[str, float] | None) -> float | None:
    if not tag_scores:
        return None
    high = sum(score for tag, score in tag_scores.items() if tag in HIGH_ENERGY_TAGS)
    low = sum(score for tag, score in tag_scores.items() if tag in LOW_ENERGY_TAGS)
    return high - low
