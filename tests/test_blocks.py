import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from number_squares.blocks import block_values, composition, draw_block, pattern
from number_squares.character import Character, layout
from number_squares.palette import BLUE, DIGIT_COLORS, ORANGE, RAINBOW, RED, WHITE


@pytest.mark.parametrize("n", [1, 9, 42, 99, 100, 215, 999, 1000, 1092, 1998])
def test_blocks_add_up_to_the_number(n):
    assert sum(block_values(n)) == n


def test_compression_thresholds():
    assert composition(99) == [(1, 99)]
    assert composition(215) == [(10, 21), (1, 5)]
    assert composition(1092) == [(100, 10), (10, 9), (1, 2)]
    assert composition(1000) == [(100, 10)]


def test_patterns():
    assert pattern(4) == (None, [4])
    assert pattern(10) == (1, [0])
    assert pattern(215) == (2, [1, 5])


def test_black_is_reserved_for_features():
    assert (0, 0, 0) not in DIGIT_COLORS.values()
    assert (0, 0, 0) not in RAINBOW


def pixel(surface, x, y):
    return tuple(surface.get_at((x, y)))[:3]


def test_215_is_orange_border_red_left_blue_right():
    surface = pygame.Surface((100, 100))
    draw_block(surface, (0, 0, 100, 100), 215)
    assert pixel(surface, 8, 50) == ORANGE
    assert pixel(surface, 35, 50) == RED
    assert pixel(surface, 65, 50) == BLUE


def test_10_is_red_border_white_inside():
    surface = pygame.Surface((100, 100))
    draw_block(surface, (0, 0, 100, 100), 10)
    assert pixel(surface, 8, 50) == RED
    assert pixel(surface, 50, 50) == WHITE


def test_seven_is_a_rainbow_from_top_to_bottom():
    pygame.init()
    seven = Character(7, 20)
    colors = [pixel(seven.body, cell.centerx, cell.centery - 7) for cell in reversed(seven.cells)]
    assert colors == list(RAINBOW)


@pytest.mark.parametrize("count", range(1, 120))
def test_layout_fits_all_blocks_and_is_not_too_skinny(count):
    cols, rows = layout(count)
    assert cols * rows >= count
    assert (rows - 1) * cols < count
    if count > 10:
        assert rows <= 2.5 * cols
