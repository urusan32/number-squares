"""Game states and the main loop."""

import math
import random

import pygame

from .blocks import compression
from .character import HAPPY, JOY, OOPS, Character, fit_block_size, legend_surface
from .effects import Confetti, Puff
from .palette import BAD, GOOD, PANEL, TEXT, TEXT_LIGHT
from .ui import Button, blit_centered, draw_cloud, font, make_background, outlined_text

WIDTH, HEIGHT = 1100, 760
GROUND_Y = 630
FPS = 60

DIFFICULTIES = {
    "Easy": (1, 9, "1 to 9"),
    "Medium": (1, 99, "up to 99"),
    "Hard": (1, 999, "up to 999"),
}

MENU, QUESTION, COMBINING, RESULT = "menu", "question", "combining", "result"

# Combining animation timeline (seconds).
CROUCH_END = 0.22
JUMP_END = 1.0
POP_END = 1.6
COMBINE_END = 1.9

MAX_INPUT_DIGITS = 4


def ease_out_back(t):
    c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.background = make_background(WIDTH, HEIGHT, GROUND_Y)
        self.fonts = {
            "title": font(84),
            "big": font(56),
            "medium": font(36),
            "label": font(30),
            "small": font(22, bold=False),
        }
        self.time = 0.0
        self.running = True
        self.difficulty = "Easy"
        self.confetti = Confetti()
        self.puff = None
        self.clouds = [(random.uniform(0, WIDTH), random.uniform(40, 260),
                        random.uniform(0.6, 1.2), random.uniform(8, 20)) for _ in range(5)]

        self.menu_buttons = {
            name: Button(name, (WIDTH // 2 + (i - 1) * 270, 265), (240, 80),
                         color, hint=f"{DIFFICULTIES[name][2]}  [{i + 1}]")
            for i, (name, color) in enumerate(
                (("Easy", (140, 225, 120)), ("Medium", (255, 205, 80)), ("Hard", (255, 140, 120)))
            )
        }
        self.play_button = Button("Play!", (WIDTH // 2, 375), (260, 70), (120, 190, 255), "Enter")
        self.quit_button = Button("Quit", (WIDTH // 2, 452), (200, 56), (220, 220, 230), "Esc")
        self.result_buttons = {
            "again": Button("Another Round", (WIDTH // 2 - 290, 695), (270, 64),
                            (140, 225, 120), "Enter"),
            "menu": Button("Menu", (WIDTH // 2, 695), (200, 64), (255, 205, 80), "M"),
            "quit": Button("Quit", (WIDTH // 2 + 260, 695), (200, 64), (220, 220, 230), "Esc"),
        }

        parade_values = list(range(1, 11))
        self.parade = [Character(v, 24) for v in parade_values]
        self.state = MENU
        self.score = [0, 0]

    # ----------------------------------------------------------------- flow

    def start_game(self):
        self.score = [0, 0]
        self.new_round()

    def new_round(self):
        low, high, _ = DIFFICULTIES[self.difficulty]
        previous = getattr(self, "problem", None)
        while True:
            a, b = random.randint(low, high), random.randint(low, high)
            if (a, b) != previous:
                break
        self.problem = (a, b)
        self.answer_text = ""
        self.confetti.clear()
        self.puff = None

        size = min(
            fit_block_size(a, WIDTH * 0.4, GROUND_Y - 190),
            fit_block_size(b, WIDTH * 0.4, GROUND_Y - 190),
        )
        self.left = Character(a, size)
        self.right = Character(b, size)
        total = a + b
        total_size = fit_block_size(total, WIDTH * 0.62, GROUND_Y - 240)
        if compression(total) == compression(max(a, b)):
            # Same kind of blocks: keep the same block size so the sum looks
            # like the two parts put together.
            total_size = min(size, total_size)
        self.total = Character(total, total_size)
        self.left_x, self.right_x = WIDTH * 0.27, WIDTH * 0.73
        self.state = QUESTION

    def submit(self):
        if not self.answer_text:
            return
        self.guess = int(self.answer_text)
        self.correct = self.guess == sum(self.problem)
        self.score[1] += 1
        if self.correct:
            self.score[0] += 1
        self.state = COMBINING
        self.state_time = 0.0

    def finish_combining(self):
        self.state = RESULT
        self.state_time = 0.0
        if self.correct:
            self.confetti.burst(WIDTH / 2, GROUND_Y - self.total.body_h / 2)

    # --------------------------------------------------------------- events

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        handler = {
            MENU: self._menu_event,
            QUESTION: self._question_event,
            RESULT: self._result_event,
        }.get(self.state)
        if handler:
            handler(event)

    def _menu_event(self, event):
        names = list(DIFFICULTIES)
        for name, button in self.menu_buttons.items():
            if button.clicked(event):
                self.difficulty = name
        if self.play_button.clicked(event):
            self.start_game()
        elif self.quit_button.clicked(event):
            self.running = False
        elif event.type == pygame.KEYDOWN:
            index = names.index(self.difficulty)
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_LEFT:
                self.difficulty = names[(index - 1) % len(names)]
            elif event.key == pygame.K_RIGHT:
                self.difficulty = names[(index + 1) % len(names)]
            elif event.unicode in ("1", "2", "3"):
                self.difficulty = names[int(event.unicode) - 1]

    def _question_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.submit()
        elif event.key == pygame.K_BACKSPACE:
            self.answer_text = self.answer_text[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.state = MENU
        elif event.unicode.isdigit() and len(self.answer_text) < MAX_INPUT_DIGITS:
            self.answer_text += event.unicode

    def _result_event(self, event):
        buttons = self.result_buttons
        if buttons["again"].clicked(event):
            self.new_round()
        elif buttons["menu"].clicked(event):
            self.state = MENU
        elif buttons["quit"].clicked(event):
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_n):
                self.new_round()
            elif event.key == pygame.K_m:
                self.state = MENU
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.running = False

    # --------------------------------------------------------------- update

    def update(self, dt):
        self.time += dt
        self.clouds = [((x + speed * dt) % (WIDTH + 200), y, s, speed)
                       for x, y, s, speed in self.clouds]
        if self.state == COMBINING:
            before = self.state_time
            self.state_time += dt
            if before < JUMP_END <= self.state_time:
                self.puff = Puff(WIDTH / 2, GROUND_Y - self.total.body_h / 2,
                                 min(130, max(self.left.body_w, self.right.body_w, 60)))
            if self.state_time >= COMBINE_END:
                self.finish_combining()
        elif self.state == RESULT:
            self.state_time += dt
            if self.correct and self.state_time < 2.5:
                self.confetti.rain(WIDTH, 3)
        if self.puff:
            self.puff.update(dt)
            if self.puff.done:
                self.puff = None
        self.confetti.update(dt, HEIGHT)

    # ----------------------------------------------------------------- draw

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for x, y, scale, _ in self.clouds:
            draw_cloud(self.screen, x - 100, y, scale)
        {
            MENU: self._draw_menu,
            QUESTION: self._draw_question,
            COMBINING: self._draw_combining,
            RESULT: self._draw_result,
        }[self.state]()
        if self.puff:
            self.puff.draw(self.screen)
        self.confetti.draw(self.screen)

    def _blink(self, phase):
        return (self.time + phase) % 3.7 < 0.13

    def _draw_character(self, char, x, y, mood=HAPPY, phase=0.0, sx=1.0, sy=1.0, label=True):
        image = char.render(mood, self.time + phase, self._blink(phase))
        ax, ay = char.anchor
        if (sx, sy) != (1.0, 1.0):
            w, h = image.get_size()
            image = pygame.transform.smoothscale(image, (max(1, round(w * sx)), max(1, round(h * sy))))
            ax, ay = ax * sx, ay * sy
        top_left = (round(x - ax), round(y - ay))
        self.screen.blit(image, top_left)
        if label:
            text = outlined_text(self.fonts["medium"], str(char.value), TEXT_LIGHT, TEXT, 3)
            head_top = top_left[1] + char.body_rect.top * sy
            self.screen.blit(text, text.get_rect(midbottom=(x, head_top - 6)))

    def _draw_legend(self, char, x):
        legend = legend_surface(char.value, self.fonts["small"], TEXT_LIGHT)
        if legend:
            blit_centered(self.screen, legend, (x, GROUND_Y + 28))

    def _bob(self, phase):
        return -abs(math.sin(self.time * 2.2 + phase)) * 5

    def _draw_menu(self):
        title = outlined_text(self.fonts["title"], "Number Squares", (255, 230, 90), TEXT, 4)
        blit_centered(self.screen, title, (WIDTH // 2, 95))
        sub = self.fonts["label"].render("Add the numbers before they combine!", True, TEXT)
        blit_centered(self.screen, sub, (WIDTH // 2, 170))

        for name, button in self.menu_buttons.items():
            button.selected = name == self.difficulty
            button.draw(self.screen, self.fonts["label"], self.fonts["small"])
        self.play_button.draw(self.screen, self.fonts["label"], self.fonts["small"])
        self.quit_button.draw(self.screen, self.fonts["label"], self.fonts["small"])

        spacing = WIDTH / (len(self.parade) + 1)
        for i, char in enumerate(self.parade):
            x = spacing * (i + 1)
            self._draw_character(char, x, GROUND_Y + self._bob(i * 0.7), HAPPY, i * 0.9, label=False)
            num = outlined_text(self.fonts["label"], str(char.value), TEXT_LIGHT, TEXT, 2)
            blit_centered(self.screen, num, (x, GROUND_Y + 40))

    def _draw_problem_text(self):
        a, b = self.problem
        text = outlined_text(self.fonts["big"], f"What is {a} + {b}?", TEXT_LIGHT, TEXT, 3)
        blit_centered(self.screen, text, (WIDTH // 2, 60))

    def _draw_score(self):
        right, total = self.score
        text = self.fonts["small"].render(
            f"{self.difficulty}   Score: {right} / {total}", True, TEXT
        )
        self.screen.blit(text, (16, 12))

    def _draw_question(self):
        self._draw_problem_text()
        self._draw_score()
        self._draw_character(self.left, self.left_x, GROUND_Y + self._bob(0), HAPPY, 0.0)
        self._draw_character(self.right, self.right_x, GROUND_Y + self._bob(1.3), HAPPY, 1.9)
        plus = outlined_text(self.fonts["title"], "+", TEXT_LIGHT, TEXT, 4)
        blit_centered(self.screen, plus, (WIDTH // 2, GROUND_Y - 170))
        self._draw_legend(self.left, self.left_x)
        self._draw_legend(self.right, self.right_x)
        self._draw_input_box()

    def _draw_input_box(self):
        box = pygame.Rect(0, 0, 330, 70)
        box.center = (WIDTH // 2, 700)
        pygame.draw.rect(self.screen, PANEL, box, border_radius=14)
        pygame.draw.rect(self.screen, TEXT, box, 3, border_radius=14)
        cursor = "|" if (self.time % 1.0) < 0.55 else " "
        shown = self.answer_text + cursor
        text = self.fonts["big"].render(shown, True, TEXT)
        blit_centered(self.screen, text, box.center)
        prompt = self.fonts["small"].render("Type your answer, then press Enter", True, TEXT_LIGHT)
        self.screen.blit(prompt, prompt.get_rect(midbottom=(WIDTH // 2, box.top - 4)))

    def _draw_combining(self):
        t = self.state_time
        self._draw_score()
        answer = self.fonts["medium"].render(f"You said: {self.guess}", True, TEXT)
        blit_centered(self.screen, answer, (WIDTH // 2, 700))

        if t < JUMP_END:
            for char, start_x, side, phase in (
                (self.left, self.left_x, -1, 0.0),
                (self.right, self.right_x, 1, 1.9),
            ):
                end_x = WIDTH / 2 + side * char.body_w * 0.3
                if t < CROUCH_END:
                    k = math.sin(t / CROUCH_END * math.pi)
                    self._draw_character(char, start_x, GROUND_Y, HAPPY, phase,
                                         1 + 0.12 * k, 1 - 0.15 * k)
                else:
                    u = (t - CROUCH_END) / (JUMP_END - CROUCH_END)
                    x = start_x + (end_x - start_x) * u
                    # Tall characters jump lower so they stay on screen.
                    height = max(40, min(190, GROUND_Y - char.height - 100))
                    y = GROUND_Y - height * 4 * u * (1 - u)
                    stretch = 0.1 * (1 - 2 * u)
                    self._draw_character(char, x, y, JOY, phase, 1 - stretch * 0.6,
                                         1 + stretch, label=False)
        else:
            u = min(1.0, (t - JUMP_END) / (POP_END - JUMP_END))
            scale = max(0.05, ease_out_back(u))
            self._draw_character(self.total, WIDTH / 2, GROUND_Y, HAPPY, 0.0, scale, scale,
                                 label=u >= 1)
        self._draw_problem_text()

    def _draw_result(self):
        self._draw_score()
        a, b = self.problem
        total = a + b
        mood = JOY if self.correct else OOPS
        self._draw_character(self.total, WIDTH / 2, GROUND_Y + (self._bob(0) * 3 if self.correct else 0), mood)

        if self.correct:
            headline = outlined_text(self.fonts["big"], f"Correct!  {a} + {b} = {total}", (140, 255, 140), TEXT, 3)
            detail = "Great job!"
        else:
            headline = outlined_text(self.fonts["big"], f"Not quite!  {a} + {b} = {total}", (255, 170, 150), TEXT, 3)
            detail = f"You said {self.guess}. The answer is {total}. Try again!"
        blit_centered(self.screen, headline, (WIDTH // 2, 55))
        detail_text = outlined_text(self.fonts["label"], detail, TEXT_LIGHT, GOOD if self.correct else BAD, 2)
        blit_centered(self.screen, detail_text, (WIDTH // 2, 112))
        legend = legend_surface(self.total.value, self.fonts["small"], TEXT)
        if legend:
            blit_centered(self.screen, legend, (WIDTH // 2, 150))

        for button in self.result_buttons.values():
            button.draw(self.screen, self.fonts["label"], self.fonts["small"])

    # ----------------------------------------------------------------- loop

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000, 0.05)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
            pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption("Number Squares")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    Game(screen).run()
    pygame.quit()
