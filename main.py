"""
Mind Hack Gin — ZBR outbreak adventure (Pygame).
Pokemon-style battles + weighted d20 difficulty before fights.
"""

from __future__ import annotations

import datetime
import json
import os
import sys
from enum import Enum, auto

import pygame

from assets import AssetManager
from battle import BattleScreen, Fighter, Move
from constants import (
    ACCENT,
    DICE_BAD,
    DICE_BEST,
    DICE_GOOD,
    DICE_NORMAL,
    ENDINGS,
    SCREEN_H,
    SCREEN_W,
    TEXT,
    TEXT_LIGHT,
)
from dice import roll_d20


class Mode(Enum):
    TITLE = auto()
    STORY = auto()
    CHOICE = auto()
    DICE = auto()
    BATTLE = auto()
    ENDING = auto()
    SHOP = auto()
    PRE_FIGHT = auto()
    SAVE_MENU = auto()
    LOAD_MENU = auto()


# --- Player build through story ---
class GameState:
    def __init__(self):
        self.backpack: list[str] = []
        self.has_ruellia = False
        self.has_flamethrower = False
        self.has_team = False
        self.player_hp = 100
        self.player_max_hp = 100
        self.endings_seen: list[str] = []
        self.chapter = "intro"
        self.coins = 30
        self.attack_bonus = 0
        self.armor = 0
        self.has_antidote = False
        self.has_pressure_point = False
        self.has_m79 = False
        self.m79_charges = 0
        self.items: dict[str, int] = {}


SHOP_ITEMS = [
    {"id": "medkit",         "name": "Medkit",          "cost":  15, "desc": "Restore 50 HP now"},
    {"id": "power",          "name": "Power Shard",     "cost":  20, "desc": "+8 attack damage permanently"},
    {"id": "antidote",       "name": "Antidote",        "cost":  10, "desc": "Auto-cure poison in battle"},
    {"id": "shield",         "name": "Shield Shard",    "cost":  15, "desc": "-4 damage from all enemy hits"},
    {"id": "random",         "name": "Mystery Box",     "cost":   8, "desc": "30% chance: random battle item!"},
    {"id": "pressure_point", "name": "Pressure Point",  "cost":  45, "desc": "Fighting style — replaces Punch (30%back/30%def↓/20%stun/20%miss)"},
    {"id": "m79",            "name": "M79 Launcher",    "cost":  35, "desc": "2 shells of 48 dmg — replaces Flame Burst, reverts after"},
]

USABLE_ITEMS: dict[str, dict] = {
    "Medkit":     {"desc": "Restore 40 HP",          "type": "heal",      "value": 40},
    "Elixir":     {"desc": "Restore full HP",         "type": "full_heal", "value": 0},
    "Smoke Bomb": {"desc": "Instantly escape battle", "type": "flee",      "value": 0},
    "Grenade":    {"desc": "Deal 30 dmg to enemy",    "type": "damage",    "value": 30},
}

RANDOM_ITEM_POOL = ["Medkit", "Elixir", "Smoke Bomb", "Grenade"]


PLAYER_MOVES = [
    Move("Punch", 10),
    Move("Dodge", 6),
    Move("Flame Burst", 22, "Fire vs rafflesia"),
    Move("Sap Splash", 18, "Sticky sap attack"),
]

ENEMIES = {
    "infected": ("ZBR Infected", 55, (160, 80, 120), [Move("Scratch", 18), Move("Bite", 22)]),
    "horde": ("Infected Horde", 70, (140, 60, 100), [Move("Swarm", 24), Move("Grab", 20)]),
    "rafflesia_young": ("Rafflesia", 80, (200, 40, 80), [Move("Spore", 22), Move("Vine Lash", 26)]),
    "rafflesia_strong": ("Giant Rafflesia", 100, (180, 30, 70), [Move("Crush", 30), Move("Spore Cloud", 24)]),
    "rafflesia_final": ("Corrupted Rafflesia", 75, (160, 20, 60), [Move("Devour", 32), Move("Root Bind", 28)]),
}


def player_fighter(gs: GameState) -> Fighter:
    if gs.has_pressure_point:
        moves = [Move("Pressure Point", 0), Move("Dodge", 8), Move("Heal", 0)]
    else:
        moves = [Move("Punch", 10), Move("Dodge", 8), Move("Heal", 0)]
    if gs.has_m79 and gs.m79_charges > 0:
        moves.append(Move("M79 Shot", 48, "Grenade launcher"))
    elif gs.has_flamethrower:
        moves.append(Move("Flame Burst", 24))
    if "sap in a jar" in gs.backpack:
        moves.append(Move("Sap Splash", 16))
    f = Fighter("Survivor", gs.player_max_hp, moves[:4], (80, 140, 220),
                attack_bonus=gs.attack_bonus, armor=gs.armor, has_antidote=gs.has_antidote)
    f.hp = gs.player_hp
    return f


def make_enemy(key: str, mult: float) -> Fighter:
    name, hp, color, moves = ENEMIES[key]
    hp = int(hp * mult)
    return Fighter(name, hp, moves, color)


