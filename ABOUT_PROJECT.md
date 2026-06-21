# About This Project — Mind Hack Gin

## Overview

**Mind Hack Gin — ZBR Outbreak** is a single-player, story-driven adventure game built with **Python** and **Pygame**. It combines a branching narrative about a biohazard plant outbreak with **Pokémon-style turn-based battles** and a **weighted d20 dice** system that changes fight difficulty before each encounter.

The game is designed for a **960 × 640** window, with a visual style inspired by **Pokémon Game Boy Advance** battles: bright colors, readable UI, HP bars, a 2×2 move grid, and a message box. The tone is **sci-fi plant horror**—mutated rafflesia flowers, infected humans, and a race to save a **golden apple** cure—while staying suitable for a kid-friendly RPG.

---

## Story & Setting

The world faces a catastrophe at **12:00 PM**: a biohazard outbreak has made plants roughly **ten times stronger** and infected humans with **Zoonotic Bridge Rafflesia (ZBR)**. Giant rafflesia flowers spread through forests and wrap around an **apple tree** that holds the only known cure—a **golden apple** that will be destroyed within days.

You play as a **survivor** who must choose whether to act or do nothing, gather items, craft weapons, find allies, and confront corrupted rafflesia monsters. Key story elements include:

| Element | Role in the game |
|--------|-------------------|
| **Ruellia tuberosa** | A plant you can pick early; required for the good ending’s final plan |
| **Golden apple** | The world’s cure; central to win/lose outcomes |
| **Flamethrower** | Crafted from pine sap, lighter, and stick; fire is rafflesia’s weakness |
| **Sap in a jar** | Obtained by running from a horde; used in the final boss strategy |
| **Survivor team** | Optional allies from a cave; affects late-game fights and endings |

Choices at story nodes (investigate camp, test weapon, spare or finish the final boss, etc.) branch into **15 distinct endings**, tracked on the title screen so players can collect them all.

---

## Core Gameplay Systems

### 1. Story mode

- Advance dialogue with **Enter** or **Space**.
- Make choices with **Up/Down** and **Enter**.
- The **backpack** updates as you collect items; it is shown during story scenes.

### 2. Weighted d20 (before battles)

Before each fight, the game rolls a **d20** with fixed odds—not a fair die:

| Roll range | Chance | Label | Effect on enemy |
|------------|--------|--------|-----------------|
| 1–6 | 50% | HARD FIGHT | Stronger enemy (×1.55 HP) |
| 7–10 | 30% | NORMAL | Standard (×1.0) |
| 11–16 | 20% | EASIER | Weaker (×0.82) |
| 17–20 | 10% | LUCKY | Weakest (×0.68) |

Press **Enter** after the roll animation to start the battle.

### 3. Pokémon-style battles

- Select moves with **arrow keys**, confirm with **Enter**.
- UI includes enemy/player HP bars, colored HP (green → yellow → red), move descriptions, and a message log.
- **Run** is available on some fights (e.g. the first young rafflesia) to escape and continue the story.
- On the **final boss**, special moves appear: **Spare** (bad ending) vs **Finish** (good ending, if you have Ruellia tuberosa).

### 4. Endings collection

Deaths and story failures unlock **bad endings**; the single **good ending** requires the right items and choices. The title screen shows **“Endings discovered: X / 15”** across playthroughs.

---

## Enemies

| Key | Name | Notes |
|-----|------|--------|
| `infected` | ZBR Infected | Early test fight after crafting |
| `horde` | Infected Horde | Swarm fight before the finale |
| `rafflesia_young` | Rafflesia | First encounter; can flee |
| `rafflesia_strong` | Giant Rafflesia | Mid/late boss fights |
| `rafflesia_final` | Corrupted Rafflesia | Final boss with Spare/Finish options |

Enemy HP scales with the dice multiplier before each battle.

---

## Technical Stack

| Item | Detail |
|------|--------|
| **Language** | Python 3.12 (recommended; Pygame wheels may fail on 3.14) |
| **Engine** | Pygame ≥ 2.5.0 |
| **Resolution** | 960 × 640 @ 60 FPS |
| **Architecture** | Modular: `main.py` (flow), `battle.py` (combat UI), `dice.py` (RNG), `constants.py` (palette & endings) |

The current build uses **procedural graphics** (colored rectangles for fighters, drawn UI panels). Optional PNG assets are documented in `ASSETS_GUIDE.md`, with **Gemini image-generation prompts** in `GEMINI_PROMPTS.md` for a consistent GBA-style art pass.

---

## Project Structure

```
mind hack gin game/
├── main.py              # Game loop, story graph, menus, endings
├── battle.py            # Turn-based battle screen & fighters
├── dice.py              # Weighted d20 roll logic
├── constants.py         # Screen size, colors, ending text, difficulty labels
├── requirements.txt     # pygame dependency
├── README.md            # Quick start & controls
├── ABOUT_PROJECT.md     # This file
├── ASSETS_GUIDE.md      # Sprite/background sizes & layout
├── GEMINI_PROMPTS.md    # AI art prompts for all assets
├── how to run.txt       # Setup commands
└── assets/              # (optional) backgrounds, sprites, UI art
```

---

## How to Run

```bash
cd "/Users/ciy_th/Desktop/mind hack gin game"
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

If installation fails with `SDL.h not found`, recreate the virtual environment with **Python 3.12** instead of 3.14.

---

## Design Goals

1. **Narrative branching** — Meaningful choices that lead to many endings, encouraging replay.
2. **Familiar battle UX** — Pokémon-like layout so players understand HP, moves, and flee without a tutorial.
3. **Risk before fights** — The weighted d20 adds tension and variety without changing story branches directly.
4. **Expandable presentation** — Code-first prototype with a clear path to swap in pixel art via the `assets/` folder and documented prompts.

---

## Credits & Context

This project implements an original **biohazard / ZBR / rafflesia** adventure concept as an educational or portfolio game: lightweight codebase, no external game engine, and documentation for generating a full art set with AI tools. It is suitable for classroom demos, game-jam extensions, or further features (sound, save files, sprite loading from `assets/`).

---

## Quick Reference — Controls

| Context | Keys |
|---------|------|
| Title / Ending | Enter or Space |
| Story text | Enter or Space |
| Choices | Up/Down, Enter |
| Dice → Battle | Enter |
| Battle | Arrows + Enter |

For the shortest playable guide, see `README.md`.
