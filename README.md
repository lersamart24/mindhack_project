# Mind Hack Gin — ZBR Outbreak (Pygame)

A Pokemon-style adventure based on your biohazard / ZBR / rafflesia story.

## Run

```bash
cd "/Users/ciy_th/Desktop/mind hack gin game"
rm -rf .venv
python3.12 -m venv .venv          # important: use 3.12, not 3.14
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**If install fails with `SDL.h not found`:** your venv is probably on Python 3.14. Pygame has no prebuilt wheel for 3.14 yet, so pip tries to compile. Recreate the venv with `python3.12` as above.

## How to play

- **Story**: Enter to advance text; Up/Down + Enter for choices.
- **Dice**: Before each fight, a weighted d20 roll sets difficulty:
  - **1–6** (50%): hard fight — stronger enemy
  - **7–10** (30%): normal
  - **11–16** (20%): easier
  - **17–20** (10%): lucky — weakest enemy
- **Battles**: Arrow keys to pick a move, Enter to confirm. Layout inspired by Pokemon (HP bars, 2×2 move grid, message box).
- **First rafflesia**: Use **Run** to escape and continue the story (like your original “run” choice).
- **Final boss**: Choose **Spare** → bad ending; **Finish** → good ending (if you picked Ruellia tuberosa earlier).
- **Endings**: Each death or ending is tracked on the title screen (collect them all).

## Files

| File | Role |
|------|------|
| `main.py` | Story flow, menus, endings |
| `battle.py` | Pokemon-style battle UI |
| `dice.py` | Weighted d20 roll |
| `constants.py` | Colors, ending text |
# mindhack_project
# mindhack_project
