"""Particle effects: confetti for a correct answer, a puff when numbers combine."""

import math
import random

import pygame

from .palette import DIGIT_COLORS, RAINBOW

CONFETTI_COLORS = list(RAINBOW) + [DIGIT_COLORS[8], (255, 255, 255)]


class Confetti:
    def __init__(self):
        self.pieces = []

    def burst(self, x, y, count=120, speed=520):
        for _ in range(count):
            angle = random.uniform(-math.pi * 0.95, -math.pi * 0.05)
            v = random.uniform(0.35, 1.0) * speed
            self._add(x, y, math.cos(angle) * v, math.sin(angle) * v)

    def rain(self, width, count=4):
        for _ in range(count):
            self._add(random.uniform(0, width), -20, random.uniform(-40, 40), 60)

    def _add(self, x, y, vx, vy):
        self.pieces.append(
            {
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "w": random.uniform(6, 11),
                "h": random.uniform(10, 17),
                "angle": random.uniform(0, math.tau),
                "spin": random.uniform(-9, 9),
                "phase": random.uniform(0, math.tau),
                "color": random.choice(CONFETTI_COLORS),
            }
        )

    def update(self, dt, height):
        for p in self.pieces:
            p["vy"] = min(p["vy"] + 700 * dt, 170)
            p["vx"] *= 1 - 1.8 * dt
            p["phase"] += dt * 6
            p["x"] += (p["vx"] + math.sin(p["phase"]) * 40) * dt
            p["y"] += p["vy"] * dt
            p["angle"] += p["spin"] * dt
        self.pieces = [p for p in self.pieces if p["y"] < height + 30]

    def draw(self, surface):
        for p in self.pieces:
            # Flip the piece's apparent width to make it look like it tumbles.
            w = p["w"] * abs(math.cos(p["phase"])) + 1
            h = p["h"]
            c, s = math.cos(p["angle"]), math.sin(p["angle"])
            corners = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
            points = [(p["x"] + dx * c - dy * s, p["y"] + dx * s + dy * c) for dx, dy in corners]
            pygame.draw.polygon(surface, p["color"], points)

    def clear(self):
        self.pieces.clear()


class Puff:
    """A cloud of white puffs and sparkles, used when two numbers combine."""

    def __init__(self, x, y, size):
        self.age = 0.0
        self.duration = 0.7
        self.clouds = []
        for i in range(18):
            angle = math.tau * i / 18 + random.uniform(-0.15, 0.15)
            speed = random.uniform(0.6, 1.2) * size * 2.2
            self.clouds.append(
                (x, y, math.cos(angle) * speed, math.sin(angle) * speed * 0.8,
                 random.uniform(0.25, 0.45) * size)
            )
        self.sparkles = []
        for _ in range(14):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1.2, 2.2) * size * 1.8
            self.sparkles.append(
                (x, y, math.cos(angle) * speed, math.sin(angle) * speed,
                 random.choice(RAINBOW))
            )

    @property
    def done(self):
        return self.age >= self.duration

    def update(self, dt):
        self.age += dt

    def draw(self, surface):
        t = min(1.0, self.age / self.duration)
        ease = 1 - (1 - t) ** 3
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        alpha = int(235 * (1 - t))
        for x, y, vx, vy, r in self.clouds:
            radius = r * (0.6 + ease)
            pygame.draw.circle(
                overlay, (255, 255, 255, alpha), (x + vx * ease, y + vy * ease), radius
            )
        for x, y, vx, vy, color in self.sparkles:
            px, py = x + vx * ease, y + vy * ease
            star(overlay, (*color, alpha), (px, py), 9 * (1 - t) + 3)
        surface.blit(overlay, (0, 0))


def star(surface, color, center, radius):
    cx, cy = center
    points = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        points.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    pygame.draw.polygon(surface, color, points)
