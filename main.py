"""
Mind Hack Gin — ZBR outbreak adventure (Pygame).
Pokemon-style battles + weighted d20 difficulty before fights.
"""

from __future__ import annotations

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


PLAYER_MOVES = [
    Move("Punch", 10),
    Move("Dodge", 6),
    Move("Flame Burst", 22, "Fire vs rafflesia"),
    Move("Sap Splash", 18, "Sticky sap attack"),
]

ENEMIES = {
    "infected": ("ZBR Infected", 40, (160, 80, 120), [Move("Scratch", 14), Move("Bite", 18)]),
    "horde": ("Infected Horde", 50, (140, 60, 100), [Move("Swarm", 20), Move("Grab", 16)]),
    "rafflesia_young": ("Rafflesia", 60, (200, 40, 80), [Move("Spore", 18), Move("Vine Lash", 22)]),
    "rafflesia_strong": ("Giant Rafflesia", 75, (180, 30, 70), [Move("Crush", 26), Move("Spore Cloud", 20)]),
    "rafflesia_final": ("Corrupted Rafflesia", 55, (160, 20, 60), [Move("Devour", 28), Move("Root Bind", 24)]),
}


def player_fighter(gs: GameState) -> Fighter:
    moves = [Move("Punch", 10), Move("Dodge", 8)]
    if gs.has_flamethrower:
        moves.append(Move("Flame Burst", 24))
    if "sap in a jar" in gs.backpack:
        moves.append(Move("Sap Splash", 16))
    f = Fighter("Survivor", gs.player_max_hp, moves[:4], (80, 140, 220))
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
        self.assets = AssetManager()

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
        elif self.mode == Mode.ENDING and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            saved_endings = list(self.gs.endings_seen)
            self.mode = Mode.TITLE
            self.gs = GameState()
            self.gs.endings_seen = saved_endings
        elif self.mode == Mode.STORY and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._story_advance()
        elif self.mode == Mode.CHOICE:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.choice_index = (self.choice_index - 1) % len(self._choices())
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.choice_index = (self.choice_index + 1) % len(self._choices())
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._pick_choice()
        elif self.mode == Mode.DICE and event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.dice_timer <= 0:
            self._start_pending_battle()
        elif self.mode == Mode.BATTLE and self.battle:
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
            self._load_story("craft")

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
        self.mode = Mode.DICE
        self.dice_timer = 90
        self.dice_spin = 0

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
        )
        self.mode = Mode.BATTLE

    def _battle_done(self):
        b = self.battle
        if not b:
            return
        gs = self.gs
        gs.player_hp = b.player.hp

        if b.result == "lose":
            return self._end(self._death_for_chapter())

        if self.after_battle == "after_first_rafflesia":
            if b.result == "flee":
                gs.player_hp = min(gs.player_max_hp, max(25, b.player.hp))
                self.battle = None
                self._load_story("horde_choice")
                return
            return self._end("fight_early")

        if self.after_battle == "fight_early":
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
        elif self.mode == Mode.BATTLE and self.battle:
            self.battle.draw(self.screen, self.fonts)
        elif self.mode == Mode.ENDING:
            self._draw_ending()

    def _draw_title(self):
        self.assets.blit_fullscreen(self.screen, self.assets.title_bg)
        if self.assets.logo:
            logo = pygame.transform.smoothscale(self.assets.logo, (500, 120))
            self.screen.blit(logo, (SCREEN_W // 2 - logo.get_width() // 2, 80))
        else:
            shadow = self.fonts["title"].render("Mind Hack Gin", True, (0, 0, 0))
            t = self.fonts["title"].render("Mind Hack Gin", True, ACCENT)
            self.screen.blit(shadow, (SCREEN_W // 2 - t.get_width() // 2 + 3, 100 + 3))
            self.screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 100))
        sub_shadow = self.fonts["text"].render("ZBR Outbreak — Roll the dice. Fight. Survive.", True, (0, 0, 0))
        sub = self.fonts["text"].render("ZBR Outbreak — Roll the dice. Fight. Survive.", True, TEXT_LIGHT)
        self.screen.blit(sub_shadow, (SCREEN_W // 2 - sub.get_width() // 2 + 2, 252))
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 250))

        hint_shadow = self.fonts["small"].render("Press Enter to start", True, (0, 0, 0))
        hint = self.fonts["small"].render("Press Enter to start", True, TEXT_LIGHT)
        self.screen.blit(hint_shadow, (SCREEN_W // 2 - hint.get_width() // 2 + 2, 402))
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 400))

        seen_text = f"Endings discovered: {len(self.gs.endings_seen)} / {len(ENDINGS)}"
        seen_shadow = self.fonts["tiny"].render(seen_text, True, (0, 0, 0))
        seen = self.fonts["tiny"].render(seen_text, True, TEXT_LIGHT)
        self.screen.blit(seen_shadow, (SCREEN_W // 2 - seen.get_width() // 2 + 2, 442))
        self.screen.blit(seen, (SCREEN_W // 2 - seen.get_width() // 2, 440))

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
        hint = self.fonts["small"].render("Enter — continue", True, (100, 100, 120))
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
            self.fonts["tiny"].render("Up/Down — select   Enter — confirm", True, (80, 80, 120)),
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
            "Odds: 1–6 hard 50% | 7–10 normal 30% | 11–16 easier 20% | 17–20 lucky 10%",
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
        panel = pygame.Rect(60, 500, SCREEN_W - 120, 120)
        pygame.draw.rect(self.screen, (40, 20, 32), panel, border_radius=12)
        head = self.fonts["heading"].render("ENDING", True, ACCENT)
        body = self.fonts["text"].render(text, True, TEXT_LIGHT)
        self.screen.blit(head, (SCREEN_W // 2 - head.get_width() // 2, panel.y + 12))
        self.screen.blit(body, (80, panel.y + 48))
        n = len(self.gs.endings_seen)
        tot = len(ENDINGS)
        prog = self.fonts["small"].render(f"Endings collected: {n} / {tot}", True, TEXT_LIGHT)
        self.screen.blit(prog, (SCREEN_W // 2 - prog.get_width() // 2, panel.y + 88))
        hint = self.fonts["small"].render("Enter — return to title", True, TEXT_LIGHT)
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 40))


if __name__ == "__main__":
    Game().run()
