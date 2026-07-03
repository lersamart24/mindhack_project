"""Pokemon-style turn-based battle screen."""

from __future__ import annotations

import math

import pygame
from constants import (
    ACCENT,
    BG_BOTTOM,
    BG_TOP,
    HP_BG,
    HP_GREEN,
    HP_RED,
    HP_YELLOW,
    PANEL,
    PANEL_BORDER,
    PANEL_DARK,
    SCREEN_H,
    SCREEN_W,
    TEXT,
    TEXT_LIGHT,
)


class Move:
    def __init__(self, name: str, power: int, desc: str = ""):
        self.name = name
        self.power = power
        self.desc = desc or name


class Fighter:
    def __init__(self, name: str, max_hp: int, moves: list[Move], sprite_color: tuple[int, int, int],
                 attack_bonus: int = 0, armor: int = 0, has_antidote: bool = False):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.moves = moves
        self.sprite_color = sprite_color
        self.attack_bonus = attack_bonus
        self.armor = armor
        self.has_antidote = has_antidote

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)


def _hp_color(ratio: float) -> tuple[int, int, int]:
    if ratio > 0.5:
        return HP_GREEN
    if ratio > 0.25:
        return HP_YELLOW
    return HP_RED


def _draw_hp_bar(
    surf: pygame.Surface,
    font: pygame.font.Font,
    x: int,
    y: int,
    w: int,
    name: str,
    hp: int,
    max_hp: int,
    align_right: bool = False,
) -> None:
    label = font.render(f"{name}", True, TEXT_LIGHT)
    if align_right:
        surf.blit(label, (x + w - label.get_width(), y))
    else:
        surf.blit(label, (x, y))
    bar_y = y + label.get_height() + 4
    pygame.draw.rect(surf, HP_BG, (x, bar_y, w, 14), border_radius=4)
    ratio = hp / max_hp if max_hp else 0
    fill_w = int(w * ratio)
    if fill_w > 0:
        pygame.draw.rect(surf, _hp_color(ratio), (x, bar_y, fill_w, 14), border_radius=4)
    hp_text = font.render(f"HP {hp}/{max_hp}", True, TEXT_LIGHT)
    surf.blit(hp_text, (x, bar_y + 18))


MOVE_COOLDOWNS = {"Flame Burst": 3, "Sap Splash": 2, "Dodge": 2, "Heal": 4, "Pressure Point": 3}

POSE_FOR_MOVE = {
    "Punch": "punch",
    "Sap Splash": "punch",
    "Pressure Point": "punch",
    "Heal": "heal",
    "M79 Shot": "m79",
    "Flame Burst": "flame",
    "Finish": "flame",
}


