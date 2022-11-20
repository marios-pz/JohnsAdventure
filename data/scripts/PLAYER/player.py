"""
Credits @Marios325346, @ƒkS124
Here is john, our protagonist.
"""

import pygame as p
import math
from copy import copy
from random import random, randint
from .player_sub.tools import (
    get_crit,
    set_camera_to,
    leveling,
    update_camera_status,
    movement,
    update_ui_animations,
    check_content,
    check_for_interaction,
    check_for_hitting,
    attack,
    get_john,
)
from .player_sub.animation_handler import animation_handing, update_attack

from .player_sub.dash import start_dash, update_dash

import pygame.mask

from ..sound_manager import SoundManager
from ..utils import (
    load,
    get_sprite,
    scale,
    flip_vertical,
    resource_path,
    l_path,
)
from .inventory import Inventory
from .player_stats import UpgradeStation
from .camera import Camera, Follow, Auto
from ..particle_system import DustManager
from ..UI.UI_animation import InteractionName
from ..QUESTS.quest_ui import QuestUI

p.font.init()
debug_font = p.font.Font(resource_path("data/database/menu-font.ttf"), 12)
vec = p.math.Vector2


class Player:
    DEFAULT_VEL = 6

    def __init__(self, game_instance, font, ux, ui, data, cutcene):
        self.game_instance = game_instance
        self.screen, self.InteractPoint = game_instance.DISPLAY, 0
        self.sound_manager = SoundManager(sound_only=True)
        self.base_vel = 10
        self.velocity = p.Vector2(0, 0)  # Player's speed
        self.direction = "left"
        self.move_ability = {
            "left": True,
            "right": True,
            "up": True,
            "down": True,
        }

        self.cutscene = cutcene

        # self.screen_shake = False

        # For displaying npc text
        self.npc_catalog = ux

        # content display (it gets updated by the npcs)
        self.interact_text = ""

        self.paused = (
            self.click
        ) = self.Interactable = self.is_interacting = False  # Features
        self.Right = (
            self.Down
        ) = self.Left = self.Right = self.Up = False  # Movement

        self.data = data
        self.inventory = Inventory(game_instance.DISPLAY, ui)
        self.quest_UI: QuestUI = None
        # will be reassigned later in GameManager.__init__

        # States
        self.walking = False

        # --------------- ANIMATION
        self.sheet = l_path("data/sprites/PLAYER/john.png")
        self.default_attack_sheet = l_path(
            "data/sprites/PLAYER/weapons/sword_sprite_reference.png"
        )

        self.lvl_up_ring = [
            scale(get_sprite(self.sheet, 701 + i * 27, 29, 27, 21), 4)
            for i in range(5)
        ]
        self.ring_lu = False
        self.current_frame_ring = self.lvl_up_ring[0]
        self.delay_rlu = 0
        self.id_rlu = 0
        self.index_animation = 0
        self.delay_animation = 0
        self.anim = get_john(self)

        # ---------------- PLAYER CONTENT

        self.rect = self.anim["right"][0].get_rect()  # This gets changed later
        self.dust_particle_effet = DustManager(10, self, self.screen)

        # ----------------- CAMERA SETTINGS
        self.camera = Camera(self, game_instance.DISPLAY)
        self.camera_mode = {
            # Follows the player
            "follow": Follow(self.camera, self),
            # Camera moves on its own without user's input
            "auto": Auto(self.camera, self),
        }

        # Default camera mode
        self.camera_status = "auto"
        # How to change the camera:
        set_camera_to(self.camera, self.camera_mode, self.camera_status)

        # For the animation/hitbox
        self.looking_down = (
            self.looking_up
        ) = self.looking_left = self.looking_right = False

        # saving player's direction in animation handler
        self.last_movement = "right"

        # For the animation
        self.index_attack_animation = self.delay_attack_animation = 0

        self.restart_animation = True
        self.attacking_frame = self.anim["left_a_2"][
            self.index_attack_animation
        ]

        # ------------------- STATS

        # The width for the UI is 180, but we need to find a way to put less health and keep the width -> width /
        # max_hp * hp
        self.level = 1
        self.health_potions = 10
        self.health = 50
        self.maximum_health = self.health
        self.health_ratio = self.maximum_health / 200
        self.health_target = self.health  # for the enemies

        self.backup_hp = self.maximum_health

        self.health_colours = {
            "normal": (255, 0, 0),
            "health_gen": (0, 255, 0),
            "attacked": (255, 255, 0),
        }
        self.damage = 12
        self.endurance = 15
        self.critical_chance = 0.051  # The critical change the player has gathered without the weapon
        self.xp = 0  # Will soon be loaded from json

        # Code for Dash Ability goes here
        self.dash_width = 200  # the pixel width for bars
        self.dash_cd = 750
        self.last_dash_end = self.dash_start = 0
        self.dashing = False
        self.dashing_direction = None
        self.dash_available = True
        self.delay_increasing_dash = (
            self.delay_dash_animation
        ) = self.index_dash_animation = 0
        self.current_dashing_frame = None

        # Levelling # XP
        self.experience = 0  # Will get data from json soon
        self.experience_width = 0  # This is for the UI
        self.level_index = 1

        # recalculate the damages, considering the equiped weapon
        self.modified_damages = self.damage + (
            self.inventory.get_equipped("Weapon").damage
            if self.inventory.get_equipped("Weapon") is not None
            else 0
        )

        self.upgrade_station = UpgradeStation(
            ui,
            p.font.Font(resource_path("data/database/menu-font.ttf"), 13),
            self,
        )

        # ---------------------------- UI
        self.health_box = scale(ui.parse_sprite("health"), 3)
        self.hp_box_rect = self.health_box.get_rect(
            topleft=(
                self.screen.get_width() - self.health_box.get_width() - 90,
                20,
            )
        )

        # --------------------------- COMBAT SYSTEM
        self.attack_pointer = l_path("data/ui/attack_pointer.png", True)
        self.attacking = False
        self.current_combo = 0
        # The number of attacks, last is rewarding extra damage
        self.last_attack = 3

        # ticks value in the future
        self.last_attacking_click = 0

        self.attack_cooldown = 475
        self.attack_speed = 110

        self.max_combo_multiplier = 1.025
        self.last_combo_hit_time = 0
        self.next_combo_available = True
        self.attacking = False
        self.attacking_hitbox: p.Rect = p.Rect(0, 0, 0, 0)
        # reversed when up or down -> (100, 250)
        self.attacking_hitbox_size = (
            self.rect.height // 2,
            self.rect.width // 2,
        )

        self.rooms_objects = []

        # animation for interaction purposes
        self.UI_interaction_anim: list[InteractionName] = []
        self.interacting_with = None

        self.show_notif = False

        self.custom_center = self.anim["right"][0].get_height() * 4 / 5

        # knock back
        self.knockable = True
        self.knocked_back = False  # true if currently affected by a knock back
        self.knock_back_duration = (
            0  # duration in ms of the knock back movement
        )
        self.start_knock_back = 0  # time of starting the knock back
        self.knock_back_vel = p.Vector2(0, 0)  # movement vel
        self.knock_back_friction = p.Vector2(0, 0)  # slowing down
        self.knock_back_vel_y = 0  # jumpy effect vel

    def handle_health(self, dt):

        # Balance numbers before UI
        if self.health_target >= self.maximum_health:
            self.health_target = self.maximum_health

        # Continue UI
        if self.health < self.health_target:
            self.health += 1  # delta time goes here
            health_bar = p.Rect(
                *self.hp_box_rect.topleft + vec(10, 10),
                int(self.health / self.health_ratio),
                40
            )
            difference = (
                int((self.health_target - self.health) / self.health_ratio)
                - 10
            )
            transition_bar = p.Rect(
                *health_bar.topright - vec(20, 0), difference, 40
            )
            p.draw.rect(
                self.screen,
                self.health_colours["health_gen"],
                transition_bar,
                40,
            )

        # Balance Health numbers
        if self.health >= self.maximum_health:
            self.health = self.maximum_health

    def handle_damage(self, dt):
        if self.health_target < self.health:
            self.health -= 1  # delta time goes here
            health_bar = p.Rect(
                *self.hp_box_rect.topleft + vec(10, 10),
                int(self.health / self.health_ratio),
                40
            )
            difference = int(
                (self.health - self.health_target) / self.health_ratio
            )
            transition_bar = p.Rect(*health_bar.topright, difference, 40)
            p.draw.rect(
                self.screen,
                self.health_colours["attacked"],
                transition_bar,
                40,
            )

        if self.health <= 0:
            # Death SIGNAL
            self.health = 0

    def update_knockback(self, dt):
        if self.knocked_back and self.knockable:
            side_dir_kb = "left" if self.knock_back_vel[0] < 0 else "right"
            other_dir_kb = "up" if self.knock_back_vel[1] < 0 else "down"

            if (
                p.time.get_ticks() - self.start_knock_back
                > self.knock_back_duration
            ):
                self.knocked_back = False

            if (
                p.time.get_ticks() - self.start_knock_back
                > self.knock_back_duration / 2
            ):
                self.rect.y += (
                    self.knock_back_vel_y * dt * 35
                    if self.move_ability["down"]
                    else 0
                )
            else:  # will later be changed to player's crit damage / endurance
                self.rect.y -= (
                    self.knock_back_vel_y * dt * 35
                    if self.move_ability["up"]
                    else 0
                )

            self.rect.x += (
                self.knock_back_vel[0] * dt * 35
                if self.move_ability[side_dir_kb]
                else 0
            )
            self.rect.y += (
                self.knock_back_vel[1] * dt * 35
                if self.move_ability[other_dir_kb]
                else 0
            )
            self.knock_back_vel -= self.knock_back_friction

    def handler(self, dt, exit_rects):
        if not self.InteractPoint:
            self.interacting_with = None

        player_p = (
            # 52 48 are players height and width
            self.rect.x - 52 - self.camera.offset.x,
            self.rect.y - self.camera.offset.y - 48,
        )
        m = p.mouse.get_pos()

        leveling(self)

        self.controls(player_p)

        check_for_interaction(self, exit_rects)
        update_ui_animations(self, dt)  # works
        animation_handing(self, dt, m, player_p)

        if self.camera_status != "auto":
            self.update_knockback(dt)
            movement(self)
            self.handle_damage(dt)
            self.handle_health(dt)

        # Update the camera: ALWAYS LAST LINE
        update_camera_status(self)  # works
        self.camera.scroll()

    def update(self, dt, exit_rects):
        # Function that handles everything :brain:
        self.handler(dt, exit_rects)

    def controls(self, pos):
        """
        Getting input from the user
        """
        for e in p.event.get():
            keys = p.key.get_pressed()
            self.click = False
            a = self.data["controls"]

            if e.type == p.QUIT:
                self.game_instance.quit_()

            if (
                self.game_instance.cutscene_engine.state != "inactive"
            ):  # if cutscene is playing, disallow all the keys
                break

            if not self.inventory.show_menu:
                self.Up = keys[a["up"]]
                self.Down = keys[a["down"]]
                self.Right = keys[a["left"]]
                self.Left = keys[a["right"]]

            dash = a["dash"]
            inv = a["inventory"]
            itr = a["interact"]
            heal = a["healing"]
            fullscreen = a["fullscreen"]

            self.velocity = (
                p.Vector2(-self.base_vel, self.base_vel)
                if not self.paused
                else p.Vector2(0, 0)
            )

            # Reset Interaction
            if True in {self.Up, self.Down, self.Right, self.Left}:
                self.walking = True
                self.InteractPoint, self.Interactable = 0, False
                self.is_interacting = False
                self.npc_catalog.reset()
                # It finds for that one NPC that the player interacted with and it goes back to walking
                for obj in self.rooms_objects:
                    if (
                        hasattr(obj, "IDENTITY")
                        and obj.IDENTITY == "NPC"
                        and not self.is_interacting
                    ):
                        obj.interacting = False
                        break  # Stop the for loop to save calculations
            match e.type:

                case p.KEYDOWN:

                    if e.key == fullscreen:
                        p.display.toggle_fullscreen()

                    if e.key == p.K_ESCAPE:
                        self.paused = True
                        # self.sound_manager.play_music("main_theme")

                    if e.key == heal:
                        if (
                            self.health_potions > 0
                            and self.health < self.maximum_health
                        ):
                            self.sound_manager.play_sound("HealUp")
                            self.health_target += 40
                            self.health_potions -= 1

                    # Temporar until we get a smart python ver
                    if e.key == inv and self.camera_status != "auto":
                        self.Left = self.Right = self.Up = self.Down = False
                        self.walking = False
                        self.inventory.set_active()
                        self.upgrade_station.set_active()
                        self.quest_UI.set_active()

                    if (
                        e.key == dash
                        and self.camera_status != "auto"
                        and not self.inventory.show_menu
                        and not self.attacking
                    ):
                        start_dash(self)

                    if e.key == itr:
                        if (
                            self.InteractPoint + 1 >= 3
                        ):  # if interaction point is 3, then reset the animation
                            self.InteractPoint = 0
                            self.Interactable = self.is_interacting = False
                            self.npc_catalog.reset()
                            self.Left = self.Right = False

                        else:  # else do the usual things
                            self.Interactable = True
                            check_content(self, pos)
                            self.InteractPoint += 1

                case p.MOUSEBUTTONDOWN:
                    match e.button:
                        # left click
                        case 1:
                            click_result1 = self.inventory.handle_clicks(
                                e.pos, self
                            )
                            click_result2 = self.upgrade_station.handle_clicks(
                                e.pos
                            )
                            click_result3 = self.quest_UI.handle_clicks(e.pos)
                            changed_activities = False
                            if (
                                self.inventory.show_menu
                                and self.upgrade_station.show_menu
                            ):
                                if (
                                    not self.inventory.im_rect.collidepoint(
                                        e.pos
                                    )
                                    and not self.upgrade_station.us_rect.collidepoint(
                                        e.pos
                                    )
                                    and not click_result3
                                ):
                                    self.inventory.set_active()
                                    self.upgrade_station.set_active()
                                    self.quest_UI.set_active()
                                    changed_activities = True

                            # Attack only on the below conditions, and of course if he has a weapon
                            if (
                                not self.inventory.show_menu
                                and not self.upgrade_station.show_menu
                                and not changed_activities
                                and not self.dashing
                            ):
                                if (
                                    self.inventory.get_equipped("Weapon")
                                    is not None
                                ):
                                    attack(self, pos)

                            self.click = True
                        # scroll up
                        case 4:
                            if self.inventory.show_menu:
                                self.inventory.scroll_up()
                        # scroll down
                        case 5:
                            if self.inventory.show_menu:
                                self.inventory.scroll_down()
