# Gemini prompts — Mind Hack Gin art

Copy one prompt at a time into **Gemini** (image generation).  
After each image: **Download → resize** to the exact pixels if Gemini’s size is different (use [photopea.com](https://www.photopea.com) or Preview on Mac).

---

## Step 0 — Paste this FIRST (same style for every picture)

Copy this bladd **“Use this style forock once. Then  all images in this project:”** before your first prompt, or paste it at the end of every prompt:

```
STYLE (use for every image):
Pokemon Game Boy Advance battle game aesthetic. 2D pixel art OR clean flat cartoon (pick one and keep it for ALL images). Bright readable colors, thick black outlines, no photorealism, no 3D render. Sci-fi plant horror adventure tone: biohazard, mutated plants, rafflesia flowers, golden apple cure. Mood: tense but colorful, suitable for a kid-friendly RPG.
```

**Tip for Gemini:** If it ignores exact pixels, set **aspect ratio** instead:
- **960×640** → aspect ratio **3:2** (landscape)
- **880×360** → very wide landscape
- **400×400** or **128×128** → **1:1** square
- **600×400** → **3:2**
- **600×300** → **2:1**

For sprites with no background, add: **`transparent background, PNG, single character only, centered.`**

---

# PART 1 — Full game window (960 × 640) — START HERE

Generate these **4 full-screen backgrounds** first. Aspect ratio: **3:2**.

---

### 1. `title.png` — Title screen  
**Save as:** `assets/backgrounds/title.png`  
**Size:** 960 × 640

```
Create a 2D game title screen background, aspect ratio 3:2, 960x640 pixels.

Pokemon GBA RPG style pixel art. Wide landscape.

Scene: Apocalyptic forest at noon. Yellow biohazard warning tape on trees. Mutated giant vines and red rafflesia flowers in the distance. Hazy green sky, subtle smoke. Empty path leading into danger. No characters, no text in the image.

Mood: "Mind Hack Gin" — plant outbreak adventure. Dramatic but not gory. Space at top center left empty for a game logo later.

Flat colors, thick outlines, no 3D, no photorealism.
```

---

### 2. `battle_field.png` — Battle background  
**Save as:** `assets/backgrounds/battle_field.png`  
**Size:** 960 × 640

```
Create a 2D Pokemon-style battle background, aspect ratio 3:2, 960x640 pixels.

Top half: bright blue sky with a few clouds. Bottom half: green grass field with simple tufts. Horizon line at middle height. Empty battle arena — no characters, no UI, no text.

Classic handheld RPG battle field look (like Pokemon Ruby/Sapphire grass route). Slightly mutated forest tint: faint purple flowers far in background optional.

Pixel art or flat cartoon, thick outlines, cheerful colors on top, slightly eerie plants in far distance only.
```

---

### 3. `ending_bg.png` — Ending screen background  
**Save as:** `assets/backgrounds/ending_bg.png`  
**Size:** 960 × 640

```
Create a 2D game background for an ending/results screen, aspect ratio 3:2, 960x640 pixels.

Dark moody sky (purple-blue sunset). Silhouette of dead twisted trees and giant flower monsters on horizon. Subtle biohazard symbols faded in clouds. Center area darker and emptier for text and a square ending illustration overlay.

Pokemon RPG pixel art style but darker than title screen. No characters, no text. Ominous but not hyper-violent.
```

---

### 4. `story_overlay.png` — Story text panel (optional)  
**Save as:** `assets/backgrounds/story_overlay.png`  
**Size:** 880 × 480

```
Create a semi-transparent story dialogue panel for a 2D RPG, wide rectangle about 880x480, aspect ratio roughly 16:9.

Simple parchment or light gray rounded rectangle frame with dark border. Center is mostly empty/light for text. Subtle corner decorations: small leaf and biohazard icons.

Flat 2D UI art, Pokemon menu box style. No characters. PNG with soft edges OK.
```

---

# PART 2 — Logo & UI (on top of full screen)

---

### 5. `logo.png`  
**Save as:** `assets/ui/logo.png`  
**Size:** 500 × 120 | **Transparent background**

```
Game logo text image, transparent background, PNG, roughly 500x120 wide banner.

Title text: "Mind Hack Gin" in bold pixel font. Colors: gold yellow letters, dark green outline, small red rafflesia flower icon on one side. Sci-fi plant horror adventure game.

No background, only logo. Readable at small size. Pokemon-era RPG title style.
```

---

### 6. `dice_d20.png`  
**Save as:** `assets/ui/dice_d20.png`  
**Size:** 120 × 120 | **Transparent**

```
Single 20-sided dice (d20) icon for a video game UI, 120x120 pixels, square, transparent background PNG.

Purple die with white numbers, slight shine, pixel art RPG inventory icon style. Isometric or front view, centered, no shadow on background.
```

---

### 7. `dice_glow_hard.png` (optional)  
**Save as:** `assets/ui/dice_glow_hard.png`  
**Size:** 140 × 140 | **Transparent**

```
Red magical glow ring effect for game UI, 140x140, transparent PNG. Soft circular aura only, no solid center — meant to go behind a dice. Pixel art style.
```

---

### 8. `dice_glow_lucky.png` (optional)  
**Save as:** `assets/ui/dice_glow_lucky.png`  
**Size:** 140 × 140 | **Transparent**

```
Blue golden lucky glow ring for game UI, 140x140, transparent PNG. Soft circular sparkle aura, pixel art RPG style.
```

---

# PART 3 — Battle sprites (Pokemon fight screen)

**All:** transparent PNG, **1:1 square** unless noted. Enemy faces **left** toward player. Player faces **right** (seen from behind).

---

### 9. `player_battle_back.png` — 128 × 128

```
2D RPG battle sprite, 128x128, transparent PNG, square.

Young survivor character seen FROM BEHIND (back view) like a Pokemon trainer in battle. Hoodie, backpack, holding a makeshift flamethrower on shoulder. Facing right. Simple pixel art, thick outline, blue-gray clothes.

No background. Single character centered.
```

---

### 10. `enemy_infected.png` — 128 × 128

```
2D RPG enemy battle sprite, 128x128, transparent PNG.

Zombie-like infected human corrupted by plant virus (ZBR). Greenish skin, vine marks on arms, glowing eyes. Front/side view facing LEFT toward player. Scary but cartoon, not gory.

Pokemon enemy sprite style, pixel art, centered, no background.
```

---

### 11. `enemy_horde.png` — 160 × 128

```
2D RPG enemy sprite, wide 160x128, transparent PNG.

Silhouette of MANY infected humans swarming together as one enemy unit. Facing left. Dark purple-green mass with reaching hands. Horde monster feel.

Pixel art Pokemon style, no background.
```

---

### 12. `enemy_rafflesia_young.png` — 128 × 128

```
2D RPG enemy battle sprite, 128x128, transparent PNG.

Monster based on Rafflesia flower — large red spotted petals, central maw, short vine legs. Facing left. Carnivorous plant boss, cute-scary Pokemon style.

No background, pixel art, thick outline.
```

---

### 13. `enemy_rafflesia_giant.png` — 160 × 160

```
Same Rafflesia flower monster as before but BIGGER and meaner, 160x160 transparent PNG, facing left.

More petals, dripping spores, angrier eyes in center. Giant boss version. Pokemon GBA pixel art style, no background.
```

---

### 14. `enemy_rafflesia_final.png` — 192 × 192

```
Final boss Rafflesia monster, 192x192, transparent PNG, facing left.

Corrupted dark purple-black petals, glowing toxic green spots, massive size, cracked golden apple stuck in vines (dying). Most detailed sprite. Epic but still 2D pixel/cartoon, not realistic.

No background.
```

---

# PART 4 — Story scenes (wide pictures)

Aspect ratio **very wide** (~880×360) unless square noted.

---

### 15. `intro_outbreak.png` — 880 × 360

```
Wide 2D story scene illustration, aspect ratio ~2.4:1 (880x360), landscape.

City/forest edge in crisis: biohazard outbreak, hazmat signs, mutated trees 10x normal size, people running. Green toxic fog. Text adventure game cutscene art, Pokemon RPG pixel style, no UI, no text in image.
```

---

### 16. `ruellia_plant.png` — 400 × 400

```
Square story illustration 400x400. Single purple-blue Ruellia tuberosa wildflower plant growing on forest path. Glowing slightly (important item). Cute detailed pixel art, no character, soft forest background simple.
```

---

### 17. `biohazard_gate.png` — 880 × 360

```
Wide landscape 880x360. Entrance to biohazard zone: chain fence, yellow tape, warning signs, dead trees, red flowers inside. Foreboding path forward. 2D pixel RPG cutscene, no text.
```

---

### 18. `apple_tree_rafflesia.png` — 880 × 360

```
Wide landscape 880x360. Apple tree in center with ONE shining golden apple. Huge red Rafflesia flower wrapped around trunk like a parasite. Inside quarantine greenhouse or toxic grove. Key story scene, pixel art RPG.
```

---

### 19. `note_golden_apple.png` — 600 × 400

```
600x400 scene. Close-up: crumpled paper note with scribbled drawings (no readable English text — use squiggles). Next to note: glowing golden apple on branch. Fire symbol sketched on paper (hint: fire weakness). Pixel art adventure game.
```

---

### 20. `sundew.png` — 400 × 400

```
400x400. Carnivorous sundew plant on ground, sticky red tentacles, trapped boot silhouette (danger). Dark comedy horror, pixel art, forest floor. Bad ending foreshadow.
```

---

### 21. `infected_approach.png` — 880 × 360

```
Wide 880x360. Forest path, large group of plant-infected humans shuffling toward camera. Mist, green fog. Player POV from hiding. Tense, Pokemon RPG story art style.
```

---

### 22. `pine_sap.png` — 256 × 256

```
256x256. Glass jar filled with golden pine tree sap, cork lid, label blank. Item icon style but larger, on simple forest background. Pixel art game item.
```

---

### 23. `abandoned_camp.png` — 880 × 360

```
Wide 880x360. Abandoned survivor camp: tent, campfire cold, dropped backpack open showing lighter inside glowing. Forest clearing, lonely mood. Pixel RPG cutscene.
```

---

### 24. `craft_flamethrower.png` — 600 × 300

```
Wide 600x300 horizontal. Crafting diagram style still life: stick + lighter + jar of sap = homemade flamethrower with small flame. Simple arrows between items (cartoon arrows OK). Pixel art, no text labels.
```

---

### 25. `cave_survivors.png` — 880 × 360

```
Wide 880x360. Dark cave interior lit by torch. 3-4 survivors hiding, scared but friendly, makeshift weapons. Stalactites, vines at entrance. Hopeful team-up moment. Pixel RPG story art.
```

---

### 26. `team_fight.png` — 880 × 360

```
Wide 880x360. Team of survivors with flamethrowers facing giant Rafflesia boss in biohazard arena. Golden apple tree damaged in background. Epic battle scene, pixel art, no UI.
```

---

### 27. `water_puddle_jar.png` — 600 × 400

```
600x400. Puddle of water on toxic ground, survivor hand holding jar of sap and purple Ruellia flower ready to mix. Clever trick plan moment. Bright pixel art, hopeful mood.
```

---

# PART 5 — Item icons (48 × 48 each)

**All:** square **48×48**, transparent PNG, simple RPG inventory icon.

---

### 28. `ruellia.png`
```
48x48 inventory icon, transparent PNG: small purple Ruellia tuberosa flower, pixel art RPG item.
```

### 29. `sap_jar.png`
```
48x48 inventory icon, transparent PNG: tiny glass jar of golden sap, pixel art.
```

### 30. `lighter.png`
```
48x48 inventory icon, transparent PNG: red pocket lighter with small flame, pixel art.
```

### 31. `stick.png`
```
48x48 inventory icon, transparent PNG: wooden stick branch, pixel art RPG item.
```

### 32. `flamethrower.png`
```
48x48 inventory icon, transparent PNG: DIY flamethrower made from stick and lighter, small flame, pixel art.
```

### 33. `golden_apple.png`
```
48x48 inventory icon, transparent PNG: shining golden apple, magical glow, pixel art.
```

### 34. `golden_seed.png`
```
48x48 inventory icon, transparent PNG: tiny glowing golden seed, pixel art.
```

---

# PART 6 — Ending pictures (400 × 400 each)

Square **1:1**, story illustration for each ending. Add the STYLE block to each.

---

### 35. `bad_start.png` — Did nothing
```
400x400 square ending illustration. Person sitting idle on couch while world outside window burns with plant monsters. "Too late" mood. Pixel art, dark comedy, no text.
```

### 36. `sundew.png` — Sundew ate you
```
400x400. Giant sundew plant eating silhouette of adventurer, boots sticking out. Bad ending. Cartoon pixel horror, not gory.
```

### 37. `fight_early.png` — Too weak
```
400x400. Small hero knocked down by medium Rafflesia flower. Defeat screen vibe. Pixel RPG.
```

### 38. `run_horde.png` — Outrun by horde
```
400x400. Character running but surrounded by endless infected swarm from all sides. Defeat, pixel art.
```

### 39. `fight_horde.png` — No weapon
```
400x400. Unarmed survivor facing horde with empty hands. Hopeless fight. Pixel art.
```

### 40. `no_camp.png` — Skipped camp
```
400x400. Lost in dark forest at night, infected behind trees, no supplies. Lonely defeat ending.
```

### 41. `no_test.png` — Didn't test flamethrower
```
400x400. Flamethrower sputtering wrong way, surprised hero, infected approaching. Comedy defeat pixel art.
```

### 42. `rush_burn.png` — Grabbed by rafflesia
```
400x400. Rafflesia vine grabbing hero mid-charge, flamethrower too weak. Dramatic defeat, pixel art.
```

### 43. `solo_rafflesia.png` — Alone vs boss
```
400x400. Tiny hero vs huge Rafflesia alone, scale difference obvious. Defeat ending.
```

### 44. `no_team.png` — Refused team
```
400x400. Hero walking away from cave survivors toward boss alone, sad silhouette. Defeat foreshadow.
```

### 45. `trip_rock.png` — Tripped on rock
```
400x400. Hero tripping on rock, stars around head, boss in background laughing (cartoon). Slapstick defeat pixel art.
```

### 46. `defend_swarm.png` — Defended teammates
```
400x400. Hero shielding injured teammates but overwhelmed by swarm from above. Heroic sad defeat.
```

### 47. `stab_fail.png` — Stick stab failed
```
400x400. Hero stabbing Rafflesia with stick, stick bending, no damage, boss angry. Fail ending pixel art.
```

### 48. `no_ruellia.png` — No Ruellia
```
400x400. Hero holding jar of plain water only, shrugging, boss looming. Missing item defeat.
```

### 49. `spare_final.png` — BAD ENDING (spare boss)
```
400x400. Hero sparing the Rafflesia (hand lowered, peaceful gesture) but golden apple tree crumbling to dust in background, world turning sick green. Tragic bad ending, pixel art, no text.
```

### 50. `good_win.png` — GOOD ENDING
```
400x400. Hero planting glowing golden seed, small golden apple tree growing fast, sunrise, survivors cheering in background. Hopeful victory ending, bright colors, pixel art RPG, no text.
```

---

# Quick order (recommended)

1 (960×640)  
3. Ending background (960×. Title screen (960×640)  
2. Battle field640)  
4. Logo  
5. Player + 5 enemy sprites  
6. Apple tree + rafflesia story scene  
7. Good + spare ending images  
8. Rest of story + items + other endings  

---

# After Gemini gives you images

1. Rename file exactly as shown (`battle_field.png`, etc.).  
2. Put in `assets/` folders (create folders from `ASSETS_GUIDE.md`).  
3. Resize to exact pixels if needed.  
4. Tell Cursor: **“load my assets folder into the game”** to hook them up in code.

---

# If Gemini won’t do transparent background

Generate on **plain bright magenta** background, then remove it in Photopea: *Select → Color range → delete magenta*.

Or ask: **“solid flat #FF00FF magenta background only behind character”** for easy removal.