# Story nodes: (text lines, choices) or special
STORY = {
    "intro": {
        "lines": [
            "The world is in danger — a biohazard outbreak has mutated plants and humans.",
            "Plants are 10× stronger. Humans carry Zoonotic Bridge Rafflesia (ZBR).",
            "Everything starts at 12:00 PM.",
        ],
        "choices": [("Save the world", "save"), ("Do nothing", "nothing")],
    },
    "shovel": {
        "lines": ["You found Ruellia tuberosa on the path."],
        "choices": [("Pick it", "pick"), ("Leave it", "leave")],
    },
    "biohazard": {
        "lines": [
            "You pass a biohazard zone.",
            "Inside: an apple tree wrapped in rafflesia.",
        ],
        "choices": [("Go in", "yes"), ("Stay out", "no")],
    },
    "note": {
        "lines": [
            "A note: the only cure is the golden apple.",
            "Rafflesia will destroy it in 2 days. Its weakness is fire.",
        ],
        "choices": [("Continue", "continue")],
    },
    "horde_choice": {
        "lines": ["A group of infected approaches!"],
        "choices": [("Fight", "fight"), ("Hide", "hide"), ("Run", "run")],
    },
    "camp": {
        "lines": ["You find an abandoned camp."],
        "choices": [("Investigate", "yes"), ("Skip it", "no")],
    },
    "craft": {
        "lines": [
            "Ingredients: pine sap, lighter, stick.",
            "Craft a flamethrower?",
        ],
        "choices": [("Craft", "yes"), ("Wait", "no")],
    },
    "test_weapon": {
        "lines": ["Test the flamethrower on infected?"],
        "choices": [("Test it", "yes"), ("Skip test", "no")],
    },
    "plan": {
        "lines": [
            "11:00 AM — the rafflesia grows. The golden apple is almost gone.",
            "You're not strong enough for a direct fight yet.",
        ],
        "choices": [("Fight anyway", "yes"), ("Think of a plan", "no")],
    },
    "rush": {
        "lines": [
            "The golden apple is destroyed. The rafflesia grabs at you!",
        ],
        "choices": [("Burn it", "burn"), ("Move out", "dodge")],
    },
    "teammate": {
        "lines": ["You need help. Search for survivors?"],
        "choices": [("Look for teammate", "yes"), ("Go alone", "no")],
    },
    "cave": {
        "lines": [
            "Survivors hide in a cave — they want to join you.",
            "1½ days have passed.",
        ],
        "choices": [("Join them", "yes"), ("Refuse", "no")],
    },
    "team_fight": {
        "lines": [
            "1:00 AM — the golden apple is gone. The rafflesia awaits.",
        ],
        "choices": [("Go in with team", "go"), ("Stay back", "back")],
    },
    "swarm": {
        "lines": ["Infected swarm! Teammates are down."],
        "choices": [("Rush in", "1"), ("Defend team", "2")],
    },
    "final_plan": {
        "lines": [
            "Out of fuel. A puddle of water gives you an idea…",
            "Use sap jar + Ruellia tuberosa?",
        ],
        "choices": [("Stick stab (fail)", "1"), ("Jar plan", "2")],
    },
}


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Mind Hack Gin — ZBR Outbreak")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.fonts = {
            "title": pygame.font.SysFont("arial", 42, bold=True),
            "heading": pygame.font.SysFont("arial", 28, bold=True),
            "text": pygame.font.SysFont("arial", 22),
            "small": pygame.font.SysFont("arial", 18),
            "tiny": pygame.font.SysFont("arial", 14),
        }
        self.gs = GameState()
        self.mode = Mode.TITLE
        self.story_key = "intro"
        self.choice_index = 0
        self.lines_shown: list[str] = []
        self.line_index = 0
        self.battle: BattleScreen | None = None
        self.pending_battle: str | None = None
        self.dice_value = 0
        self.dice_tier = ""
        self.dice_label = ""
        self.dice_mult = 1.0
        self.dice_timer = 0
        self.dice_spin = 0
        self.ending_key: str | None = None
        self.after_battle: str | None = None
        self.final_spare_available = False
        self.shop_cursor = 0
        self._after_shop = ""
        self.shop_message = ""
        self.pre_fight_cursor = 0
        self.item_menu_open = False
        self.item_cursor = 0
        self.assets = AssetManager()
        self.save_slot_cursor = 0
        self.save_message = ""
        self._pre_save_mode: Mode | None = None

    def run(self):
        while True:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle(event)
            self._update(dt)
            self._draw()
            pygame.display.flip()

    def _handle(self, event: pygame.event.Event):
        if event.type != pygame.KEYDOWN:
            return
        if self.mode == Mode.TITLE and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.mode = Mode.STORY
            self._load_story("intro")
        elif self.mode == Mode.TITLE and event.key == pygame.K_l:
            self.save_slot_cursor = 0
            self.save_message = ""
            self.mode = Mode.LOAD_MENU
        elif self.mode == Mode.LOAD_MENU:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.save_slot_cursor = (self.save_slot_cursor - 1) % 3
                self.save_message = ""
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.save_slot_cursor = (self.save_slot_cursor + 1) % 3
                self.save_message = ""
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self._load_game(self.save_slot_cursor + 1):
                    self.save_message = ""
                else:
                    self.save_message = "No save in this slot!"
            elif event.key == pygame.K_ESCAPE:
                self.mode = Mode.TITLE
                self.save_message = ""
        elif self.mode == Mode.SAVE_MENU:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.save_slot_cursor = (self.save_slot_cursor - 1) % 3
                self.save_message = ""
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.save_slot_cursor = (self.save_slot_cursor + 1) % 3
                self.save_message = ""
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                slot = self.save_slot_cursor + 1
                self._save_game(slot)
                self.save_message = f"Saved to Slot {slot}!"
            elif event.key == pygame.K_ESCAPE:
                self.mode = self._pre_save_mode or Mode.STORY
                self._pre_save_mode = None
                self.save_message = ""
        elif self.mode == Mode.ENDING and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            saved_endings = list(self.gs.endings_seen)
            self.mode = Mode.TITLE
            self.gs = GameState()
            self.gs.endings_seen = saved_endings
            self.item_menu_open = False
        elif self.mode == Mode.STORY and event.key == pygame.K_F5:
            self._pre_save_mode = self.mode
            self.mode = Mode.SAVE_MENU
            self.save_slot_cursor = 0
            self.save_message = ""
        elif self.mode == Mode.STORY and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._story_advance()
        elif self.mode == Mode.CHOICE:
            if event.key == pygame.K_F5:
                self._pre_save_mode = self.mode
                self.mode = Mode.SAVE_MENU
                self.save_slot_cursor = 0
                self.save_message = ""
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.choice_index = (self.choice_index - 1) % len(self._choices())
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.choice_index = (self.choice_index + 1) % len(self._choices())
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._pick_choice()
        elif self.mode == Mode.PRE_FIGHT:
            if event.key == pygame.K_F5:
                self._pre_save_mode = self.mode
                self.mode = Mode.SAVE_MENU
                self.save_slot_cursor = 0
                self.save_message = ""
            elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                self.pre_fight_cursor = 1 - self.pre_fight_cursor
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.pre_fight_cursor == 0:
                    self._open_shop("__dice__")
                else:
                    self.mode = Mode.DICE
        elif self.mode == Mode.SHOP:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.shop_cursor = (self.shop_cursor - 1) % len(SHOP_ITEMS)
                self.shop_message = ""
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.shop_cursor = (self.shop_cursor + 1) % len(SHOP_ITEMS)
                self.shop_message = ""
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._buy_item()
            elif event.key == pygame.K_ESCAPE:
                self.shop_message = ""
                if self._after_shop == "__dice__":
                    self.mode = Mode.PRE_FIGHT
                else:
                    self._load_story(self._after_shop)
        elif self.mode == Mode.DICE and event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.dice_timer <= 0:
            self._start_pending_battle()
        elif self.mode == Mode.BATTLE and self.battle:
            if self.item_menu_open:
                item_names = [k for k, v in self.gs.items.items() if v > 0]
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    self.item_menu_open = False
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.item_cursor = (self.item_cursor - 1) % max(1, len(item_names))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.item_cursor = (self.item_cursor + 1) % max(1, len(item_names))
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and item_names:
                    self._use_selected_item()
            elif event.key == pygame.K_q and self.battle.phase == "menu" and not self.battle.result:
                if self.gs.items:
                    self.item_menu_open = True
                    self.item_cursor = 0
            else:
                self.battle.handle_event(event)
                if self.battle.result and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._battle_done()

    def _choices(self):
        return STORY[self.story_key]["choices"]

    def _load_story(self, key: str):
        self.story_key = key
        self.gs.chapter = key
        data = STORY[key]
        self.lines_shown = list(data["lines"])
        self.line_index = 0
        if len(data["choices"]) == 1 and data["choices"][0][1] == "continue":
            self.mode = Mode.STORY
        else:
            self.mode = Mode.CHOICE if data["choices"] else Mode.STORY
        self.choice_index = 0

    def _story_advance(self):
        if self.line_index < len(self.lines_shown) - 1:
            self.line_index += 1
        else:
            data = STORY[self.story_key]
            if data["choices"]:
                self.mode = Mode.CHOICE
            else:
                self._pick_choice_auto()

    def _pick_choice_auto(self):
        pass

    def _pick_choice(self):
        _, action = self._choices()[self.choice_index]
        self._apply_choice(action)

    def _apply_choice(self, action: str):
        gs = self.gs
        key = self.story_key

        if key == "intro":
            if action == "nothing":
                return self._end("bad_start")
            self._load_story("shovel")

        elif key == "shovel":
            if action == "pick":
                gs.has_ruellia = True
                gs.backpack.append("Ruellia tuberosa")
            self._load_story("biohazard")

        elif key == "biohazard":
            if action == "no":
                return self._end("sundew")
            self._load_story("note")

        elif key == "note":
            self._queue_battle("rafflesia_young", after="after_first_rafflesia")

        elif key == "horde_choice":
            if action == "fight":
                return self._end("fight_horde")
            if action == "run":
                return self._end("run_horde")
            gs.backpack.append("sap in a jar")
            self._load_story("camp")

        elif key == "camp":
            if action == "no":
                return self._end("no_camp")
            gs.backpack.append("lighter")
            self._open_shop("craft")

        elif key == "craft":
            gs.backpack.append("stick")
            if action == "yes":
                gs.has_flamethrower = True
                for used in ("sap in a jar", "lighter", "stick"):
                    if used in gs.backpack:
                        gs.backpack.remove(used)
                gs.backpack.append("flamethrower")
            self._load_story("test_weapon")

        elif key == "test_weapon":
            if action == "no":
                return self._end("no_test")
            self._queue_battle("infected", after="post_test")

        elif key == "plan":
            if action == "yes":
                self._queue_battle("rafflesia_strong", after="fight_early", can_flee=False)
            else:
                self._load_story("rush")

        elif key == "rush":
            if action == "burn":
                return self._end("rush_burn")
            self._load_story("teammate")

        elif key == "teammate":
            if action == "no":
                return self._end("no_team")
            self._load_story("cave")

        elif key == "cave":
            if action == "no":
                return self._end("no_team")
            gs.has_team = True
            self._load_story("team_fight")

        elif key == "team_fight":
            if action == "back":
                return self._end("trip_rock")
            self._queue_battle("rafflesia_strong", after="post_team", can_flee=False)

        elif key == "swarm":
            if action == "2":
                return self._end("defend_swarm")
            self._queue_battle("horde", after="pre_final")

        elif key == "final_plan":
            if action == "1":
                return self._end("stab_fail")
            if not gs.has_ruellia:
                return self._end("no_ruellia")
            self._queue_battle("rafflesia_final", after="final_boss", can_flee=False, spare_kill=True)

    def _queue_battle(
        self,
        enemy_key: str,
        after: str,
        can_flee: bool = True,
        spare_kill: bool = False,
    ):
        self.pending_battle = enemy_key
        self.after_battle = after
        self._battle_can_flee = can_flee
        self.final_spare_available = spare_kill
        self.mode = Mode.PRE_FIGHT
        self.pre_fight_cursor = 1
        self.dice_timer = 90
        self.dice_spin = 0
        self.dice_value = 0

    def _roll_dice_anim(self):
        self.dice_value, self.dice_tier, self.dice_label, self.dice_mult = roll_d20()

    def _start_pending_battle(self):
        enemy = make_enemy(self.pending_battle or "infected", self.dice_mult)
        special = None
        if self.final_spare_available:
            special = [Move("Spare", 0, "Let it live"), Move("Finish", 30, "End it")]
        enemy_key = self.pending_battle or "infected"
        self.battle = BattleScreen(
            player_fighter(self.gs),
            enemy,
            self.dice_value,
            self.dice_label,
            can_flee=self._battle_can_flee,
            special_moves=special,
            background=self.assets.battle_bg,
            player_sprite=self.assets.player_sprite,
            enemy_sprite=self.assets.enemy_sprite(enemy_key),
            m79_charges=self.gs.m79_charges if self.gs.has_m79 else 0,
        )
        self.mode = Mode.BATTLE

    def _battle_done(self):
        b = self.battle
        if not b:
            return
        self.item_menu_open = False
        gs = self.gs
        gs.player_hp = b.player.hp
        if gs.has_m79:
            gs.m79_charges = b.m79_charges
            if gs.m79_charges <= 0:
                gs.has_m79 = False

        if b.result == "win":
            gs.coins += 20

        if b.result == "lose":
            return self._end(self._death_for_chapter())

        if self.after_battle == "after_first_rafflesia":
            if b.result == "flee":
                gs.player_hp = min(gs.player_max_hp, max(25, b.player.hp))
                self.battle = None
                self._load_story("horde_choice")
                return
            if b.result == "win":
                self.battle = None
                self._load_story("horde_choice")
                return
            return self._end("fight_early")

        if self.after_battle == "fight_early":
            if b.result == "win":
                self.battle = None
                self._load_story("rush")
                return
            return self._end("fight_early")

        if self.after_battle == "post_test":
            self.battle = None
            self._load_story("plan")
            return

        if self.after_battle == "post_team":
            self.battle = None
            self._load_story("swarm")
            return

        if self.after_battle == "pre_final":
            self.battle = None
            self._load_story("final_plan")
            return

        if self.after_battle == "final_boss":
            if b.result == "spare":
                return self._end("spare_final")
            if b.result == "win":
                return self._end("good_win")
            return self._end("no_ruellia")

        self.mode = Mode.STORY

    def _death_for_chapter(self) -> str:
        m = {
            "rafflesia_young": "fight_early",
            "infected": "no_test",
            "horde": "defend_swarm",
            "rafflesia_strong": "solo_rafflesia",
            "rafflesia_final": "no_ruellia",
        }
        return m.get(self.pending_battle or "", "fight_early")

    def _end(self, key: str):
        if key not in self.gs.endings_seen:
            self.gs.endings_seen.append(key)
        self.ending_key = key
        self.mode = Mode.ENDING

    def _update(self, dt: int):
        if self.mode == Mode.DICE:
            self.dice_timer -= 1
            self.dice_spin = (self.dice_spin + 1) % 20
            if self.dice_timer == 45:
                self._roll_dice_anim()
            if self.dice_timer <= 0 and self.dice_value == 0:
                self._roll_dice_anim()
        if self.mode == Mode.BATTLE and self.battle:
            self.battle.update()

    def _draw(self):
        self.screen.fill((32, 48, 72))
        if self.mode == Mode.TITLE:
            self._draw_title()
        elif self.mode == Mode.STORY:
            self._draw_story()
        elif self.mode == Mode.CHOICE:
            self._draw_choice()
        elif self.mode == Mode.DICE:
            self._draw_dice()
        elif self.mode == Mode.PRE_FIGHT:
            self._draw_pre_fight()
        elif self.mode == Mode.BATTLE and self.battle:
            self.battle.draw(self.screen, self.fonts)
            if self.item_menu_open:
                self._draw_item_menu()
        elif self.mode == Mode.ENDING:
            self._draw_ending()
        elif self.mode == Mode.SHOP:
            self._draw_shop()
        elif self.mode == Mode.SAVE_MENU:
            self._draw_slot_menu(is_load=False)
        elif self.mode == Mode.LOAD_MENU:
            self._draw_slot_menu(is_load=True)

    def _draw_outlined(self, font, text, color, outline_color, cx, y, outline=2):
        surf = font.render(text, True, color)
        out = font.render(text, True, outline_color)
        x = cx - surf.get_width() // 2
        for dx in range(-outline, outline + 1):
            for dy in range(-outline, outline + 1):
                if dx or dy:
                    self.screen.blit(out, (x + dx, y + dy))
        self.screen.blit(surf, (x, y))

    def _draw_title(self):
        self.assets.blit_fullscreen(self.screen, self.assets.title_bg)
        cx = SCREEN_W // 2
        if self.assets.logo:
            logo = pygame.transform.smoothscale(self.assets.logo, (500, 120))
            self.screen.blit(logo, (cx - logo.get_width() // 2, 80))
        else:
            self._draw_outlined(self.fonts["title"], "Mind Hack Gin", ACCENT, (0, 0, 0), cx, 100, outline=3)
        self._draw_outlined(self.fonts["text"], "ZBR Outbreak — Roll the dice. Fight. Survive.", TEXT_LIGHT, (0, 0, 0), cx, 250, outline=2)
        self._draw_outlined(self.fonts["small"], "Press Enter to start", TEXT_LIGHT, (0, 0, 0), cx, 400, outline=2)
        if any(self._get_save_info(s) for s in range(1, 4)):
            self._draw_outlined(self.fonts["small"], "L — Load saved game", TEXT_LIGHT, (0, 0, 0), cx, 426, outline=2)
        seen_text = f"Endings discovered: {len(self.gs.endings_seen)} / {len(ENDINGS)}"
        self._draw_outlined(self.fonts["tiny"], seen_text, TEXT_LIGHT, (0, 0, 0), cx, 456, outline=2)

    def _draw_story_panel(self):
        story_img = self.assets.story_image(self.story_key)
        if story_img:
            img_rect = pygame.Rect(40, 24, SCREEN_W - 80, 240)
            self.assets.blit_centered(self.screen, story_img, img_rect)
        panel_y = 280 if story_img else 80
        panel_h = SCREEN_H - panel_y - 40
        text_rect = pygame.Rect(40, panel_y, SCREEN_W - 80, panel_h)
        if self.assets.story_overlay:
            overlay = pygame.transform.smoothscale(
                self.assets.story_overlay, (text_rect.width, text_rect.height)
            )
            self.screen.blit(overlay, text_rect.topleft)
            # Inset for the decorative frame border so text stays inside.
            return text_rect.inflate(-200, -100)
        pygame.draw.rect(self.screen, (248, 248, 252), text_rect, border_radius=12)
        return text_rect.inflate(-24, -24)

    def _draw_backpack(self, x: int, y: int):
        if not self.gs.backpack:
            self.screen.blit(
                self.fonts["small"].render("Backpack: (empty)", True, (80, 80, 100)), (x, y)
            )
            return
        self.screen.blit(self.fonts["small"].render("Backpack:", True, (80, 80, 100)), (x, y))
        ix = x + 100
        for item in self.gs.backpack:
            icon = self.assets.item_icon(item)
            if icon:
                scaled = pygame.transform.smoothscale(icon, (32, 32))
                self.screen.blit(scaled, (ix, y - 4))
                ix += 36
            else:
                label = self.fonts["tiny"].render(item[:8], True, (80, 80, 100))
                self.screen.blit(label, (ix, y + 4))
                ix += label.get_width() + 8

    def _wrap_text(self, font: pygame.font.Font, text: str, max_w: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        line = ""
        for w in words:
            test = f"{line} {w}".strip()
            if font.size(test)[0] <= max_w:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines

    def _blit_wrapped(self, font: pygame.font.Font, text: str, x: int, y: int, max_w: int, color=TEXT) -> int:
        lh = font.get_linesize()
        for ln in self._wrap_text(font, text, max_w):
            self.screen.blit(font.render(ln, True, color), (x, y))
            y += lh
        return y

    def _draw_story(self):
        text_rect = self._draw_story_panel()
        line = self.lines_shown[self.line_index] if self.lines_shown else ""
        self._blit_wrapped(
            self.fonts["text"], line, text_rect.x, text_rect.y + 20, text_rect.width
        )
        self._draw_backpack(text_rect.x, text_rect.bottom - 48)
        hint = self.fonts["small"].render("Enter — continue   F5 — Save", True, (100, 100, 120))
        self.screen.blit(hint, (text_rect.x, text_rect.bottom - 22))

    def _draw_choice(self):
        text_rect = self._draw_story_panel()
        line = self.lines_shown[self.line_index] if self.lines_shown else ""
        next_y = self._blit_wrapped(
            self.fonts["text"], line, text_rect.x, text_rect.y + 20, text_rect.width
        )
        choices = self._choices()
        y = next_y + 12
        for i, (label, _) in enumerate(choices):
            col = ACCENT if i == self.choice_index else TEXT
            self.screen.blit(self.fonts["text"].render(f"  {label}", True, col), (text_rect.x, y))
            y += 32
        self._draw_backpack(text_rect.x, text_rect.bottom - 48)
        self.screen.blit(
            self.fonts["tiny"].render("Up/Down — select   Enter — confirm   F5 — Save", True, (80, 80, 120)),
            (text_rect.x, text_rect.bottom - 22),
        )

    def _draw_dice(self):
        colors = {
            "worst": DICE_BAD,
            "normal": DICE_NORMAL,
            "good": DICE_GOOD,
            "best": DICE_BEST,
        }
        tier = self.dice_tier or "normal"
        face = self.dice_value if self.dice_timer <= 0 else (self.dice_spin % 20) + 1
        col = colors.get(tier, DICE_NORMAL)
        cx, cy = SCREEN_W // 2, 260
        glow = None
        if self.dice_timer <= 0:
            if tier == "worst":
                glow = self.assets.dice_glow_hard
            elif tier == "best":
                glow = self.assets.dice_glow_lucky
        if glow:
            g = pygame.transform.smoothscale(glow, (140, 140))
            self.screen.blit(g, (cx - 70, cy - 70))
        if self.assets.dice_d20:
            die = pygame.transform.smoothscale(self.assets.dice_d20, (120, 120))
            self.screen.blit(die, (cx - 60, cy - 60))
        else:
            pygame.draw.rect(self.screen, col, (cx - 60, cy - 60, 120, 120), border_radius=16)
        num = self.fonts["title"].render(str(face), True, TEXT_LIGHT)
        self.screen.blit(num, (cx - num.get_width() // 2, cy - num.get_height() // 2))
        title = self.fonts["heading"].render("Rolling d20 for next fight…", True, TEXT_LIGHT)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 120))
        if self.dice_timer <= 0:
            lbl = self.fonts["text"].render(f"{self.dice_label}  (rolled {self.dice_value})", True, TEXT_LIGHT)
            self.screen.blit(lbl, (SCREEN_W // 2 - lbl.get_width() // 2, 360))
            hint = self.fonts["small"].render("Enter — start battle", True, TEXT_LIGHT)
            self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 420))
        probs = self.fonts["tiny"].render(
            "Odds: 1–6 hard 40% | 7–10 normal 30% | 11–16 easier 20% | 17–20 lucky 10%",
            True,
            (200, 200, 220),
        )
        self.screen.blit(probs, (SCREEN_W // 2 - probs.get_width() // 2, 500))

    def _draw_ending(self):
        key = self.ending_key or "fight_early"
        text = ENDINGS.get(key, "Ending")
        self.assets.blit_fullscreen(self.screen, self.assets.ending_bg)
        ending_img = self.assets.ending_image(key)
        if ending_img:
            img_rect = pygame.Rect(SCREEN_W // 2 - 200, 80, 400, 400)
            self.assets.blit_centered(self.screen, ending_img, img_rect)
        panel = pygame.Rect(60, 500, SCREEN_W - 120, 140)
        pygame.draw.rect(self.screen, (40, 20, 32), panel, border_radius=12)
        head = self.fonts["heading"].render("ENDING", True, ACCENT)
        body = self.fonts["text"].render(text, True, TEXT_LIGHT)
        self.screen.blit(head, (SCREEN_W // 2 - head.get_width() // 2, panel.y + 12))
        self.screen.blit(body, (80, panel.y + 48))
        n = len(self.gs.endings_seen)
        tot = len(ENDINGS)
        prog = self.fonts["small"].render(f"Endings collected: {n} / {tot}", True, TEXT_LIGHT)
        self.screen.blit(prog, (SCREEN_W // 2 - prog.get_width() // 2, panel.y + 84))
        hint = self.fonts["small"].render("Enter — return to title", True, TEXT_LIGHT)
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, panel.y + 114))


    def _draw_pre_fight(self):
        self.screen.fill((28, 36, 56))
        enemy_name = ENEMIES.get(self.pending_battle or "", ("Unknown Enemy",))[0]
        title = self.fonts["heading"].render("Battle Approaches!", True, ACCENT)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 110))
        sub = self.fonts["text"].render(f"Prepare to face: {enemy_name}", True, TEXT_LIGHT)
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 168))
        coins_s = self.fonts["small"].render(f"Coins: {self.gs.coins}  |  Items: {sum(self.gs.items.values())}",
                                             True, (255, 215, 0))
        self.screen.blit(coins_s, (SCREEN_W // 2 - coins_s.get_width() // 2, 210))
        options = ["Visit Shop", "Roll Dice & Fight"]
        for i, opt in enumerate(options):
            sel = i == self.pre_fight_cursor
            rect = pygame.Rect(SCREEN_W // 2 - 180, 280 + i * 64, 360, 50)
            pygame.draw.rect(self.screen, (55, 75, 110) if sel else (38, 54, 82), rect, border_radius=8)
            if sel:
                pygame.draw.rect(self.screen, ACCENT, rect, 2, border_radius=8)
            col = ACCENT if sel else TEXT_LIGHT
            s = self.fonts["text"].render(opt, True, col)
            self.screen.blit(s, (rect.x + rect.width // 2 - s.get_width() // 2,
                                 rect.y + rect.height // 2 - s.get_height() // 2))
        hint = self.fonts["small"].render("Up/Down — select   Enter — confirm", True, TEXT_LIGHT)
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 50))

    def _draw_item_menu(self):
        panel = pygame.Rect(SCREEN_W // 2 - 220, SCREEN_H // 2 - 130, 440, 260)
        pygame.draw.rect(self.screen, (24, 34, 54), panel, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT, panel, 2, border_radius=10)
        title = self.fonts["small"].render("Items  (Q / Esc to close)", True, ACCENT)
        self.screen.blit(title, (panel.x + 14, panel.y + 12))
        item_names = [k for k, v in self.gs.items.items() if v > 0]
        if not item_names:
            msg = self.fonts["text"].render("No items!", True, TEXT_LIGHT)
            self.screen.blit(msg, (panel.x + panel.width // 2 - msg.get_width() // 2, panel.y + 110))
        else:
            for i, name in enumerate(item_names):
                y = panel.y + 50 + i * 44
                sel = i == self.item_cursor
                col = ACCENT if sel else TEXT_LIGHT
                idef = USABLE_ITEMS.get(name, {})
                label = f"{'> ' if sel else '  '}{name} (x{self.gs.items[name]})  —  {idef.get('desc', '')}"
                self.screen.blit(self.fonts["small"].render(label, True, col), (panel.x + 16, y))
        hint = self.fonts["tiny"].render("Up/Down — select   Enter — use", True, TEXT_LIGHT)
        self.screen.blit(hint, (panel.x + 14, panel.bottom - 26))

    def _use_selected_item(self):
        import random as _rnd
        item_names = [k for k, v in self.gs.items.items() if v > 0]
        if not item_names or self.item_cursor >= len(item_names):
            return
        name = item_names[self.item_cursor]
        idef = USABLE_ITEMS.get(name)
        if not idef:
            return
        self.gs.items[name] -= 1
        if self.gs.items[name] <= 0:
            del self.gs.items[name]
        self.item_menu_open = False
        b = self.battle
        if not b:
            return
        t = idef["type"]
        if t == "heal":
            b.player.hp = min(b.player.max_hp, b.player.hp + idef["value"])
            b.message = f"Used {name}! +{idef['value']} HP. Enemy attacks!"
            b.phase = "player_anim"
            b._anim_timer = 28
        elif t == "full_heal":
            b.player.hp = b.player.max_hp
            b.message = f"Used {name}! Full HP! Enemy attacks!"
            b.phase = "player_anim"
            b._anim_timer = 28
        elif t == "flee":
            b.result = "flee"
            b.message = f"Used {name}! Escaped safely!"
            b.phase = "end"
        elif t == "damage":
            b.enemy.take_damage(idef["value"])
            b.enemy_shake = 14
            b.message = f"Used {name}! Dealt {idef['value']} dmg. Enemy attacks!"
            b.phase = "player_anim"
            b._anim_timer = 28

    def _open_shop(self, after: str):
        self.mode = Mode.SHOP
        self.shop_cursor = 0
        self._after_shop = after
        self.shop_message = ""

    def _buy_item(self):
        gs = self.gs
        item = SHOP_ITEMS[self.shop_cursor]
        if gs.coins < item["cost"]:
            self.shop_message = "Not enough coins!"
            return
        gs.coins -= item["cost"]
        if item["id"] == "medkit":
            gs.player_hp = min(gs.player_max_hp, gs.player_hp + 50)
            self.shop_message = f"Restored HP! ({gs.player_hp}/{gs.player_max_hp})"
        elif item["id"] == "power":
            gs.attack_bonus += 8
            self.shop_message = f"+8 attack! (total +{gs.attack_bonus})"
        elif item["id"] == "antidote":
            gs.has_antidote = True
            self.shop_message = "Antidote equipped — poison won't affect you!"
        elif item["id"] == "shield":
            gs.armor += 4
            self.shop_message = f"-4 damage! (total -{gs.armor})"
        elif item["id"] == "random":
            import random
            if random.random() < 0.30:
                picked = random.choice(RANDOM_ITEM_POOL)
                gs.items[picked] = gs.items.get(picked, 0) + 1
                self.shop_message = f"Lucky! Got: {picked}!"
            else:
                self.shop_message = "No luck... (30% chance)"
        elif item["id"] == "pressure_point":
            if gs.has_pressure_point:
                self.shop_message = "You already know Pressure Point!"
                gs.coins += item["cost"]
            else:
                gs.has_pressure_point = True
                self.shop_message = "Pressure Point unlocked! Replaces Punch."
        elif item["id"] == "m79":
            gs.has_m79 = True
            gs.m79_charges = 2
            self.shop_message = "M79 loaded! 2 shells — replaces Flame Burst until spent."

    def _draw_shop(self):
        self.screen.fill((28, 40, 60))
        title = self.fonts["heading"].render("Camp Shop", True, ACCENT)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 30))

        coins_surf = self.fonts["text"].render(f"Coins: {self.gs.coins}", True, (255, 215, 0))
        self.screen.blit(coins_surf, (SCREEN_W // 2 - coins_surf.get_width() // 2, 72))

        stats_surf = self.fonts["small"].render(
            f"HP {self.gs.player_hp}/{self.gs.player_max_hp}   ATK +{self.gs.attack_bonus}   "
            f"ARM -{self.gs.armor}   Antidote: {'YES' if self.gs.has_antidote else 'NO'}",
            True, TEXT_LIGHT,
        )
        self.screen.blit(stats_surf, (SCREEN_W // 2 - stats_surf.get_width() // 2, 104))

        for i, item in enumerate(SHOP_ITEMS):
            y = 130 + i * 66
            sel = i == self.shop_cursor
            rect = pygame.Rect(SCREEN_W // 2 - 300, y, 600, 58)
            pygame.draw.rect(self.screen, (55, 75, 110) if sel else (38, 54, 82), rect, border_radius=8)
            if sel:
                pygame.draw.rect(self.screen, ACCENT, rect, 2, border_radius=8)
            can_afford = self.gs.coins >= item["cost"]
            name_col = ACCENT if sel else (TEXT_LIGHT if can_afford else (120, 120, 130))
            cost_col = (255, 215, 0) if can_afford else (160, 100, 100)
            self.screen.blit(self.fonts["text"].render(item["name"], True, name_col), (rect.x + 16, y + 6))
            cost_s = self.fonts["text"].render(f"{item['cost']} coins", True, cost_col)
            self.screen.blit(cost_s, (rect.right - cost_s.get_width() - 16, y + 6))
            self.screen.blit(self.fonts["small"].render(item["desc"], True, (170, 180, 200)), (rect.x + 16, y + 32))

        if self.shop_message:
            msg = self.fonts["text"].render(self.shop_message, True, (100, 240, 140))
            self.screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, SCREEN_H - 100))

        hint = self.fonts["small"].render("Up/Down — select   Enter — buy   Esc — leave shop", True, TEXT_LIGHT)
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 50))

    # ── Save / Load ────────────────────────────────────────────────────────
    def _save_path(self, slot: int) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), f"save_{slot}.json")

    def _get_save_info(self, slot: int) -> dict | None:
        path = self._save_path(slot)
        if not os.path.exists(path):
            return None
        try:
            with open(path) as f:
                data = json.load(f)
            gs_d = data.get("gs", {})
            return {
                "timestamp": data.get("timestamp", "Unknown"),
                "chapter":   gs_d.get("chapter", "?"),
                "hp":        gs_d.get("player_hp", 0),
                "max_hp":    gs_d.get("player_max_hp", 100),
                "coins":     gs_d.get("coins", 0),
            }
        except Exception:
            return None

    def _save_game(self, slot: int) -> None:
        gs = self.gs
        saved_mode = (self._pre_save_mode or self.mode).name
        data = {
            "timestamp":            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "chapter":              gs.chapter,
            "mode":                 saved_mode,
            "story_key":            self.story_key,
            "line_index":           self.line_index,
            "pending_battle":       self.pending_battle,
            "after_battle":         self.after_battle,
            "battle_can_flee":      getattr(self, "_battle_can_flee", True),
            "final_spare_available": self.final_spare_available,
            "gs": {
                "backpack":          gs.backpack,
                "has_ruellia":       gs.has_ruellia,
                "has_flamethrower":  gs.has_flamethrower,
                "has_team":          gs.has_team,
                "player_hp":         gs.player_hp,
                "player_max_hp":     gs.player_max_hp,
                "endings_seen":      gs.endings_seen,
                "chapter":           gs.chapter,
                "coins":             gs.coins,
                "attack_bonus":      gs.attack_bonus,
                "armor":             gs.armor,
                "has_antidote":      gs.has_antidote,
                "has_pressure_point": gs.has_pressure_point,
                "has_m79":           gs.has_m79,
                "m79_charges":       gs.m79_charges,
                "items":             gs.items,
            },
        }
        with open(self._save_path(slot), "w") as f:
            json.dump(data, f, indent=2)

    def _load_game(self, slot: int) -> bool:
        path = self._save_path(slot)
        if not os.path.exists(path):
            return False
        try:
            with open(path) as f:
                data = json.load(f)
            gs_d = data["gs"]
            gs = GameState()
            gs.backpack          = gs_d["backpack"]
            gs.has_ruellia       = gs_d["has_ruellia"]
            gs.has_flamethrower  = gs_d["has_flamethrower"]
            gs.has_team          = gs_d["has_team"]
            gs.player_hp         = gs_d["player_hp"]
            gs.player_max_hp     = gs_d["player_max_hp"]
            gs.endings_seen      = gs_d["endings_seen"]
            gs.chapter           = gs_d["chapter"]
            gs.coins             = gs_d["coins"]
            gs.attack_bonus      = gs_d["attack_bonus"]
            gs.armor             = gs_d["armor"]
            gs.has_antidote      = gs_d["has_antidote"]
            gs.has_pressure_point = gs_d["has_pressure_point"]
            gs.has_m79           = gs_d["has_m79"]
            gs.m79_charges       = gs_d["m79_charges"]
            gs.items             = gs_d.get("items", {})
            self.gs = gs

            self.story_key             = data["story_key"]
            self.line_index            = data.get("line_index", 0)
            self.pending_battle        = data.get("pending_battle")
            self.after_battle          = data.get("after_battle")
            self._battle_can_flee      = data.get("battle_can_flee", True)
            self.final_spare_available = data.get("final_spare_available", False)
            self.item_menu_open        = False
            self.battle                = None

            mode_name = data.get("mode", "STORY")
            if mode_name == "PRE_FIGHT":
                self.mode            = Mode.PRE_FIGHT
                self.pre_fight_cursor = 1
                self.dice_timer      = 90
                self.dice_spin       = 0
                self.dice_value      = 0
            else:
                story_data = STORY.get(self.story_key, {})
                self.lines_shown  = list(story_data.get("lines", []))
                self.choice_index = 0
                choices = story_data.get("choices", [])
                if mode_name == "CHOICE" and choices and not (len(choices) == 1 and choices[0][1] == "continue"):
                    self.mode = Mode.CHOICE
                else:
                    self.mode = Mode.STORY
            return True
        except Exception as e:
            print(f"Load failed: {e}")
            return False

    def _draw_slot_menu(self, is_load: bool) -> None:
        self.screen.fill((20, 28, 48))
        cx = SCREEN_W // 2
        title_text = "Load Game" if is_load else "Save Game"
        title = self.fonts["heading"].render(title_text, True, ACCENT)
        self.screen.blit(title, (cx - title.get_width() // 2, 60))

        for i in range(3):
            slot = i + 1
            info = self._get_save_info(slot)
            sel  = i == self.save_slot_cursor
            rect = pygame.Rect(cx - 280, 140 + i * 120, 560, 100)
            pygame.draw.rect(self.screen, (55, 75, 110) if sel else (32, 44, 68), rect, border_radius=10)
            if sel:
                pygame.draw.rect(self.screen, ACCENT, rect, 2, border_radius=10)

            slot_label = self.fonts["small"].render(f"Slot {slot}", True, ACCENT if sel else TEXT_LIGHT)
            self.screen.blit(slot_label, (rect.x + 16, rect.y + 10))

            if info:
                self.screen.blit(
                    self.fonts["small"].render(info["timestamp"], True, (180, 200, 220)),
                    (rect.x + 16, rect.y + 36),
                )
                detail = f"Chapter: {info['chapter']}   HP: {info['hp']}/{info['max_hp']}   Coins: {info['coins']}"
                self.screen.blit(
                    self.fonts["tiny"].render(detail, True, TEXT_LIGHT),
                    (rect.x + 16, rect.y + 62),
                )
            else:
                empty = self.fonts["small"].render("— Empty —", True, (100, 110, 130))
                self.screen.blit(empty, (rect.x + 16, rect.y + 36))

        if self.save_message:
            msg_color = (100, 240, 140) if "Saved" in self.save_message else (240, 100, 100)
            msg = self.fonts["text"].render(self.save_message, True, msg_color)
            self.screen.blit(msg, (cx - msg.get_width() // 2, SCREEN_H - 80))

        action = "load" if is_load else "save"
        hint_text = f"Up/Down — select   Enter — {action}   Esc — back"
        hint = self.fonts["small"].render(hint_text, True, TEXT_LIGHT)
        self.screen.blit(hint, (cx - hint.get_width() // 2, SCREEN_H - 40))


if __name__ == "__main__":
    Game().run()
