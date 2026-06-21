# Picture / sprite guide — Mind Hack Gin

**Game window size:** `960 × 640` pixels  
**Best file type:** PNG with **transparent background** (for characters, items, UI frames)  
**Style tip:** Pokemon-style = simple pixels, clear outline, front view for enemies, back view for player in battle

Put all files in an `assets/` folder (see structure at the bottom).

---

## 1. Battle screen (most important — like Pokemon)

| # | File name (suggested) | What to draw | Size (pixels) | Notes |
|---|------------------------|--------------|---------------|--------|
| 1 | `backgrounds/battle_field.png` | Grass + sky battle scene | **960 × 640** | Full screen; top = sky, bottom = grass |
| 2 | `sprites/player_battle_back.png` | Your survivor from **behind** (like Pokemon trainer) | **128 × 128** | Shown ~80×80 on screen; extra pixels = sharper |
| 3 | `sprites/enemy_infected.png` | ZBR infected human | **128 × 128** | Front view, scary but readable |
| 4 | `sprites/enemy_horde.png` | Many infected / swarm silhouette | **160 × 128** | Wider = group feel |
| 5 | `sprites/enemy_rafflesia_young.png` | Normal rafflesia flower monster | **128 × 128** | Red/purple flower |
| 6 | `sprites/enemy_rafflesia_giant.png` | Bigger rafflesia | **160 × 160** | Same design, larger |
| 7 | `sprites/enemy_rafflesia_final.png` | Corrupted / dark rafflesia | **192 × 192** | Final boss — most detailed |
| 8 | `ui/battle_platform_grass.png` | Small oval shadow under feet | **160 × 40** | Optional; game draws oval now |
| 9 | `ui/panel_message.png` | Text box frame (left side in battle) | **464 × 144** | Optional; game draws box now |
| 10 | `ui/panel_moves.png` | Move menu frame (right side) | **464 × 144** | Optional |
| 11 | `ui/hp_bar_frame.png` | HP bar border | **240 × 14** | Optional; bars drawn in code |
| 12 | `ui/cursor_arrow.png` | Small pointer for selected move | **24 × 24** | Optional |

**Battle layout (where art appears):**

```
┌──────────────────────────────── 960 ────────────────────────────────┐
│  [Enemy name + HP bar]                    [Enemy sprite 128px]   │  ~top
│                                         (top-right area)          │
│                                                                   │
│  ─────────── grass line (y = 320) ───────────                     │
│                                                                   │
│  [Player sprite 128px]                                              │
│  (bottom-left)          [Your HP bar]                             │
├───────────────────────────────────────────────────────────────────┤
│  Message box (left half)  │  Move buttons 2×2 (right half)       │  168px tall
└───────────────────────────────────────────────────────────────────┘
```

---

## 2. Story / exploration pictures

Shown during text + choices (center or top of screen).

| # | File name | Scene from your story | Size |
|---|-----------|----------------------|------|
| 13 | `story/intro_outbreak.png` | World in danger, biohazard | **880 × 360** |
| 14 | `story/ruellia_plant.png` | Ruellia tuberosa on path | **400 × 400** |
| 15 | `story/biohazard_gate.png` | Biohazard zone entrance | **880 × 360** |
| 16 | `story/apple_tree_rafflesia.png` | Apple tree + rafflesia wrapped around it | **880 × 360** |
| 17 | `story/note_golden_apple.png` | Paper note + golden apple | **600 × 400** |
| 18 | `story/sundew.png` | Sundew plant (bad path) | **400 × 400** |
| 19 | `story/infected_approach.png` | Group of infected coming | **880 × 360** |
| 20 | `story/pine_sap.png` | Pine tree sap in jar | **256 × 256** |
| 21 | `story/abandoned_camp.png` | Abandoned camp + backpack | **880 × 360** |
| 22 | `story/craft_flamethrower.png` | Stick + lighter + sap = flamethrower | **600 × 300** |
| 23 | `story/cave_survivors.png` | Cave with survivors | **880 × 360** |
| 24 | `story/team_fight.png` | Team vs giant rafflesia | **880 × 360** |
| 25 | `story/water_puddle_jar.png` | Puddle + jar plan (final trick) | **600 × 400** |

---

## 3. Title & menus

| # | File name | What | Size |
|---|-----------|------|------|
| 26 | `backgrounds/title.png` | Title screen background | **960 × 640** |
| 27 | `ui/logo.png` | Game logo "Mind Hack Gin" | **500 × 120** | Transparent PNG |
| 28 | `backgrounds/story_overlay.png` | Light panel behind story text | **880 × 480** | Semi-transparent OK |
| 29 | `backgrounds/ending_bg.png` | Dark ending screen background | **960 × 640** | Reuse for all endings |

