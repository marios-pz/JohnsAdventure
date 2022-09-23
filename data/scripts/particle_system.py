import pygame as pg
from copy import copy
from random import randint, choice, gauss
from .particles_templates import Particle, ParticleManager
from .utils import scale

from math import pow


class Shadow_Particle(Particle):
    
    def __init__(self, image, pos, last_time, camera):
        super().__init__(image, pos, last_time, camera)
        self.image.fill(pg.Color("#6c25be"))
        self.dy = 1
        self.dx = 2
        
    def behavior(self):
        """[It's supposed to fly upwards and and move randomly left and right, showing aura]
        """
        self.rect.y -= self.dy 
        # Change the below to randint(-self.dx, self.dy) later
        self.rect.x += randint(-self.dx, self.dx)
        
class Shadow_Manager(ParticleManager):
    def __init__(self, intensity, player, screen, enemy):
        super(Shadow_Manager, self).__init__(player)
        self.intensity, self.screen = intensity, screen 
        # Pick Particle
        self.particle_object = Shadow_Particle
        self.duration = randint(1000, 1750)
        # Size Particle
        self.size = pg.Surface((intensity // 2, intensity // 2))
        self.enemy = enemy
        
    def logic(self) -> bool:
        if self.trigger_check():
            self.add_particles(self.size, self.enemy.particle_scroller, self.duration)
        return True
        
class DustManager(ParticleManager):

    def __init__(self, intensity: int, player_instance, display):
        super(DustManager, self).__init__(player_instance)
        self.particle_object = DustParticle
        self.player = player_instance
        self.display = display
        self.color = [255, 255, 255]
        self.size = (intensity // 2, intensity // 2)
        self.last_player_pos = copy(self.player.rect.midbottom)

    # Checks if the rect has moved at all 
    def trigger_check(self) -> bool:
        return self.get_pl_rect().midbottom != self.last_player_pos

    # Returns a RGB of Higher values by degree, showcasing a darker colour.
    def darker(self, color, degree):
        return [max(c - degree, 0) for c in color]

    def get_pl_rect(self):
        pl_rect = copy(self.player.rect)
        pl_rect.topleft -= pg.Vector2(15, -70)
        pl_rect.w -= 70
        pl_rect.h -= 115
        return pl_rect

    def logic(self) -> bool:
        if self.trigger_check():
            match self.player.direction:
                case "left":
                    val = [(0, 40), (0, 20)]
                case "right":
                    val = [(0, -40), (0, 20)]
                case "up":
                    val = [(-20, 20), (0, -40)]
                case "down":
                    val = [(-20, 20), (0, 40)]
            pl_rect = self.get_pl_rect()
            self.last_player_pos = copy(pl_rect.midbottom)

            # Suppressing the error when the player is in a loading situation
            # Or edge of the background
            try:    
                self.add_particles(
                    self.size,
                    (pl_rect.centerx + (randint(min(val[0]), max(val[0]))),
                        pl_rect.bottom - randint(min(val[1]), max(val[1]))),
                    self.darker(self.display.get_at(
                        (int(self.last_player_pos[0] - self.player.camera.offset.x),
                            int(self.last_player_pos[1] + 1 - self.player.camera.offset.y))
                    ), 20),
                    400
                    )
            except Exception as e:
                pass
            return True
        return False

class DustParticle(Particle):

    def __init__(self, size: tuple[int, int], pos: pg.Vector2, color: tuple[int, int, int], last_time, camera):
        super().__init__(
            image=pg.Surface(size),
            pos=pos,
            last_time=last_time,
            camera=camera
        )
        self.image.fill(color)
        self.dy = 1

    def behavior(self):
        """
            Gives a wiggly effect into the particles 
        """
        self.rect.y += -self.dy if pg.time.get_ticks() - self.begin_time < self.last_time // 2 else self.dy
        
class SmokeManager(ParticleManager):
    def __init__(self, pos, size, player_instance):
        super(SmokeManager, self).__init__(player_instance)
        self.particle_object = SmokeParticle
        self.player = player_instance
        self.colors = [
            (150, 150, 150),
            (152, 152, 152),
            (154, 154, 154),
            (156, 156, 156),
        ]
        self.pos = pos
        self.size = size
        self.height = 1600
        self.duration = [4000, 4500]
        self.last_len = len(self.particles)
        for i in range(4):
            rad = int(gauss(*self.size))
            self.add_particles(rad, pg.Vector2(pos) - pg.Vector2(20, rad * 1.5), choice(self.colors), self.height,
                               randint(*self.duration))

    def trigger_check(self) -> bool:
        return self.last_len != len(self.particles)

    def logic(self) -> bool:

        if self.trigger_check():
            rad = int(gauss(*self.size))
            self.add_particles(rad, pg.Vector2(self.pos) - pg.Vector2(35, rad * 1.3), choice(self.colors), self.height,
                               randint(*self.duration))

        return True


class SmokeParticle(Particle):

    def __init__(self, radius: int, pos: pg.Vector2, color: tuple[int, int, int], max_height: int, last_time, camera):
        super().__init__(
            image=pg.Surface((radius // 2, radius // 2), pg.SRCALPHA),
            pos=pos,
            last_time=last_time,
            camera=camera
        )
        self.dep_pos = pos
        pg.draw.circle(self.image, color, (radius // 4, radius // 4), radius // 4)
        self.image = scale(self.image, 4.5)
        self.dp = pg.Vector2(1, 1)
        self.max_height = max_height
        self.delay = pg.time.get_ticks()
        self.cond = choice([True, False])

    def behavior(self):
        self.image.set_alpha(180 - ((pg.time.get_ticks() - self.begin_time) / self.last_time) * 180)
        if pg.time.get_ticks() - self.delay > 200:
            self.cond = not self.cond
            self.delay = pg.time.get_ticks()
        self.rect.topleft += pg.Vector2(-gauss(self.dp[0], 1) if self.cond else gauss(self.dp[0], 1), -self.dp[1])

    def render(self, screen):
        update = super().render(screen)
        if pg.Vector2(self.pos).distance_to(pg.Vector2(self.dep_pos)) > self.max_height:
            return "kill"
        return update


PARTICLE_EFFECTS = {
    "smoke": SmokeManager,
    "dust": DustManager
}
