"""Shared colors, layout, and fonts for Mind Hack Gin."""

SCREEN_W = 960
SCREEN_H = 640
FPS = 60

# Pokemon-inspired palette
BG_TOP = (72, 120, 200)
BG_BOTTOM = (40, 72, 140)
PANEL = (248, 248, 248)
PANEL_DARK = (56, 56, 72)
PANEL_BORDER = (32, 32, 48)
TEXT = (32, 32, 48)
TEXT_LIGHT = (248, 248, 252)
HP_GREEN = (72, 200, 96)
HP_YELLOW = (240, 200, 48)
HP_RED = (232, 72, 72)
HP_BG = (48, 48, 64)
ACCENT = (255, 200, 48)
DICE_BAD = (200, 64, 64)
DICE_NORMAL = (200, 160, 64)
DICE_GOOD = (96, 180, 96)
DICE_BEST = (96, 200, 255)

DIFFICULTY_LABELS = {
    "worst": ("HARD FIGHT", DICE_BAD, 1.55),
    "normal": ("NORMAL", DICE_NORMAL, 1.0),
    "good": ("EASIER", DICE_GOOD, 0.82),
    "best": ("LUCKY", DICE_BEST, 0.68),
}

ENDINGS = {
    "bad_start": "Bad Ending — You did nothing. Everyone dies.",
    "sundew": "Bad Ending — Stepped on a sundew. It ate you.",
    "fight_early": "Bad Ending — Too weak to fight the rafflesia.",
    "run_horde": "Bad Ending — Outrun by a thousand infected.",
    "fight_horde": "Bad Ending — No weapon against the horde.",
    "no_camp": "Bad Ending — Killed in the forest without supplies.",
    "no_test": "Bad Ending — Didn't know how to use the flamethrower.",
    "rush_burn": "Bad Ending — Flamethrower too slow; rafflesia grabs you.",
    "solo_rafflesia": "Bad Ending — Not strong enough alone.",
    "no_team": "Bad Ending — Refused allies and fell to the rafflesia.",
    "trip_rock": "Bad Ending — Tripped on a rock during the team fight.",
    "defend_swarm": "Bad Ending — Overwhelmed protecting teammates.",
    "stab_fail": "Bad Ending — Stick stab didn't finish it.",
    "no_ruellia": "Bad Ending — No Ruellia tuberosa for the final plan.",
    "spare_final": "Bad Ending — You spared the rafflesia. The golden apple is lost.",
    "good_win": "Good Ending — You saved the world with the golden apple seed!",
}
