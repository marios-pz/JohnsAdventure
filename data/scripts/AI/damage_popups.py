import pygame as pg
from random import randint
from ..utils import resource_path


class DamagePopUp:

    def __init__(self, screen: pg.Surface, rect: pg.Rect, value: int, dmg_type: str = "default"):

        self.screen = screen
        self.font = pg.font.Font(resource_path("data/database/menu-font.ttf"), 25)

        # Start point
        self.temp = rect.y - 30

        colors = {
            "health": (110, 0, 150),
            "crit": (255, 255, 0),
            "default": (255, 255, 255)
        }

        self.rendered_txt = self.font.render(str(value), True, colors[dmg_type])

        self.rect = self.rendered_txt.get_rect(center=(rect.x + rect.w // 2, rect.y - 45))
        self.init_time = pg.time.get_ticks()
        self.velocity_y = 7

        self.direction = "left" if randint(0, 1) == 0 else "right"

    def update(self, scroll):
        self.rect.x += 2 if self.direction == "right" else -2

        t = pg.time.get_ticks() - self.init_time
        if t < 550:
            self.rect.y -= 2
        elif t < 1100:
            self.rect.y += 2
        else:
            return "kill"

        self.screen.blit(self.rendered_txt, self.rect.topleft-scroll)
