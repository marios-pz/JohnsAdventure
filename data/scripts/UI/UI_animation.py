import pygame as pg
from copy import copy


class UiAnimation:

    def __init__(self, display):
        self.display = display
        self.W, self.H = self.display.get_size()
        self.alive = True

    def kill(self):
        # start killing process
        # -> self.alive = False
        pass

    def logic(self, scroll, dt):
        # animation logic
        pass

    def update(self, scroll, dt):
        self.logic(scroll, dt)
        return self.alive


class InteractionName(UiAnimation):

    def __init__(self, tag: str, display: pg.Surface, pos: pg.Vector2, name: str, font: pg.font.Font, color: pg.Color):
        super().__init__(display)
        self.tag = tag
        self.direction = pg.Vector2(5, -5)
        self.vel = copy(self.direction)
        self.vel.scale_to_length(3)
        self.dying = False
        self.points = [copy(pos), copy(pos), copy(pos)]
        self.phase = 1
        self.render = font.render(name, True, color)
        self.color = color

    def restart(self):
        if self.dying:
            self.dying = False
            self.phase = 1

    def kill(self):
        self.dying = True
        self.phase = 1

    def logic(self, scroll, dt):
        if not self.dying:
            if self.phase == 1:
                self.points[1] += self.vel * dt * 35
                if self.points[0].distance_to(self.points[1]) > 15:
                    self.phase += 1
                    self.points[2] = copy(self.points[1])
            elif self.phase == 2:
                self.points[2][0] += self.vel.length() * 7 * dt * 35
                if self.points[1].distance_to(self.points[2]) > self.render.get_width() * 1.3:
                    self.phase += 1
        else:
            if self.phase == 1:
                self.points[2][0] -= self.vel.length() * 7 * dt * 35
                if self.points[2][0] <= self.points[1][0]:
                    self.phase += 1
                    self.points[2] = copy(self.points[1])
            elif self.phase == 2:
                self.points[2] = copy(self.points[1])
                self.points[1] -= self.vel * dt * 35
                if self.points[1].distance_to(self.points[0]) <= 2:
                    self.alive = False
        if self.phase == 3:
            self.display.blit(self.render, self.render.get_rect(
                centerx=((1 / 2) * (self.points[2][0] + self.points[1][0])) - scroll[0],
                bottom=self.points[2][1] - 5 - scroll[1]
            ))
        pg.draw.lines(self.display, self.color, False, [point-scroll for point in self.points], width=3)
