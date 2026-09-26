"""Small UI helpers: fonts, outlined text, buttons, background."""

import math

import pygame

from .palette import GRASS, GRASS_DARK, SKY_BOTTOM, SKY_TOP, TEXT, shade

FONT_NAMES = "comicsansms,comicneue,nunito,ubuntu,dejavusans,freesans,arial"


def font(size, bold=True):
    return pygame.font.SysFont(FONT_NAMES, size, bold=bold)


def outlined_text(fnt, text, color, outline=(40, 40, 60), width=2):
    base = fnt.render(text, True, color)
    edge = fnt.render(text, True, outline)
    w, h = base.get_width() + 2 * width, base.get_height() + 2 * width
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx * dx + dy * dy <= width * width + 1:
                surface.blit(edge, (width + dx, width + dy))
    surface.blit(base, (width, width))
    return surface


def blit_centered(surface, image, center):
    surface.blit(image, image.get_rect(center=center))


class Button:
    def __init__(self, label, center, size=(240, 60), color=(255, 200, 60), hint=""):
        self.label = label
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.color = color
        self.hint = hint
        self.selected = False

    def hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, surface, label_font, hint_font):
        lift = 3 if self.hovered() or self.selected else 0
        rect = self.rect.move(0, -lift)
        shadow = self.rect.move(0, 5)
        pygame.draw.rect(surface, shade(self.color, 0.6), shadow, border_radius=16)
        fill = shade(self.color, 1.25) if self.hovered() else self.color
        pygame.draw.rect(surface, fill, rect, border_radius=16)
        border = TEXT if self.selected else shade(self.color, 0.6)
        pygame.draw.rect(surface, border, rect, 4 if self.selected else 3, border_radius=16)
        text = label_font.render(self.label, True, TEXT)
        if self.hint:
            hint = hint_font.render(self.hint, True, shade(TEXT, 1.4))
            total = text.get_height() + hint.get_height() - 4
            top = rect.centery - total // 2
            surface.blit(text, text.get_rect(midtop=(rect.centerx, top)))
            surface.blit(
                hint, hint.get_rect(midtop=(rect.centerx, top + text.get_height() - 4))
            )
        else:
            blit_centered(surface, text, rect.center)


def make_background(width, height, ground_y):
    surface = pygame.Surface((width, height))
    for y in range(ground_y):
        t = y / max(1, ground_y - 1)
        color = tuple(round(a + (b - a) * t) for a, b in zip(SKY_TOP, SKY_BOTTOM))
        pygame.draw.line(surface, color, (0, y), (width, y))
    pygame.draw.rect(surface, GRASS, (0, ground_y, width, height - ground_y))
    pygame.draw.rect(surface, GRASS_DARK, (0, ground_y, width, 6))
    for x in range(0, width, 18):
        h = 8 + 5 * math.sin(x * 0.7)
        pygame.draw.line(surface, GRASS_DARK, (x, ground_y + 6), (x + 4, ground_y + 6 + h), 2)
    return surface


def draw_cloud(surface, x, y, scale):
    for dx, dy, r in ((0, 0, 30), (32, -14, 34), (66, 0, 28), (32, 8, 30)):
        pygame.draw.circle(
            surface, (255, 255, 255), (x + dx * scale, y + dy * scale), r * scale
        )
