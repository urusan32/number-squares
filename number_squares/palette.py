"""Colors used by the number squares.

Every digit has its own color. Black is reserved for drawing features
(faces, arms, legs), so it never appears in a digit's color pattern.
"""

WHITE = (250, 250, 250)
RED = (230, 45, 45)
ORANGE = (255, 140, 20)
YELLOW = (255, 220, 30)
GREEN = (60, 190, 70)
BLUE = (40, 110, 230)
DARK_PURPLE = (95, 35, 140)
MAGENTA = (225, 40, 200)
GREY = (150, 150, 155)

INDIGO = (75, 70, 200)
LIGHT_PURPLE = (185, 130, 250)

# Seven is a rainbow; the 7th color is a lighter purple so it can't be
# confused with 6's dark purple.
RAINBOW = (RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, LIGHT_PURPLE)

DIGIT_COLORS = {
    0: WHITE,
    1: RED,
    2: ORANGE,
    3: YELLOW,
    4: GREEN,
    5: BLUE,
    6: DARK_PURPLE,
    7: LIGHT_PURPLE,  # representative color; 7 is drawn as a rainbow
    8: MAGENTA,
    9: GREY,
}

FEATURE = (0, 0, 0)
FEATURE_HIGHLIGHT = (255, 255, 255)

SKY_TOP = (120, 190, 245)
SKY_BOTTOM = (200, 235, 255)
GRASS = (110, 200, 90)
GRASS_DARK = (80, 165, 65)
TEXT = (35, 40, 70)
TEXT_LIGHT = (255, 255, 255)
GOOD = (30, 160, 60)
BAD = (220, 70, 50)
PANEL = (255, 255, 255)


def shade(color, factor):
    """Scale a color toward black (factor < 1) or toward white (factor > 1)."""
    if factor <= 1:
        return tuple(int(c * factor) for c in color)
    t = factor - 1
    return tuple(int(c + (255 - c) * t) for c in color)


def edge_color(color):
    """A darker version of a color, used to outline a region of that color."""
    # White needs a stronger darkening to show up at all.
    if min(color) > 200:
        return (185, 185, 195)
    return shade(color, 0.68)
