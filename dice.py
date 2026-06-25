"""Weighted d20 roll: story odds map to die faces 1–6, 7–10, 11–16, 17–20."""

import random
from constants import DIFFICULTY_LABELS

# Weights must sum to 100 so all tiers can fire
_TIERS = (
    ("worst", (1, 6), 40),
    ("normal", (7, 10), 30),
    ("good", (11, 16), 20),
    ("best", (17, 20), 10),
)


def roll_d20() -> tuple[int, str, str, float]:
    """
    Returns (face_value, tier_key, label, enemy_multiplier).
    Tier chances: worst 50%, normal 30%, good 20%, best 10%.
    """
    r = random.uniform(0, 100)
    cumulative = 0
    tier_key = "normal"
    low, high = 7, 10
    for key, (a, b), weight in _TIERS:
        cumulative += weight
        if r <= cumulative:
            tier_key = key
            low, high = a, b
            break
    value = random.randint(low, high)
    label, _, mult = DIFFICULTY_LABELS[tier_key]
    return value, tier_key, label, mult
