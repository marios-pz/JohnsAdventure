from math import ceil
import pygame as pg
from copy import copy
from ..utils import (
    l_path,
    load,
    get_sprite,
    smooth_scale,
    scale,
    resource_path,
)
from .player_sub.tools import load_attack_anim


class Items:
    """This class will contain all the objects"""

    class NullItem:  # Reference Model
        def __init__(self):
            font = pg.font.Font(
                resource_path("data/database/menu-font.ttf"), 24
            )
            self.text = font.render("NullItem", True, (0, 0, 0))
            self.image = pg.Surface((self.text.get_size()))
            self.image.fill((255, 204, 0))
            self.image.blit(self.text, (0, 0))
            self.rect = self.image.get_rect()

        def handle_clicks(self, pos):
            pass

        def update(self, surf, pos):
            self.rect.topleft = pos
            surf.blit(self.image, pos)


class Weapon:
    def __init__(self, dmg: int, crit_chance: float, sheet: str):

        self.icon = pg.Surface((25, 25))
        self.type = "Weapon"
        self.font = pg.font.Font(
            resource_path("data/database/menu-font.ttf"), 14
        )
        self.text = self.font.render(self.__class__.__name__, True, (0, 0, 0))
        self.stat = self.font.render(" +1", True, (255, 0, 255))
        self.eq = self.font.render(
            ">", True, (255, 0, 0)
        )  # to replace with an image later on
        self.damage = dmg
        self.critical_chance = crit_chance

        self.sound: str = ""

        self.image = pg.Surface(
            (
                self.text.get_width()
                + self.stat.get_width()
                + self.eq.get_width(),
                self.text.get_height(),
            )
        )
        self.image.fill((239, 159, 26))
        self.image.blit(self.text, (0, 0))
        self.image.blit(self.stat, (self.text.get_width(), 0))
        self.equipped = False
        self.rect = self.image.get_rect()

        self.KB = False  # define if the knock back is applying to this weapon
        self.knock_back = {"duration": 0, "vel": 0, "friction": 0}

        self.sheet = l_path(sheet, alpha=False)

    def start_special_effect(self, obj: object):
        # Here the devs can pass a function to start a special effect

        pass

    def special_effect(self, player_instance):
        # Here the devs can pass a function that affect the object hit by a special effect

        pass

    def update(self, surf, pos, dmg, add_pos=(0, 0)):
        d_dmg = (
            self.damage - dmg
        )  # getting the difference from the player's damages and the current item's damages
        txt_stat = (
            (" +" if d_dmg >= 0 else " ") + str(d_dmg)
            if not self.equipped
            else ""
        )
        color = (
            (0, 255, 0)
            if d_dmg > 0
            else (
                (100 if d_dmg == 0 else 255),
                (100 if d_dmg == 0 else 0),
                (100 if d_dmg == 0 else 0),
            )
        )  # grey if the d_dmg is 0, green if > 0, red if < 0
        self.stat = self.font.render(
            txt_stat, True, color
        )  # resetting the stat rendering

        self.image.fill((239, 159, 26))
        rect = copy(self.rect)
        rect.topleft += pg.Vector2(add_pos)
        if rect.collidepoint(pg.mouse.get_pos()):
            self.image.fill((219, 139, 6))

        if not self.equipped:
            self.image.blit(self.text, (0, 0))
            self.image.blit(self.stat, (self.text.get_width(), 0))
        else:
            self.image.blit(self.eq, (0, 0))
            self.image.blit(self.text, (self.eq.get_width(), 0))
            self.image.blit(
                self.stat, (self.text.get_width() + self.eq.get_width(), 0)
            )
        self.rect.topleft = pos
        surf.blit(self.image, pos)

    def handle_clicks(self, pos, player):
        if self.rect.collidepoint(pos):
            return self.set_equiped(player)  # Un/Equips clicked item

    def set_equiped(self, player):
        self.equipped = not self.equipped
        if self.equipped:
            load_attack_anim(player, self.sheet)
        return self.equipped, self.type, self


class Training_Sword(Weapon):
    def __init__(self):
        super().__init__(
            dmg=5,
            crit_chance=0.1,
            sheet="data/sprites/PLAYER/weapons/training_sword.png",
        )
        self.icon = l_path(
            "data/sprites/items/wooden_sword_item.png", alpha=True
        )

        self.sound: str = "woodenSword"

        # This knockback is temporar, we will update the system when its time
        self.KB = True
        self.knock_back = {"duration": 150, "vel": 10, "friction": 0.1}


class ManosSword(Weapon):
    def __init__(self):
        super().__init__(
            dmg=15,
            crit_chance=0.15,
            sheet="data/sprites/PLAYER/weapons/knight_sword.png",
        )
        self.KB = True
        self.knock_back = {"duration": 150, "vel": 10, "friction": 0.1}
        self.icon = l_path(
            "data/sprites/items/knight_sword_item.png", alpha=True
        )

        self.sound: str = "manosSword"

        self.obj_bleeding = []
        self.start_bleed = {}
        self.bleed_duration = 500
        self.last_tick = {}
        self.tick_cd = 50
        self.bleed_damages = ceil(self.damage * 0.01)
        self.affecting_bleed = {}

    def start_special_effect(self, obj: object):
        if obj not in self.obj_bleeding:
            self.obj_bleeding.append(obj)
            self.start_bleed[id(obj)] = pg.time.get_ticks()
            self.affecting_bleed[id(obj)] = True
            self.last_tick[id(obj)] = pg.time.get_ticks()
        else:
            if not self.affecting_bleed[id(obj)]:
                self.start_bleed[id(obj)] = pg.time.get_ticks()
                self.affecting_bleed[id(obj)] = True
                self.last_tick[id(obj)] = pg.time.get_ticks()

    def special_effect(self, player_instance):

        """Apply bleeding effect, if the cooldown has passed,"""

        for obj in self.obj_bleeding:

            if (
                pg.time.get_ticks() - self.start_bleed[id(obj)]
                > self.bleed_duration
            ):
                self.affecting_bleed[id(obj)] = False
            else:
                if (
                    pg.time.get_ticks() - self.last_tick[id(obj)]
                    > self.tick_cd
                ):
                    self.last_tick[id(obj)] = pg.time.get_ticks()
                    obj.deal_damage(
                        self.bleed_damages, False, endurance_ignorance=True
                    )
                    if obj.hp <= 0:
                        player_instance.experience += obj.xp_available
                        obj.xp_available = 0


class ItemSorter:
    weapons = {"Training_Sword": Training_Sword, "ManosSword": ManosSword}
