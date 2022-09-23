import pygame as pg
from ..utils import l_path, get_sprite, scale
from random import randint
import threading
from copy import copy
import time


def input_d(instance, image, pos, sprite_scale):
    instance.animations.append(DeathAnim(image, pos, sprite_scale))


class DeathManager:

    """Contains all the dead object in order to animate their death. It's useful to save memory, by deleting the
    whole enemy objects, and just transmitting the image and position."""

    def __init__(self, DISPLAY, camera):
        self.DISPLAY, self.camera = DISPLAY, camera

        # contains all the animations going on
        self.animations = []

    def input_death_animation(self, image, pos, sprite_scale):

        # Removed the thread cause it slows down main program

        #calculating_thread = threading.Thread(target=input_d, args=(self, image, pos, sprite_scale))
        #calculating_thread.start()

        input_d(self, image, pos, sprite_scale)


class DeathAnim:

    def __init__(self, image, pos, sprite_scale):
        self.image, self.pos = image, pos
        self.rect = self.image.get_rect(topleft=pos)

        self.particles = []

        debut = time.time()

        px_width = sprite_scale
        px_height = sprite_scale
        length_y = 1

        surf = pg.surfarray.array3d(self.image).swapaxes(0, 1)

        # Increase the pixel depth pretty please
        for y in range(0, len(surf), sprite_scale):
            for x in range(0, len(surf[y]), sprite_scale):
                if not (surf[y][x][0] == 255 and surf[y][x][1] == 255 and surf[y][x][2] == 255):
                    self.particles.append(
                        DestructedParticle(
                            (sprite_scale * 2, sprite_scale * 2), self.rect.topleft + pg.Vector2(x, y), surf[y][x], length_y*y
                        )
                    )

        for particle in self.particles:
            particle.delay = [pg.time.get_ticks(), pg.time.get_ticks()]

    def update(self, screen, scroll, death_anim_manager):

        to_remove = []
        for particle in self.particles:
            upd = particle.update(screen, scroll)
            if upd == "kill":
                to_remove.append(particle)

        for removing in to_remove:
            self.particles.remove(removing)

        if len(self.particles) == 0:
            death_anim_manager.animations.remove(self)

class DestructedParticle:

    def __init__(self, size, pos, color, delay):

        self.image = pg.Surface(size, pg.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)
        self.color = list(color)
        self.image.fill(color)
        self.tend_color = (192, 160, 128, 255)

        self.start_time = pg.time.get_ticks() + delay
        self.last_time = 2500
        self.delay = [0, 0]
        self.WIDTH = self.image.get_width()

        self.dy = 1
        self.count = 0

    def whiter(self, step):
        if self.color[0] < 255:
            self.color[0] += 1
        if self.color[1] < 255:
            self.color[1] += 1
        if self.color[2] < 255:
            self.color[2] += 1

    def behavior(self):
        if pg.time.get_ticks() > self.start_time:

            self.rect.y -= self.dy
            self.rect.x += randint(-1, 1)
            if pg.time.get_ticks() - self.delay[0] > (self.last_time // 255):
                self.delay[0] = pg.time.get_ticks()
                self.image.set_alpha(self.image.get_alpha()-2)
            if pg.time.get_ticks() - self.delay[1] > (self.last_time // self.WIDTH):
                self.delay[1] = pg.time.get_ticks()
                alpha = self.image.get_alpha()

                try:
                    self.image = pg.Surface((self.image.get_width()-1, self.image.get_height()-1), pg.SRCALPHA)
                except pg.error:
                    pass
                self.rect.topleft += pg.Vector2(0.5, 0.5)
                self.image.set_alpha(alpha)
                self.image.fill(self.color)

    def update(self, screen, scroll):
        self.behavior()
        screen.blit(self.image, self.rect.topleft-scroll)
        if pg.time.get_ticks() - self.start_time > self.last_time:
            return "kill"
