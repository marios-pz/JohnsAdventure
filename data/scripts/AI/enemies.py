from math import ceil
import pygame as pg
from .enemy import Enemy
from ..utils import resource_path


class Dummy(Enemy):
    def __init__(
        self,
        level_instance,
        pos: tuple[int, int],
        hp: int = 100,
        xp_drop=105,
    ):
        super().__init__(
            level_instance,
            pos,
            hp=100,
            xp_drop=210,
            custom_rect=[8 * 4 + 2, 34 + 17, (24 - 8) * 4, 34 * 4],
            enemy_type="static",
        )
        self.load_animation(
            resource_path("data/sprites/dummy.png"),
            idle="static",
            hit_anim="animated",
            idle_coo=[0, 0, 34, 48, 1, 4],
            hit_coo=[0, 48, 34, 48, 4, 4],
        )
        self.custom_center = int(self.rect.h * 4 / 5)
        self.xp_drop = self.xp_available = xp_drop
        self.scale = 4
        self.damage = 10


class ShadowDummy(Enemy):
    def __init__(
        self,
        level_instance,
        pos: tuple[int, int],
        hp: int = 100,
        xp_drop=25,
    ):
        # OC formula
        # calc_intensity = ceil(damage * health ) / xp_drop (this process must be automated instead of passed in
        # __init__)

        calc_intensity = ceil(
            12 * hp / xp_drop
        )  # 12 will be re-written else where later

        super().__init__(
            level_instance,
            pos,
            hp=65,
            xp_drop=65,
            custom_rect=[10, 25, 29 * 3, 24 * 3],
            enemy_type="shadow",
            intensiveness=calc_intensity,
            vel=2,
            up_hitbox=(128, 128),
            down_hitbox=(128, 128),
            left_hitbox=(128, 128),
            right_hitbox=(128, 128),
        )

        self.load_animation(
            resource_path("data/sprites/shadow_dummie.png"),
            idle="static",
            hit_anim="animated",
            walk_anim="animated",
            attack_anim="animated",
            idle_coo=[0, 0, 29, 24, 1, 4],
            walk_d_coo=[0, 25, 29, 24, 5, 4],
            walk_l_coo=[0, 0, 29, 24, 5, 4],
            walk_r_coo=[0, 25, 29, 24, 5, 4],
            walk_u_coo=[0, 0, 29, 24, 5, 4],
            attack_d_coo=[0, 50, 29, 24, 5, 4],
            attack_l_coo=[0, 50, 29, 24, 5, 4],
            attack_r_coo=[0, 75, 29, 24, 5, 4],
            attack_u_coo=[0, 75, 29, 24, 5, 4],
        )
        self.custom_center = 24 * 3 * 4 / 5
        self.xp_drop = self.xp_available = xp_drop
        self.scale = 4
        self.damage = 2
        self.knock_back = {"duration": 150, "vel": 3, "friction": 2.5}


class Guardian(Enemy):
    def __init__(
        self,
        level_instance,
        pos: tuple[int, int],
        hp: int = 100,
        xp_drop=45,
    ):
        super().__init__(
            level_instance,
            pos,
            hp=175,
            xp_drop=210,
            custom_rect=[25 * 5 + 10, 50, 29 * 2, 45 * 2 + 25],
            enemy_type="normal",
            vel=1,
            up_hitbox=(18 * 5, 128),
            down_hitbox=(18 * 5, 128),
            left_hitbox=(34 * 5, 128),
            right_hitbox=(34 * 5, 128),
        )

        self.load_animation(
            resource_path("data/sprites/guardian_sheet.png"),
            idle="static",
            hit_anim="animated",
            walk_anim="animated",
            attack_anim="animated",
            idle_coo=[0, 0, 67, 34, 1, 5],
            walk_d_coo=[0, 0, 67, 34, 5, 5],
            walk_l_coo=[0, 0, 67, 34, 5, 5],
            walk_r_coo=[0, 0, 67, 34, 5, 5],
            walk_u_coo=[0, 0, 67, 34, 5, 5],
            attack_d_coo=[0, 34, 67, 34, 5, 5],
            attack_l_coo=[0, 34, 67, 34, 5, 5],
            attack_r_coo=[0, 34, 67, 34, 5, 5],
            attack_u_coo=[0, 34, 67, 34, 5, 5],
            flip_anim=True,
        )
        self.health_bar_width = 45 * 2
        self.custom_center = (45 * 2 + 25) * 4 / 5
        self.xp_drop = self.xp_available = xp_drop
        self.damage = 4
        self.scale = 4