---

## 4. Dice screen

| # | File name | What | Size |
|---|-----------|------|------|
| 30 | `ui/dice_d20.png` | D20 die (one image) | **120 × 120** |
| 31 | `ui/dice_glow_hard.png` | Red glow (optional) | **140 × 140** | For roll 1–6 |
| 32 | `ui/dice_glow_lucky.png` | Blue glow (optional) | **140 × 140** | For roll 17–20 |

---

## 5. Items (backpack icons)

Small icons shown next to backpack text (you can add later).

| # | File name | Item | Size |
|---|-----------|------|------|
| 33 | `items/ruellia.png` | Ruellia tuberosa | **48 × 48** |
| 34 | `items/sap_jar.png` | Sap in jar | **48 × 48** |
| 35 | `items/lighter.png` | Lighter | **48 × 48** |
| 36 | `items/stick.png` | Stick | **48 × 48** |
| 37 | `items/flamethrower.png` | Flamethrower | **48 × 48** |
| 38 | `items/golden_apple.png` | Golden apple | **48 × 48** |
| 39 | `items/golden_seed.png` | Golden apple seed | **48 × 48** |

---

## 6. Ending pictures (16 endings)

You can use **one frame** + different illustration, or 16 small variants.

| # | File name | Ending | Size |
|---|-----------|--------|------|
| 40 | `endings/bad_start.png` | Did nothing | **400 × 400** |
| 41 | `endings/sundew.png` | Sundew ate you | **400 × 400** |
| 42 | `endings/fight_early.png` | Too weak | **400 × 400** |
| 43 | `endings/run_horde.png` | Outrun by horde | **400 × 400** |
| 44 | `endings/fight_horde.png` | No weapon | **400 × 400** |
| 45 | `endings/no_camp.png` | Skipped camp | **400 × 400** |
| 46 | `endings/no_test.png` | Didn't test flamethrower | **400 × 400** |
| 47 | `endings/rush_burn.png` | Grabbed by rafflesia | **400 × 400** |
| 48 | `endings/solo_rafflesia.png` | Alone vs rafflesia | **400 × 400** |
| 49 | `endings/no_team.png` | Refused team | **400 × 400** |
| 50 | `endings/trip_rock.png` | Tripped on rock | **400 × 400** |
| 51 | `endings/defend_swarm.png` | Defended teammates | **400 × 400** |
| 52 | `endings/stab_fail.png` | Stick stab failed | **400 × 400** |
| 53 | `endings/no_ruellia.png` | No Ruellia plant | **400 × 400** |
| 54 | `endings/spare_final.png` | **Bad ending** — spared rafflesia | **400 × 400** |
| 55 | `endings/good_win.png` | **Good ending** — golden tree grows | **400 × 400** |

---

## 7. Minimum set (if you are short on time)

Start with these **12 images** — game already runs without them (colored boxes):

1. `battle_field.png` — 960×640  
2. `player_battle_back.png` — 128×128  
3. `enemy_infected.png` — 128×128  
4. `enemy_horde.png` — 160×128  
5. `enemy_rafflesia_young.png` — 128×128  
6. `enemy_rafflesia_giant.png` — 160×160  
7. `enemy_rafflesia_final.png` — 192×192  
8. `title.png` — 960×640  
9. `logo.png` — 500×120  
10. `apple_tree_rafflesia.png` — 880×360  
11. `good_win.png` — 400×400  
12. `spare_final.png` — 400×400  

---

## 8. Folder structure

```
mind hack gin game/
  assets/
    backgrounds/
    sprites/
    story/
    items/
    ui/
    endings/
  main.py
  ...
```

---

## 9. Art rules (so it fits the game)

- **Transparent PNG** for characters, items, logo, ending art.  
- **JPG or PNG** for full-screen backgrounds (no transparency needed).  
- Keep important details in the **center** — edges may be cropped on small screens later.  
- **Enemy sprites:** face the **left** (toward the player), like Pokemon.  
- **Player battle sprite:** face **right** (back toward camera).  
- Use **2× size** (e.g. draw 256×256, export 128×128) if you want crisp pixel art.

---

## Total count

| Category | How many pictures |
|----------|-------------------|
| Battle | 12 (7 required + 5 optional UI) |
| Story | 13 |
| Title / UI | 4 |
| Dice | 3 |
| Items | 7 |
| Endings | 16 |
| **Full set** | **55 images** |
| **Starter set** | **12 images** |

When your pictures are ready, ask to “load assets from the assets folder” and the game code can be updated to use them.
