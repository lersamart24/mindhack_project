"""Load and cache game images from assets/."""

from __future__ import annotations

from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

STORY_IMAGES = {
    "intro": "story/intro_outbreak.png",
    "shovel": "story/ruellia_plant.png",
    "biohazard": "story/biohazard_gate.png",
    "note": "story/note_golden_apple.png",
    "horde_choice": "story/infected_approach.png",
    "camp": "story/abandoned_camp.png",
    "craft": "story/craft_flamethrower.png",
    "test_weapon": "story/pine_sap.png",
    "plan": "story/apple_tree_rafflesia.png",
    "rush": "story/apple_tree_rafflesia.png",
    "teammate": "story/cave_survivors.png",
    "cave": "story/cave_survivors.png",
    "team_fight": "story/team_fight.png",
    "swarm": "story/infected_approach.png",
    "final_plan": "story/water_puddle_jar.png",
}

ENEMY_SPRITES = {
    "infected": "sprites/enemy_infected.png",
    "horde": "sprites/enemy_horde.png",
    "rafflesia_young": "sprites/enemy_rafflesia_young.png",
    "rafflesia_strong": "sprites/enemy_rafflesia_giant.png",
    "rafflesia_final": "sprites/enemy_rafflesia_final.png",
}

ITEM_ICONS = {
    "Ruellia tuberosa": "items/ruellia.png",
    "sap in a jar": "items/sap_jar.png",
    "lighter": "items/lighter.png",
    "stick": "items/stick.png",
    "flamethrower": "items/flamethrower.png",
    "Elixir": "items/elixir.png",
    "Smoke Bomb": "items/smoke_bomb.png",
}

PLAYER_POSES = {
    "heal": "sprites/player_pose_heal.png",
    "m79": "sprites/player_pose_m79.png",
    "flame": "sprites/player_pose_flame.png",
    "punch": "sprites/player_pose_punch.png",
}


def _load(path: Path) -> pygame.Surface | None:
    if not path.exists():
        return None
    try:
        surf = pygame.image.load(str(path))
        return surf.convert_alpha() if surf.get_masks()[3] else surf.convert()
    except pygame.error:
        return None


def _scale(surf: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
    if surf.get_size() == size:
        return surf
    return pygame.transform.smoothscale(surf, size)


class AssetManager:
    def __init__(self) -> None:
        self._cache: dict[str, pygame.Surface | None] = {}
        self.title_bg = self.get("backgrounds/title.png")
        self.battle_bg = self.get("backgrounds/battle_field.png")
        self.ending_bg = self.get("backgrounds/ending_bg.png")
        self.story_overlay = self.get("backgrounds/story_overlay.png")
        self.logo = self.get("ui/logo.png")
        self.dice_d20 = self.get("ui/dice_d20.png")
        self.dice_glow_hard = self.get("ui/dice_glow_hard.png")
        self.dice_glow_lucky = self.get("ui/dice_glow_lucky.png")
        self.player_poses = {key: self.get(rel) for key, rel in PLAYER_POSES.items()}
        self.player_sprite = self.get("sprites/player_battle_back.png")

    def get(self, rel: str) -> pygame.Surface | None:
        if rel not in self._cache:
            self._cache[rel] = _load(ASSETS / rel)
        return self._cache[rel]

    def story_image(self, key: str) -> pygame.Surface | None:
        rel = STORY_IMAGES.get(key)
        return self.get(rel) if rel else None

    def ending_image(self, key: str) -> pygame.Surface | None:
        return self.get(f"endings/{key}.png")

    def enemy_sprite(self, key: str) -> pygame.Surface | None:
        rel = ENEMY_SPRITES.get(key)
        return self.get(rel) if rel else None

    def item_icon(self, name: str) -> pygame.Surface | None:
        rel = ITEM_ICONS.get(name)
        return self.get(rel) if rel else None

    def blit_fullscreen(self, surf: pygame.Surface, bg: pygame.Surface | None) -> None:
        if bg is None:
            return
        scaled = _scale(bg, surf.get_size())
        surf.blit(scaled, (0, 0))

    def blit_centered(
        self,
        surf: pygame.Surface,
        image: pygame.Surface | None,
        rect: pygame.Rect,
        max_size: tuple[int, int] | None = None,
    ) -> None:
        if image is None:
            return
        target = max_size or (rect.width, rect.height)
        iw, ih = image.get_size()
        scale = min(target[0] / iw, target[1] / ih, 1.0)
        w, h = max(1, int(iw * scale)), max(1, int(ih * scale))
        scaled = _scale(image, (w, h))
        x = rect.x + (rect.width - w) // 2
        y = rect.y + (rect.height - h) // 2
        surf.blit(scaled, (x, y))
