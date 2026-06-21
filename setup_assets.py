"""One-time helper: copy numbered picture/*.png into assets/ folders."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PICTURE = ROOT / "picture"
ASSETS = ROOT / "assets"

# picture/N.png where N = prompt_number + 24
MAPPING: dict[int, str] = {
    1: "backgrounds/title.png",
    2: "backgrounds/battle_field.png",
    3: "backgrounds/ending_bg.png",
    4: "backgrounds/story_overlay.png",
    5: "ui/logo.png",
    6: "ui/dice_d20.png",
    7: "ui/dice_glow_hard.png",
    8: "ui/dice_glow_lucky.png",
    9: "sprites/player_battle_back.png",
    10: "sprites/enemy_infected.png",
    11: "sprites/enemy_horde.png",
    12: "sprites/enemy_rafflesia_young.png",
    13: "sprites/enemy_rafflesia_giant.png",
    14: "sprites/enemy_rafflesia_final.png",
    15: "story/intro_outbreak.png",
    16: "story/ruellia_plant.png",
    17: "story/biohazard_gate.png",
    18: "story/apple_tree_rafflesia.png",
    19: "story/note_golden_apple.png",
    20: "story/sundew.png",
    21: "story/infected_approach.png",
    22: "story/pine_sap.png",
    23: "story/abandoned_camp.png",
    24: "story/craft_flamethrower.png",
    25: "story/cave_survivors.png",
    26: "story/team_fight.png",
    27: "story/water_puddle_jar.png",
    28: "items/ruellia.png",
    29: "items/sap_jar.png",
    30: "items/lighter.png",
    31: "items/stick.png",
    32: "items/flamethrower.png",
    33: "items/golden_apple.png",
    34: "items/golden_seed.png",
    35: "endings/bad_start.png",
    36: "endings/sundew.png",
    37: "endings/fight_early.png",
    38: "endings/run_horde.png",
    39: "endings/fight_horde.png",
    40: "endings/no_camp.png",
    41: "endings/no_test.png",
    42: "endings/rush_burn.png",
    43: "endings/solo_rafflesia.png",
    44: "endings/no_team.png",
    45: "endings/trip_rock.png",
    46: "endings/defend_swarm.png",
    47: "endings/stab_fail.png",
    48: "endings/no_ruellia.png",
    49: "endings/spare_final.png",
    50: "endings/good_win.png",
}


def main() -> None:
    copied = 0
    for prompt_num, rel_path in MAPPING.items():
        src = PICTURE / f"{prompt_num + 24}.png"
        dst = ASSETS / rel_path
        if not src.exists():
            print(f"SKIP missing: {src.name}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
        print(f"OK {src.name} -> {rel_path}")
    print(f"\nDone: {copied} files copied to assets/")


if __name__ == "__main__":
    main()