class BattleScreen:
  """Full battle UI: dice result already applied to enemy stats."""

  def __init__(
      self,
      player: Fighter,
      enemy: Fighter,
      dice_value: int,
      dice_label: str,
      can_flee: bool = True,
      special_moves: list[Move] | None = None,
      background: pygame.Surface | None = None,
      player_sprite: pygame.Surface | None = None,
      enemy_sprite: pygame.Surface | None = None,
      player_poses: dict[str, pygame.Surface | None] | None = None,
      m79_charges: int = 0,
  ):
      self.player = player
      self.enemy = enemy
      self.dice_value = dice_value
      self.dice_label = dice_label
      self.can_flee = can_flee
      self.special_moves = special_moves
      self.background = background
      self.player_sprite = player_sprite
      self.enemy_sprite = enemy_sprite
      self.player_poses = player_poses or {}
      self.message = f"Wild {enemy.name} appeared! (Roll: {dice_value} — {dice_label})"
      self.phase = "menu"  # menu | player_anim | enemy_anim | end
      self.result: str | None = None  # win | lose | flee | spare
      self.selected_move = 0
      self.menu_mode = "fight"  # fight | bag (unused)
      self._anim_timer = 0
      self.last_move_name: str | None = None
      self.cooldowns: dict[str, int] = {}
      self.disabled_moves: dict[str, int] = {}
      self.dodge_active = False
      self._skip_enemy_turn = False
      self._give_turn_back = False
      self.enemy_burn = 0
      self.player_poison = 0
      self.enemy_shake = 0
      self.player_shake = 0
      self.enemy_defense_down = 0
      self.m79_charges = m79_charges

  def handle_event(self, event: pygame.event.Event) -> None:
      if self.phase != "menu" or self.result:
          return
      if event.type != pygame.KEYDOWN:
          return
      moves = self._current_moves()
      if event.key in (pygame.K_UP, pygame.K_w):
          self.selected_move = (self.selected_move - 2) % max(2, len(moves))
          if self.selected_move >= len(moves):
              self.selected_move = len(moves) - 1
      elif event.key in (pygame.K_DOWN, pygame.K_s):
          self.selected_move = (self.selected_move + 2) % max(2, len(moves))
          if self.selected_move >= len(moves):
              self.selected_move = 0
      elif event.key in (pygame.K_LEFT, pygame.K_a):
          self.selected_move = (self.selected_move - 1) % len(moves)
      elif event.key in (pygame.K_RIGHT, pygame.K_d):
          self.selected_move = (self.selected_move + 1) % len(moves)
      elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
          mv = moves[self.selected_move]
          if self.disabled_moves.get(mv.name, 0) > 0:
              self.message = f"{mv.name} is disabled! ({self.disabled_moves[mv.name]} turns left)"
              return
          self._execute_move(mv)

  def _current_moves(self) -> list[Move]:
      base = list(self.player.moves)
      if self.special_moves:
          base = base[:2] + list(self.special_moves)
      if self.can_flee:
          base = base + [Move("Run", 0, "Try to escape")]
      return base[:4]

  def _execute_move(self, move: Move) -> None:
      import random
      self.last_move_name = move.name
      if move.name == "Spare":
          self.result = "spare"
          self.message = "You spare the rafflesia. It recovers…"
          self.phase = "end"
          return
      if move.name == "Finish":
          dmg = max(40, move.power)
          self.enemy.take_damage(dmg)
          self.enemy_shake = 14
          self.message = f"You use {move.name}! Massive {dmg} damage!"
          self.phase = "player_anim"
          self._anim_timer = 28
          return
      if move.name == "Run":
          if self.can_flee:
              if random.random() < 0.3:
                  self.result = "flee"
                  self.message = "Got away safely!"
              else:
                  self.message = "Failed to escape! The enemy attacks!"
                  self.phase = "player_anim"
                  self._anim_timer = 28
          else:
              self.message = "Can't run from this fight!"
          return
      if self.cooldowns.get(move.name, 0) > 0:
          self.message = f"{move.name} is on cooldown! ({self.cooldowns[move.name]} turns left)"
          return
      if move.name == "Dodge":
          self.dodge_active = True
          cd = MOVE_COOLDOWNS.get(move.name, 0)
          if cd:
              self.cooldowns[move.name] = cd
          self.message = "You dodge! The zombie strikes back!"
          self.phase = "player_anim"
          self._anim_timer = 28
          return
      if move.name == "Heal":
          heal = 25
          self.player.hp = min(self.player.max_hp, self.player.hp + heal)
          self.cooldowns["Heal"] = MOVE_COOLDOWNS["Heal"]
          self.message = f"You heal for {heal} HP! The zombie strikes back!"
          self.phase = "player_anim"
          self._anim_timer = 28
          return
      if move.name == "M79 Shot":
          dmg = 48
          self.enemy.take_damage(dmg)
          self.enemy_shake = 14
          self.m79_charges -= 1
          if self.m79_charges == 0:
              self.message = f"BOOM! M79 deals {dmg} damage! Last shell spent — back to Flame Burst."
          else:
              self.message = f"BOOM! M79 deals {dmg} damage! ({self.m79_charges} shell{'s' if self.m79_charges != 1 else ''} left)"
          self.phase = "player_anim"
          self._anim_timer = 28
          return
      if move.name == "Pressure Point":
          cd = MOVE_COOLDOWNS.get("Pressure Point", 0)
          if cd:
              self.cooldowns["Pressure Point"] = cd
          r = random.random()
          if r < 0.30:
              self.player.take_damage(13)
              self.player_shake = 14
              self.message = "Pressure Point backfired! You took 13 damage!"
          elif r < 0.60:
              self.enemy_defense_down = 3
              self.message = f"Pressure Point hit a nerve! {self.enemy.name}'s defense drops for 3 turns!"
          elif r < 0.80:
              self._skip_enemy_turn = True
              self.message = f"Pressure Point struck true! {self.enemy.name} is stunned!"
          else:
              self.message = "Pressure Point missed! The enemy shrugged it off."
          self.phase = "player_anim"
          self._anim_timer = 28
          return
      dmg = max(8, int((move.power + (self.player.max_hp // 20) + self.player.attack_bonus) * 1.5))
      if self.enemy_defense_down > 0:
          dmg = int(dmg * 1.5)
      self.enemy.take_damage(dmg)
      self.enemy_shake = 14
      if move.name == "Flame Burst":
          self.enemy_burn = 3
          self.message = f"Flame Burst! {dmg} dmg — {self.enemy.name} is burning! (3 turns)"
      else:
          self.message = f"You used {move.name}! It dealt {dmg} damage."
      cd = MOVE_COOLDOWNS.get(move.name, 0)
      if cd:
          self.cooldowns[move.name] = cd
      self.phase = "player_anim"
      self._anim_timer = 28

  def update(self) -> None:
      if self.enemy_shake > 0:
          self.enemy_shake -= 1
      if self.player_shake > 0:
          self.player_shake -= 1
      if self.phase == "menu" or self.result:
          return
      self._anim_timer -= 1
      if self._anim_timer > 0:
          return
      if self.phase == "player_anim":
          if not self.enemy.alive:
              self.result = "win"
              self.message = f"{self.enemy.name} fainted! You win!"
              self.phase = "end"
              return
          if self._skip_enemy_turn:
              self._skip_enemy_turn = False
              self.cooldowns = {k: v - 1 for k, v in self.cooldowns.items() if v > 1}
              self.phase = "menu"
              return
          self.phase = "enemy_anim"
          self._enemy_turn()
          self._anim_timer = 28
      elif self.phase == "enemy_anim":
          if not self.player.alive:
              self.result = "lose"
              self.message = "You blacked out..."
              self.phase = "end"
              return
          if self._give_turn_back:
              self._give_turn_back = False
              self.cooldowns = {k: v - 1 for k, v in self.cooldowns.items() if v > 1}
              self.disabled_moves = {k: v - 1 for k, v in self.disabled_moves.items() if v > 1}
              self.phase = "menu"
              return
          tick_msgs = []
          if self.enemy_burn > 0:
              burn_dmg = 8
              self.enemy.take_damage(burn_dmg)
              self.enemy_shake = 10
              self.enemy_burn -= 1
              tick_msgs.append(f"Burn: -{burn_dmg}HP ({self.enemy_burn} left)")
              if not self.enemy.alive:
                  self.result = "win"
                  self.message = f"{self.enemy.name} burned to death! You win!"
                  self.phase = "end"
                  return
          if self.player_poison > 0:
              poison_dmg = 6
              self.player.take_damage(poison_dmg)
              self.player_shake = 10
              self.player_poison -= 1
              tick_msgs.append(f"Poison: -{poison_dmg}HP ({self.player_poison} left)")
              if not self.player.alive:
                  self.result = "lose"
                  self.message = "Poison claimed your life..."
                  self.phase = "end"
                  return
          self.cooldowns = {k: v - 1 for k, v in self.cooldowns.items() if v > 1}
          self.disabled_moves = {k: v - 1 for k, v in self.disabled_moves.items() if v > 1}
          if self.enemy_defense_down > 0:
              self.enemy_defense_down -= 1
          self.phase = "menu"
          self.message = ("  ".join(tick_msgs) + " — What will you do?" if tick_msgs else "What will you do?")

  def _enemy_turn(self) -> None:
      import random

      move = random.choice(self.enemy.moves) if self.enemy.moves else Move("Strike", 12)
      hit = True
      if self.dodge_active:
          self.dodge_active = False
          r = random.random()
          if r < 0.01:
              self.player.hp = 0
              self.player_shake = 14
              self.message = f"{self.enemy.name} used {move.name}! CRITICAL — You were one-shotted!"
              hit = False
          elif r < 0.41:
              self.message = f"{self.enemy.name} used {move.name}! You dodged it! Your turn again."
              self._give_turn_back = True
              hit = False
          else:
              dmg = max(1, move.power - self.player.armor)
              self.player.take_damage(dmg)
              self.player_shake = 14
              self.message = f"{self.enemy.name} used {move.name}! Dodge failed! ({dmg} damage)"
      else:
          dmg = max(1, move.power - self.player.armor)
          self.player.take_damage(dmg)
          self.player_shake = 14
          self.message = f"{self.enemy.name} used {move.name}! ({dmg} damage)"

      if hit:
          extras = []
          if random.random() < 0.35 and self.player_poison == 0 and not self.player.has_antidote:
              self.player_poison = 3
              extras.append("Poisoned! (3 turns)")
          attack_moves = [m for m in self._current_moves()
                          if m.name not in ("Dodge", "Heal", "Run", "Spare", "Finish")]
          if attack_moves and random.random() < 0.30:
              target = random.choice(attack_moves)
              if self.disabled_moves.get(target.name, 0) == 0:
                  self.disabled_moves[target.name] = 2
                  extras.append(f"{target.name} disabled 2 turns!")
          if extras:
              self.message += "  " + "  ".join(extras)

  def _current_player_sprite(self) -> pygame.Surface | None:
      if self.player_poses and self.phase == "player_anim" and self.last_move_name:
          key = POSE_FOR_MOVE.get(self.last_move_name)
          if key:
              pose = self.player_poses.get(key)
              if pose:
                  return pose
      return self.player_sprite

  def _blit_sprite(
      self,
      surf: pygame.Surface,
      image: pygame.Surface | None,
      fallback_color: tuple[int, int, int],
      x: int,
      y: int,
      max_w: int,
      max_h: int,
  ) -> None:
      if image:
          iw, ih = image.get_size()
          scale = min(max_w / iw, max_h / ih)
          w, h = max(1, int(iw * scale)), max(1, int(ih * scale))
          scaled = pygame.transform.smoothscale(image, (w, h))
          surf.blit(scaled, (x + (max_w - w) // 2, y + (max_h - h) // 2))
      else:
          pygame.draw.rect(surf, fallback_color, (x, y, max_w, max_h), border_radius=8)

  def draw(self, surf: pygame.Surface, fonts: dict) -> None:
      if self.background:
          bg = pygame.transform.smoothscale(self.background, (SCREEN_W, SCREEN_H))
          surf.blit(bg, (0, 0))
      else:
          for y in range(SCREEN_H // 2):
              t = y / (SCREEN_H // 2)
              c = (
                  int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t),
                  int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t),
                  int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t),
              )
              pygame.draw.line(surf, c, (0, y), (SCREEN_W, y))
          # Left half: dirt (player side), right half: grass (enemy side)
          pygame.draw.rect(surf, (160, 110, 60), (0, SCREEN_H // 2, SCREEN_W // 2, SCREEN_H // 2))
          pygame.draw.rect(surf, (88, 140, 72), (SCREEN_W // 2, SCREEN_H // 2, SCREEN_W // 2, SCREEN_H // 2))

      # Shake offsets (sinusoidal left-right wobble)
      esx = int(math.sin(self.enemy_shake * 1.8) * 7) if self.enemy_shake > 0 else 0
      psx = int(math.sin(self.player_shake * 1.8) * 7) if self.player_shake > 0 else 0

      # Enemy platform (bottom right, on the grass)
      ex, ey = SCREEN_W - 240, 175
      pygame.draw.ellipse(surf, (50, 90, 46), (ex + esx, ey + 162, 200, 32))
      self._blit_sprite(surf, self.enemy_sprite, self.enemy.sprite_color, ex + esx, ey, 200, 200)
      _draw_hp_bar(
          surf, fonts["small"], ex, ey - 76, 200,
          self.enemy.name, self.enemy.hp, self.enemy.max_hp,
      )
      if self.enemy_burn > 0 or self.enemy_defense_down > 0:
          name_w = fonts["small"].size(self.enemy.name)[0]
          bx = ex + name_w + 4
          if self.enemy_burn > 0:
              burn_badge = fonts["tiny"].render(f"  BURN {self.enemy_burn}", True, (255, 120, 30))
              surf.blit(burn_badge, (bx, ey - 74))
              bx += burn_badge.get_width()
          if self.enemy_defense_down > 0:
              def_badge = fonts["tiny"].render(f"  DEF↓ {self.enemy_defense_down}", True, (100, 200, 255))
              surf.blit(def_badge, (bx, ey - 74))

      # Player platform (bottom left, on dirt)
      px, py = 60, 285
      pygame.draw.ellipse(surf, (120, 80, 40), (px + psx, py + 162, 200, 32))
      self._blit_sprite(surf, self._current_player_sprite(), self.player.sprite_color, px + psx, py, 200, 200)
      _draw_hp_bar(surf, fonts["small"], px, py - 76, 200, "You", self.player.hp, self.player.max_hp)
      if self.player_poison > 0:
          name_w = fonts["small"].size("You")[0]
          poison_badge = fonts["tiny"].render(f"  POISON {self.player_poison}", True, (100, 220, 80))
          surf.blit(poison_badge, (px + name_w + 4, py - 74))

      # Message + move panel (Pokemon layout)
      panel_h = 168
      panel_y = SCREEN_H - panel_h
      pygame.draw.rect(surf, PANEL_DARK, (0, panel_y, SCREEN_W, panel_h))
      pygame.draw.rect(surf, PANEL_BORDER, (0, panel_y, SCREEN_W, panel_h), 3)

      msg_rect = pygame.Rect(16, panel_y + 12, SCREEN_W // 2 - 8, panel_h - 24)
      pygame.draw.rect(surf, PANEL, msg_rect, border_radius=6)
      pygame.draw.rect(surf, PANEL_BORDER, msg_rect, 2, border_radius=6)
      text_area = msg_rect.inflate(-12, -8)
      text_area.x += 30
      text_area.y += 10
      self._blit_wrapped(surf, fonts["text"], self.message, text_area)

      moves = self._current_moves()
      move_rect = pygame.Rect(SCREEN_W // 2 + 8, panel_y + 12, SCREEN_W // 2 - 24, panel_h - 24)
      pygame.draw.rect(surf, PANEL, move_rect, border_radius=6)
      pygame.draw.rect(surf, PANEL_BORDER, move_rect, 2, border_radius=6)
      cols, rows = 2, 2
      cell_w = (move_rect.width - 12) // cols
      cell_h = (move_rect.height - 12) // rows
      for i, mv in enumerate(moves):
          row, col = divmod(i, cols)
          r = pygame.Rect(
              move_rect.x + 6 + col * cell_w,
              move_rect.y + 6 + row * cell_h,
              cell_w - 4,
              cell_h - 4,
          )
          on_cd = self.cooldowns.get(mv.name, 0) > 0
          disabled = self.disabled_moves.get(mv.name, 0) > 0
          sel = i == self.selected_move and self.phase == "menu" and not on_cd and not disabled
          color = ACCENT if sel else ((110, 60, 60) if disabled else (160, 160, 168) if on_cd else (220, 220, 228))
          pygame.draw.rect(surf, color, r, border_radius=4)
          pygame.draw.rect(surf, PANEL_BORDER, r, 1, border_radius=4)
          name_color = (200, 80, 80) if disabled else (140, 140, 148) if on_cd else TEXT
          name_s = fonts["small"].render(mv.name, True, name_color)
          surf.blit(name_s, (r.x + 8, r.y + 8))
          if disabled:
              dis_txt = fonts["tiny"].render(f"DISABLED {self.disabled_moves[mv.name]} turns", True, (220, 100, 100))
              surf.blit(dis_txt, (r.x + 8, r.y + 28))
          elif on_cd:
              cd_txt = fonts["tiny"].render(f"CD: {self.cooldowns[mv.name]} turns", True, (180, 80, 80))
              surf.blit(cd_txt, (r.x + 8, r.y + 28))
          elif mv.name == "M79 Shot":
              info = fonts["tiny"].render(f"Dmg 48  Shells: {self.m79_charges}", True, (255, 180, 50))
              surf.blit(info, (r.x + 8, r.y + 28))
          elif mv.name == "Pressure Point":
              info = fonts["tiny"].render("30%back 30%def↓ 20%stun 20%miss", True, (180, 140, 255))
              surf.blit(info, (r.x + 8, r.y + 28))
          elif mv.name == "Dodge":
              info = fonts["tiny"].render("40% dodge / 1% die", True, (80, 80, 96))
              surf.blit(info, (r.x + 8, r.y + 28))
          elif mv.name == "Run":
              info = fonts["tiny"].render("30% escape", True, (80, 80, 96))
              surf.blit(info, (r.x + 8, r.y + 28))
          elif mv.name == "Finish":
              actual = max(40, mv.power)
              pwr = fonts["tiny"].render(f"Dmg {actual}", True, (80, 80, 96))
              surf.blit(pwr, (r.x + 8, r.y + 28))
          elif mv.name == "Heal":
              info = fonts["tiny"].render("Restore 25 HP  CD:4", True, (80, 180, 80))
              surf.blit(info, (r.x + 8, r.y + 28))
          elif mv.name == "Spare":
              pass
          elif mv.power:
              actual = max(8, int((mv.power + (self.player.max_hp // 20)) * 1.5))
              pwr = fonts["tiny"].render(f"Dmg {actual}", True, (80, 80, 96))
              surf.blit(pwr, (r.x + 8, r.y + 28))

      hint = fonts["tiny"].render("Arrows: select  |  Enter: confirm  |  Q: Items", True, TEXT_LIGHT)
      surf.blit(hint, (16, 8))

  def _blit_wrapped(self, surf, font, text, rect):
      words = text.split()
      lines, line = [], ""
      for w in words:
          test = f"{line} {w}".strip()
          if font.size(test)[0] <= rect.width:
              line = test
          else:
              if line:
                  lines.append(line)
              line = w
      if line:
          lines.append(line)
      y = rect.y
      for ln in lines[:4]:
          surf.blit(font.render(ln, True, TEXT), (rect.x, y))
          y += font.get_linesize()