class Goblin(Enemy):
    def __init__(
        self,
        level_instance,
        pos: tuple[int, int],
        hp: int = 100,
        xp_drop=45,
    ):
        super().__init__(
            level_instance,
            pos,
            hp=65,
            xp_drop=45,
            custom_rect=[15, 35, 17 * 2, 25 * 2 + 10],
            enemy_type="normal",
            vel=3,
            up_hitbox=(17 * 4, 92),
            down_hitbox=(17 * 4, 92),
            left_hitbox=(15 * 4, 92),
            right_hitbox=(15 * 4, 92),
        )

        self.load_animation(
            resource_path("data/sprites/goblin_template.png"),
            idle="static",
            hit_anim="animated",
            walk_anim="animated",
            attack_anim="animated",
            idle_coo=[0, 0, 17, 25, 1, 4],
            walk_d_coo=[0, 0, 17, 25, 5, 4],
            walk_l_coo=[0, 0, 17, 25, 5, 4],
            walk_r_coo=[0, 0, 17, 25, 5, 4],
            walk_u_coo=[0, 0, 17, 25, 5, 4],
            attack_d_coo=[0, 25, 17, 25, 5, 4],
            attack_l_coo=[0, 25, 17, 25, 5, 4],
            attack_r_coo=[0, 25, 17, 25, 5, 4],
            attack_u_coo=[0, 25, 17, 25, 5, 4],
            flip_anim=True,
        )

        self.damage = 3
        self.custom_center = (25 * 2 + 10) * 4 / 5
        self.xp_drop = self.xp_available = xp_drop
        self.scale = 2


class BigShadowDummy(Enemy):
    def __init__(
        self,
        level_instance,
        pos: tuple[int, int],
        hp: int = 1650,
        xp_drop: int = 350,
    ):
        calc_intensity = ceil(5 * hp / xp_drop)  # 12 is the damages

        super().__init__(
            level_instance,
            pos,
            hp,
            xp_drop,
            custom_rect=[50, 50, 29 * 4, 24 * 6],
            enemy_type="boss",
            intensiveness=calc_intensity,
            vel=1,
            up_hitbox=(29 * 8, 24 * 13),
            down_hitbox=(29 * 8, 24 * 13),
            left_hitbox=(29 * 8, 24 * 13),
            right_hitbox=(29 * 8, 24 * 13),
        )
        self.boss_name = "The Big Dummie"
        self.attacking_distance = 190

        self.custom_center = 24 * 6 * 4 / 5
        self.xp_drop = self.xp_available = xp_drop
        self.scale = 4
        self.damage = 7

        self.load_animation(
            resource_path("data/sprites/shadow_dummie.png"),
            idle="static",
            hit_anim="animated",
            walk_anim="animated",
            attack_anim="animated",
            idle_coo=[0, 0, 29, 24, 1, 8],
            walk_d_coo=[0, 25, 29, 24, 5, 8],
            walk_l_coo=[0, 0, 29, 24, 5, 8],
            walk_r_coo=[0, 25, 29, 24, 5, 8],
            walk_u_coo=[0, 0, 29, 24, 5, 8],
            attack_d_coo=[0, 50, 29, 24, 5, 8],
            attack_l_coo=[0, 50, 29, 24, 5, 8],
            attack_r_coo=[0, 75, 29, 24, 5, 8],
            attack_u_coo=[0, 75, 29, 24, 5, 8],
        )
