"""Cartoon number square characters."""

import math

import pygame

from .blocks import STACK_FOR_VALUE, block_values, composition, draw_block
from .palette import FEATURE, FEATURE_HIGHLIGHT

HAPPY = "happy"  # default gentle smile
JOY = "joy"  # big open grin, arms in the air
OOPS = "oops"  # surprised little "o"

MAX_LIMB = 48
MIN_FACE = 44


def layout(count):
    """Return (cols, rows) for a body of `count` blocks."""
    if count <= 3 or count in (5, 7):
        return 1, max(count, 1)
    root = math.sqrt(count)
    divisor = max(d for d in range(1, int(root) + 1) if count % d == 0)
    # Use an exact rectangle unless it would make a very skinny tower.
    if divisor >= root / 2 and count // divisor <= 2.5 * divisor:
        return divisor, count // divisor
    cols = math.ceil(root)
    return cols, math.ceil(count / cols)


def fit_block_size(value, max_w, max_h, max_block=64):
    """Largest block size so a character for `value` fits in max_w x max_h."""
    cols, rows = layout(len(block_values(value)) or 1)
    size = min(
        max_block,
        (max_w - 2.4 * MAX_LIMB) / cols,
        (max_h - 1.2 * MAX_LIMB) / rows,
    )
    return max(6, int(size))


