import random

import pygame as pg
from pygame import Rect
from copy import copy
from operator import attrgetter
import json
from random import gauss, randint

from ..PLAYER.player import *
from ..PLAYER.inventory import *
from ..utils import resource_path, load, l_path, flip_vertical, flip_horizontal


from ..AI.enemy import Enemy
from ..AI.death_animator import DeathManager
from .lights_manager import LightManager
from ..props import Prop, PropGetter, Torch
from ..AI.npc import NPC, MovingNPC


def get_cutscene_played(id_: str):
    with open(resource_path("data/database/cutscenes.json"), "r") as data:
        return json.load(data)[id_]


vec = pg.math.Vector2


class GameState:
    """Parent class of every level.
    It handles every objects and handle their update method's arguments.
    (These args can of course be different than other objects of the list)"""

    def __init__(
        self,
        player_instance,
        prop_objects,
        id_: str,
        light_state="day",
        has_boss=False,
    ):
        self.id = id_
        # ------- SCREEN -----------------
        self.display, self.screen = (
            player_instance.screen,
            player_instance.screen,
        )
        self.W, self.H = self.display.get_size()
        self.dt = 0  # wil be updated in update method

        # -------- WORLD's OBJECTS ----------
        self.player = player_instance  # get player to pass it as an argument in certain func of obj
        self._PLAYER_VEL = copy(self.player.DEFAULT_VEL)

        self.objects = []
        self.scroll = self.player.camera.offset.xy
        # Get the prop object dict, (basically all the objects generated from open_world.json)
        self.prop_objects = prop_objects

        self.boss_found = False  # To save iterations
        if has_boss:
            self.spawned_boss = False
            self.boss_data = None
            self.boss_name = None
            self.font = pg.font.Font(
                resource_path("data/database/menu-font.ttf"), 36
            )
            self.kill_hp_bar = False
            self.shake_time = pg.time.get_ticks()

        # This might be the reason why players blit at top left for a nano second when you boot the game
        self.world = pg.Surface(
            (1, 1)
        )  # set default values for world -> supposed to be replaced

        # eg. -> "next_state_name" : Rect(0, 0, 100, 100)
        self.exit_rects = {}  # the rects that lead to exit the current room

        # dead objects animations
        self.death_anim_manager = DeathManager(self.screen, self.player.camera)

        self.green_leaf = pg.Surface(
            (
                player_instance.screen.get_width(),
                player_instance.screen.get_height(),
            )
        )
        self.green_leaf.fill((61, 121, 6))
        self.green_leaf.convert()

        # ----------- COLLISION SYSTEM ---------

        self.points_side = {  # -> lambda functions to get the coordinates of the colliding points
            "left": lambda rect, vel: [rect.midleft - vec(-vel[0], 0)],
            "right": lambda rect, vel: [rect.midright - vec(vel[0], 0)],
            "up": lambda rect, vel: [rect.midtop - vec(0, vel[1])],
            "down": lambda rect, vel: [rect.midbottom + vec(0, vel[1])],
        }

        self.spawn = {}
        # previous_state : coords

        # camera script :
        self.cam_index = -1
        self.ended_script = get_cutscene_played(self.id)
        self.camera_script = []
        """
        ** = optional
        [
        {
            "pos": (x, y),
            "duration": (int) ms, -> (can be null -> will just use func look_at)
            ** -> "text": str,  (can be empty) 
            ** -> "wainting_end": (int) ms,
            ** -> "next_cam_status": cam_status
        },
        {
            ... -> same shape : will be played directly after it
        }
        ]
        """
        self.offset_map = vec(0, 0)

        # Light system
        self.light_state = light_state
        self.lights_manager = LightManager(self.screen)
        self.additional_lights = []

        self.step_timer = pg.time.get_ticks()

        self.music_manager = SoundManager(True, False, volume=1)

    def check(self, moving_object, col_obj, side):
        """Given a side of the moving object,
        this function detects the collision between
        the moving object and the collider.

        It handles the change of dictionary of the moving object.

         During the whole func, we use copy to get rects. It's not always useful,
        but it's necessary sometimes, so to prevent from eventual assignement bugs
        we do it by default."""

        m_obj = moving_object
        c_obj = col_obj

        if isinstance(moving_object, Enemy) and isinstance(col_obj, Enemy):
            return  # We allow overlapping of enemies

        # ----------------------------------------------- REFACTOR
        # get the d_collision arguments
        m_d_col = (
            m_obj.d_collision
            if hasattr(moving_object, "d_collision")
            else [0, 0, m_obj.rect.w, m_obj.rect.h]
        )
        if not isinstance(col_obj, Rect):
            c_d_col = (
                c_obj.d_collision
                if hasattr(col_obj, "d_collision")
                else [0, 0, c_obj.rect.w, c_obj.rect.h]
            )
        else:
            c_d_col = None

        # apply the adaptations to the different rects (for the moving object)
        if isinstance(moving_object, Player):
            object_rect = Rect(
                m_obj.rect.x - 15,
                m_obj.rect.y + 70,
                m_obj.rect.w - 70,
                m_obj.rect.h - 115,
            )
            velocity = abs(m_obj.velocity[0]), abs(m_obj.velocity[1])
        elif isinstance(moving_object, Enemy):
            object_rect = Rect(
                m_obj.rect.x + m_d_col[0],
                m_obj.rect.y + m_d_col[1],
                m_d_col[2],
                m_d_col[3],
            )
            velocity = m_obj.BASE_VEL, m_obj.BASE_VEL
            if hasattr(moving_object, "tp_V"):
                if m_obj.tp_V[0] != 0 or m_obj.tp_V[1] != 0:
                    velocity = abs(m_obj.tp_V[0]), abs(m_obj.tp_V[1])
        else:
            velocity = abs(m_obj.velocity[0]), abs(m_obj.velocity[1])
            object_rect = m_obj.rect.copy()

        # apply the adaptations to the different rect
        if isinstance(col_obj, Player):
            collider_rect = Rect(
                c_obj.rect.x - 15,
                c_obj.rect.y + 70,
                c_obj.rect.w - 70,
                c_obj.rect.h - 115,
            )
        elif (
            isinstance(col_obj, Enemy)
            or isinstance(col_obj, NPC)
            or isinstance(col_obj, Prop)
            or isinstance(col_obj, Torch)
        ):
            collider_rect = Rect(
                c_obj.rect.x + c_d_col[0],
                c_obj.rect.y + c_d_col[1],
                *c_d_col[2:],
            )
        else:  # case if the collider is actually just a rect
            collider_rect = col_obj.copy()

        velocity_parser = {
            "left": pg.Vector2(-velocity[0], 0),
            "right": pg.Vector2(velocity[0], 0),
            "down": pg.Vector2(0, velocity[1]),
            "up": pg.Vector2(0, -velocity[1]),
        }

        moved_rect = object_rect.move(*tuple(velocity_parser[side]))
        m_obj.move_ability[side] = not moved_rect.colliderect(collider_rect)
        if not m_obj.move_ability[side]:
            if isinstance(moving_object, Enemy) or isinstance(
                moving_object, MovingNPC
            ):
                if side == m_obj.direction:
                    m_obj.switch_directions(blocked_direction=side)
            return "kill"

    def collision_system(self, obj_moving, objects_to_collide):

        """Basically the function that handles every object and every direction
        of the collide system."""

        for direction in ["left", "right", "down", "up"]:
            for obj in objects_to_collide:
                check = self.check(obj_moving, obj, direction)
                if (
                    check == "kill"
                ):  # a collision has occured on this side, no need to check more, so break
                    if hasattr(obj_moving, "switch_directions"):
                        obj_moving.switch_directions(
                            blocked_direction=direction
                        )  # switch NPCs direction for eg.

                    break

    def update(self, camera, dt) -> None:

        # update the game values
        self.player.rooms_objects = self.objects
        self.player.base_vel = copy(self._PLAYER_VEL)
        self.dt = dt

        # blit the background
        self.screen.blit(self.world, -camera.offset.xy - self.offset_map)

        # get the scroll value and update it
        self.scroll = camera.offset.xy

        # Filter out the objects from Rects
        all_objects = list(
            filter(lambda obj: type(obj) is not pygame.Rect, self.objects)
        )

        # register the objects that will be removed on next frame
        to_remove = []

        for obj_ in all_objects:

            if hasattr(obj_, "custom_center"):
                # apply the custom center
                obj_.centery = obj_.rect.y + obj_.custom_center
            else:
                # just get the centery from the objects' rect
                obj_.centery = obj_.rect.centery

                # check if the current object is a non sortable object (eg. roads), set the centery to 0
                # so it's always under everything
                if hasattr(obj_, "sort") and not obj_.sort:
                    obj_.centery = -1000000

        # do the same as above, but just in the death animation managers objects
        for obj_2 in self.death_anim_manager.animations:
            obj_2.centery = obj_2.rect.centery

        # add these objects to the list
        all_objects.extend(self.death_anim_manager.animations)

        # append the player to the objects (he needs to be sorted and updated too)
        all_objects.append(self.player)
        self.player.centery = self.player.rect.centery

        # update the objects, by ordering them considering their centery
        for obj in sorted(all_objects, key=attrgetter("centery")):

            # method.__code__.co_varnames -> ("arg1", "arg2", "var1", "var2", "var...") of the method
            # so we remove self argument (useless) using [1:x]
            # and we stop when we reach arguments' count gotten by : method.__code__.co_argcount
            # get all the arguments of the func in a list -> the arguments must be found inside this class (GameState)
            # for eg. : def update(self, screen, scroll)
            # self is ignored, screen and scroll are found by getattr(self, "screen") and getattr(self, "scroll")
            if isinstance(obj, Player) and self.id == "credits":
                continue
            obj.update(
                *[
                    getattr(self, arg)
                    for arg in obj.update.__code__.co_varnames[
                        1 : obj.update.__code__.co_argcount
                    ]
                ]
            )

            # add the dead enemies in the death manager
            if hasattr(obj, "IDENTITY"):
                if obj.IDENTITY == "ENEMY":
                    if obj.dead:
                        to_remove.append(obj)
                        scale = 1 if not hasattr(obj, "scale") else obj.scale
                        self.death_anim_manager.input_death_animation(
                            obj.current_sprite, obj.rect.topleft, scale
                        )
                        if obj.enemy_type == "boss":
                            self.kill_hp_bar = True

                    if obj.enemy_type == "boss" and not self.boss_found:
                        self.player.screen_shake = True
                        self.spawned_boss = True
                        self.boss_data = obj
                        self.boss_name = self.font.render(
                            obj.boss_name, True, (255, 255, 255)
                        )
                        self.boss_found = True

        # EXIT FOR LOOP
        if self.boss_found and self.spawned_boss and not self.kill_hp_bar:
            if self.boss_data.show_boss_bar:
                # Shake the camera to show expressions of the boss
                if pg.time.get_ticks() - self.shake_time > 380:
                    power = 4
                    self.player.camera.offset += randint(
                        -power, power
                    ), randint(-power, power)
                    self.shake_time = pg.time.get_ticks()

                pg.draw.rect(
                    self.screen,
                    (0, 0, 0),
                    [200 - 4, 610 - 4, 920 + 4, 68],
                    border_radius=25,
                )

                pg.draw.rect(
                    self.screen,
                    (255, 0, 0),
                    [
                        200,
                        610,
                        int(
                            (920 / self.boss_data.MAX_HP)
                            * self.boss_data.show_hp
                        )
                        - 2,
                        60,
                    ],
                    border_radius=25,
                )

                self.screen.blit(self.boss_name, (200, 555))

        # remove all the objects that need to be removed from self.objects
        for removing in to_remove:
            self.objects.remove(removing)
            del removing

        # Make sure dead sprites are deleted from memory
        import gc

        gc.collect()
        gc.collect()

        # Collision algorithm
        for obj in self.objects:

            if hasattr(obj, "move_ability"):
                objects = copy(self.objects)  # gets all objects
                objects.remove(
                    obj
                )  # remove the object that we are currently checking for collisions
                objects.append(
                    self.player
                )  # add the player in the object list bc it's still a collider
                for obj_ in objects:
                    if hasattr(obj_, "IDENTITY"):
                        if obj_.IDENTITY == "PROP":
                            if not obj_.collidable or vec(
                                obj.rect.center
                            ).distance_to(obj_.rect.center) > max(
                                obj.rect.size
                            ) + max(
                                obj_.rect.size
                            ):
                                objects.remove(obj_)
                self.collision_system(obj, objects)  # handle collisions

        # handle collisions for the player
        objects = copy(self.objects)
        for obj_ in copy(objects):
            if hasattr(obj_, "IDENTITY"):
                if obj_.IDENTITY == "PROP":
                    if not obj_.collidable or pg.Vector2(
                        self.player.rect.topleft
                    ).distance_to(obj_.rect.center) > max(
                        obj_.rect.size
                    ) + max(
                        self.player.rect.size
                    ):
                        objects.remove(obj_)

        self.collision_system(self.player, objects)

        if self.player.walking and pg.time.get_ticks() - self.step_timer > 250:
            self.player.camera.offset.x += randint(-1, 1)
            self.player.camera.offset.y += randint(-1, 1)
            self.step_timer = pg.time.get_ticks()

        # Light system updating
        self.lights_manager.update(self)

        # MUST BE REWORKED -> supposed to track if the player is interacting with exit rects
        for exit_state, exit_rect in self.exit_rects.items():

            itr_box = p.Rect(
                *(self.player.rect.topleft - pg.Vector2(17, -45)),
                self.player.rect.w // 2,
                self.player.rect.h // 2,
            )

            if exit_state[-1] == "useless":
                break

            if len(exit_rect) == 3 and exit_rect[-1] == "mandatory":
                if itr_box.colliderect(exit_rect[0]):
                    return exit_state

            exit_rect = (
                Rect(exit_rect[0].x, exit_rect[0].y, *exit_rect[0].size),
                exit_rect[1],
            )

            if itr_box.colliderect(exit_rect[0]):
                match self.player.InteractPoint:
                    case 1:
                        # Open UI interaction
                        self.player.is_interacting = True
                        self.player.npc_text = exit_rect[1]
                    case 2:
                        # Send the player to next level
                        self.player.is_interacting = False
                        self.player.npc_text = ""
                        return exit_state
