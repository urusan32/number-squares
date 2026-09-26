"""How numbers are broken into blocks, and how a single block is painted.

Pattern rules:
  * A single digit number is a solid block of that digit's color
    (7 is a rainbow: each block of a 7 is the next rainbow color).
  * From 10 upward the block's border is the first digit and the interior
    is split into vertical stripes, one per remaining digit, left to right.
    e.g. 10 = red border, white interior; 215 = orange border, red|blue.
  * A 7 appearing inside a multi-digit pattern is drawn as horizontal
    rainbow bands.

Large numbers are compressed so the body stays a sensible size:
  * below 100 every block is worth 1
  * 100-999 uses "ten blocks" (worth 10 each) plus ones
  * 1000+ uses "hundred blocks" plus ten blocks plus ones
Compressed blocks are drawn as a stack (extra layers peeking out behind),
one extra layer for tens and two for hundreds.
"""

import pygame

from .palette import DIGIT_COLORS, RAINBOW, edge_color


def composition(n):
    """Return [(block_value, count), ...] from largest block value down."""
    if n < 100:
        parts = [(1, n)]
    elif n < 1000:
        parts = [(10, n // 10), (1, n % 10)]
    else:
        parts = [(100, n // 100), (10, (n // 10) % 10), (1, n % 10)]
    return [(value, count) for value, count in parts if count]


def block_values(n):
    """Flat list of block values, biggest first (they go at the bottom)."""
    return [value for value, count in composition(n) for _ in range(count)]


def compression(n):
    """The largest block value used for n (1, 10 or 100)."""
    return composition(n)[0][0] if n else 1


def pattern(n):
    """Describe a block of number n as (border_digit, [stripe digits]).

    Single digits have no border: (None, [digit]).
    """
    digits = [int(d) for d in str(n)]
    if len(digits) == 1:
        return None, digits
    return digits[0], digits[1:]


def _fill_region(surface, rect, digit, rainbow_index):
    if digit == 7 and rainbow_index is None:
        # Horizontal rainbow bands across the region.
        top = rect.top
        for i, color in enumerate(RAINBOW):
            bottom = rect.top + round(rect.height * (i + 1) / len(RAINBOW))
            pygame.draw.rect(surface, color, (rect.left, top, rect.width, bottom - top))
            top = bottom
        return RAINBOW[-1]
    if digit == 7:
        color = RAINBOW[rainbow_index % len(RAINBOW)]
    else:
        color = DIGIT_COLORS[digit]
    pygame.draw.rect(surface, color, rect)
    return color


def _outline(surface, rect, color, width):
    if width > 0:
        pygame.draw.rect(surface, edge_color(color), rect, width)


def draw_block_face(surface, rect, n, index=0):
    """Paint the color pattern of number n into rect.

    index is the block's position in the body; single-digit 7s use it to
    pick their rainbow color.
    """
    rect = pygame.Rect(rect)
    size = min(rect.width, rect.height)
    line = 1 if size < 28 else 2
    border_digit, stripes = pattern(n)

    if border_digit is None:
        color = _fill_region(surface, rect, stripes[0], index)
        _outline(surface, rect, color, line)
        return

    border = max(2, round(size * 0.18))
    color = _fill_region(surface, rect, border_digit, None)
    _outline(surface, rect, color, line)

    inner = rect.inflate(-2 * border, -2 * border)
    left = inner.left
    for i, digit in enumerate(stripes):
        right = inner.left + round(inner.width * (i + 1) / len(stripes))
        stripe = pygame.Rect(left, inner.top, right - left, inner.height)
        color = _fill_region(surface, stripe, digit, None)
        _outline(surface, stripe, color, line)
        left = right


def draw_block(surface, rect, n, index=0, stack=0):
    """Draw one body block. stack > 0 marks a compressed block (x10, x100)."""
    rect = pygame.Rect(rect)
    if stack:
        # Shrink the front face and let copies peek out up and to the right,
        # like a little stack of blocks.
        step = max(2, round(rect.width * 0.09))
        face_size = rect.width - step * stack
        for layer in range(stack, -1, -1):
            layer_rect = pygame.Rect(
                rect.left + step * layer,
                rect.bottom - face_size - step * layer,
                face_size,
                face_size,
            )
            draw_block_face(surface, layer_rect, n, index)
    else:
        draw_block_face(surface, rect, n, index)


STACK_FOR_VALUE = {1: 0, 10: 1, 100: 2}