class Character:
    def __init__(self, value, block_size):
        self.value = value
        self.block_size = block_size
        values = block_values(value) or [1]
        self.count = len(values)
        self.cols, self.rows = layout(self.count)

        bs = block_size
        self.body_w = self.cols * bs
        self.body_h = self.rows * bs
        body_scale = max(bs * 0.8, min(self.body_w, self.body_h) * 0.2)
        self.limb = int(max(12, min(MAX_LIMB, body_scale)))
        self.line = max(3, self.limb // 6)
        # Small blocks get a face a bit bigger than the block so it stays readable.
        self.face_size = max(bs, min(MIN_FACE, int(bs * 1.6), self.body_w))

        top_extra = max(0, (self.face_size - bs) // 2) + 4
        side = int(self.limb * 1.25) + self.line
        self.width = self.body_w + 2 * side
        self.height = top_extra + self.body_h + self.limb + self.line
        self.body_rect = pygame.Rect(side, top_extra, self.body_w, self.body_h)

        # Block positions, filled from the bottom row up; a partial top row
        # is centered.
        self.cells = []
        for i in range(self.count):
            row, col = divmod(i, self.cols)
            in_row = min(self.cols, self.count - row * self.cols)
            x = self.body_rect.left + (col + (self.cols - in_row) / 2) * bs
            y = self.body_rect.bottom - (row + 1) * bs
            self.cells.append(pygame.Rect(round(x), y, bs, bs))

        top_row = (self.count - 1) // self.cols
        top_start = top_row * self.cols
        self.head = self.cells[top_start + (self.count - top_start) // 2]

        self.body = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i, (cell, block_value) in enumerate(zip(self.cells, values)):
            rainbow_index = self.count - 1 - i  # red on top, like a real rainbow
            draw_block(
                self.body, cell, value, rainbow_index, STACK_FOR_VALUE[block_value]
            )

    @property
    def anchor(self):
        """Point between the feet, in surface coordinates."""
        return self.body_rect.centerx, self.height

    def render(self, mood=HAPPY, t=0.0, blink=False):
        surface = self.body.copy()
        self._draw_legs(surface)
        self._draw_arms(surface, mood, t)
        self._draw_face(surface, mood, blink)
        return surface

    def _draw_legs(self, surface):
        body = self.body_rect
        spread = min(body.width * 0.25, self.block_size * 0.6)
        foot = max(4, self.line + 2)
        for sign in (-1, 1):
            x = body.centerx + sign * spread
            top = (x, body.bottom)
            bottom = (x, body.bottom + self.limb - foot // 2)
            pygame.draw.line(surface, FEATURE, top, bottom, self.line)
            foot_rect = pygame.Rect(0, 0, foot * 2.4, foot * 1.3)
            foot_rect.midbottom = (x + sign * foot * 0.5, self.height - 1)
            pygame.draw.ellipse(surface, FEATURE, foot_rect)

    def _draw_arms(self, surface, mood, t):
        body = self.body_rect
        shoulder_y = body.top + min(body.height * 0.45, self.block_size * 1.4)
        for sign in (-1, 1):
            if mood == JOY:
                # Up in the air, waving.
                angle = math.radians(140 + 12 * math.sin(t * 12 + sign))
            elif mood == OOPS:
                angle = math.radians(25)
            else:
                angle = math.radians(40 + 6 * math.sin(t * 2.5 + sign))
            start = (body.left - 1 if sign < 0 else body.right, shoulder_y)
            end = (
                start[0] + sign * math.sin(angle) * self.limb,
                start[1] + math.cos(angle) * self.limb,
            )
            pygame.draw.line(surface, FEATURE, start, end, self.line)
            pygame.draw.circle(surface, FEATURE, end, self.line + 1)

    def _draw_face(self, surface, mood, blink):
        f = self.face_size
        cx, cy = self.head.center
        eye_dx = f * 0.2
        eye_y = cy - f * 0.1
        stroke = max(2, round(f / 16))

        for sign in (-1, 1):
            ex = cx + sign * eye_dx
            if mood == JOY:
                # Happy closed eyes: ^ ^
                rect = pygame.Rect(0, 0, f * 0.2, f * 0.2)
                rect.center = (ex, eye_y + f * 0.04)
                pygame.draw.arc(surface, FEATURE, rect, 0.2, math.pi - 0.2, stroke)
            elif blink:
                pygame.draw.line(
                    surface,
                    FEATURE,
                    (ex - f * 0.07, eye_y),
                    (ex + f * 0.07, eye_y),
                    stroke,
                )
            else:
                eye = pygame.Rect(0, 0, max(3, f * 0.13), max(4, f * 0.2))
                eye.center = (ex, eye_y)
                pygame.draw.ellipse(surface, FEATURE, eye)
                glint = max(1, round(f * 0.03))
                pygame.draw.circle(
                    surface,
                    FEATURE_HIGHLIGHT,
                    (eye.centerx + glint * 0.6, eye.top + glint * 1.6),
                    glint,
                )
            if mood == OOPS:
                brow = pygame.Rect(0, 0, f * 0.2, f * 0.12)
                brow.center = (ex, eye_y - f * 0.2)
                pygame.draw.arc(surface, FEATURE, brow, 0.3, math.pi - 0.3, stroke)

        if mood == JOY:
            mouth = pygame.Rect(0, 0, f * 0.5, f * 0.4)
            mouth.center = (cx, cy + f * 0.1)
            points = [
                (
                    mouth.centerx + math.cos(a) * mouth.width / 2,
                    mouth.centery + math.sin(a) * mouth.height / 2,
                )
                for a in (math.pi * i / 16 for i in range(17))
            ]
            pygame.draw.polygon(surface, FEATURE, points)
            tongue = pygame.Rect(0, 0, f * 0.22, f * 0.12)
            tongue.center = (cx, mouth.centery + mouth.height * 0.33)
            pygame.draw.ellipse(surface, (255, 120, 150), tongue)
        elif mood == OOPS:
            mouth = pygame.Rect(0, 0, f * 0.16, f * 0.18)
            mouth.center = (cx, cy + f * 0.2)
            pygame.draw.ellipse(surface, FEATURE, mouth, stroke)
        else:
            mouth = pygame.Rect(0, 0, f * 0.44, f * 0.3)
            mouth.center = (cx, cy + f * 0.08)
            pygame.draw.arc(
                surface, FEATURE, mouth, math.pi + 0.35, 2 * math.pi - 0.35, stroke
            )


def legend_surface(value, font, text_color):
    """Explain compressed blocks, e.g. [stacked block] = 10. None if unneeded."""
    parts = [(v, c) for v, c in composition(value) if v > 1]
    if not parts:
        return None
    icon = 26
    pieces = []
    for block_value, _ in parts:
        block = pygame.Surface((icon, icon), pygame.SRCALPHA)
        draw_block(block, block.get_rect(), value, 0, STACK_FOR_VALUE[block_value])
        label = font.render(f"= {block_value}", True, text_color)
        pieces.append((block, label))
    gap = 16
    width = sum(icon + 6 + label.get_width() for _, label in pieces) + gap * (
        len(pieces) - 1
    )
    height = max(icon, max(label.get_height() for _, label in pieces))
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    x = 0
    for block, label in pieces:
        surface.blit(block, (x, (height - icon) // 2))
        x += icon + 6
        surface.blit(label, (x, (height - label.get_height()) // 2))
        x += label.get_width() + gap
    return surface
