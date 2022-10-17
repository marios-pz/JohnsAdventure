import random
from typing import Any

from pygame import Rect
import json

from data.scripts.QUESTS import quest, quest_manager

# from .PLAYER.items import Chest
from .PLAYER.player import *
from .PLAYER.inventory import *
from .AI.enemies import *
from .AI import npc
from .utils import resource_path, load, l_path
from .utils import (
    generate_cave_walls,
    generate_chunk,
    generate_hills,
    generate_wall_chunk,
    get_new_road_object,
    build_road,
)

from .props import Chest, Torch
from .PLAYER.items import ManosSword, Training_Sword
from .POSTPROCESSING.light_types import PolygonLight, LightSource
from .POSTPROCESSING.gamestate import GameState
from .sound_manager import SoundManager
from random import randint


def get_cutscene_played(id_: str) -> Any:
    with open(resource_path("data/database/cutscenes.json"), "r") as data:
        return json.load(data)[id_]


def reset_cutscene(id_: str) -> None:
    with open(resource_path("data/database/cutscenes.json"), "r") as data:
        data = json.load(data)
    data[id_] = False
    with open(resource_path("data/database/cutscenes.json"), "w") as data2:
        json.dump(data, data2, indent=2)


def play_cutscene(id_: str) -> None:
    with open(resource_path("data/database/cutscenes.json"), "r") as data:
        data = json.load(data)
    data[id_] = True
    with open(resource_path("data/database/cutscenes.json"), "w") as data2:
        json.dump(data, data2, indent=2)


class PlayerRoom(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "player_room",
            light_state="inside_clear",
        )
        self.objects = [
            Rect(0, 0, 1280, 133),
            Rect(1270, 134, 10, 586),
            Rect(0, 0, 1280, 133),
            Rect(0, 711, 1280, 9),
            npc.Mau((150, 530), (300, 100)),
            Rect(10, 90, 430, 360),
            Rect(5, 500, 72, 214),
            Rect(450, 40, 410, 192),
            Rect(36, 400, 77, 94),
        ]

        self.music_manager = SoundManager(False, True, volume=0.45)
        self.music_manager.play_music("main_theme")

        self.world = pg.transform.scale(
            l_path("data/sprites/world/Johns_room.png"), (1280, 720)
        )
        self.exit_rects = {"kitchen": (Rect(1008, 148, 156, 132), "Go down?")}
        self.spawn = {
            "kitchen": (self.exit_rects["kitchen"][0].bottomleft + vec(0, 50))
        }

        from .scripts import PLAYER_ROOM_SCENE

        self.camera_script = PLAYER_ROOM_SCENE

        self.additional_lights = [
            # Windows
            PolygonLight(
                vec(79 * 3, 9 * 3),
                68 * 3,
                350,
                50,
                85,
                (255, 255, 255),
                dep_alpha=50,
                horizontal=True,
                additional_alpha=175,
            ),
            PolygonLight(
                vec(347 * 3, 9 * 3),
                68 * 3,
                350,
                50,
                85,
                (255, 255, 255),
                dep_alpha=50,
                horizontal=True,
                additional_alpha=175,
            ),
            # John's Computer
            PolygonLight(
                vec(254 * 3 + 1, 26 * 3),
                49 * 3,
                150,
                25,
                125,
                (89, 144, 135),
                dep_alpha=185,
                horizontal=True,
            ),
        ]


class Kitchen(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "kitchen",
            light_state="inside_clear",
        )
        self.world = pg.transform.scale(
            load(resource_path("data/sprites/world/kitchen.png")), (1280, 720)
        )
        self.objects = [
            Rect(-40, 0, 40, 720),
            Rect(0, 0, 1280, 133),
            Rect(1270, 134, 10, 586),
            Rect(0, 0, 1280, 133),
            Rect(0, 711, 1280, 9),
            Rect(20, 250, 250, 350),
            Rect(280, 300, 64, 256),
            Rect(10, 0, 990, 230),
            Rect(1020, 440, 256, 200),
            npc.Cynthia((570, 220)),
        ]
        self.exit_rects = {
            "player_room": (Rect(1054, 68, 138, 119), "Back to your room?"),
            "johns_garden": (Rect(551, 620, 195, 99), "Go outside?"),
        }
        self.spawn = {
            "player_room": (
                self.exit_rects["player_room"][0].bottomleft + vec(75, 0)
            ),
            "johns_garden": (
                self.exit_rects["johns_garden"][0].topleft + vec(0, -200)
            ),
        }
        self.additional_lights = [
            PolygonLight(
                vec(103 * 3, 9 * 3),
                68 * 3,
                350,
                50,
                85,
                (255, 255, 255),
                dep_alpha=80,
                horizontal=True,
                additional_alpha=150,
            ),
        ]

        self.pop_cynthia = False
        self.sound_manager = SoundManager(True, False, volume=1)
        self.ended_script = True
        self.spawned = False
        self.started_script = False

        from .scripts import KITCHEN_SCENE

        self.camera_script = KITCHEN_SCENE

    def update(self, camera, dt):

        # if level in json = false and cutscene not played
        # if not get_cutscene_played(self.id) and not self.started_script:

        if not get_cutscene_played(self.id) and not self.started_script:
            # gets player's current main mission and then sub mission
            if self.player.game_instance.quest_manager.quests[
                "A new beginning"
            ].quest_state["Talk to Cynthia in the kitchen"]:
                self.started_script = True
                self.ended_script = False

        if self.player.game_instance.quest_manager.quests[
            "A new beginning"
        ].quest_state["Talk back to manos"]:
            if not self.pop_cynthia:
                # SHE IS GONE MATE
                self.objects.pop()
                self.pop_cynthia = True  # Save iteration

        return super(Kitchen, self).update(camera, dt)


class JohnsGarden(GameState):
    """Open world state of the game -> includes john's house, mano's hut, and more..."""

    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "johns_garden",
            light_state="day",
        )

        # Get the positions and the sprites' informations from the json files
        with open(resource_path("data/database/open_world_pos.json")) as pos:
            self.positions = json.load(pos)

        with open(resource_path("data/database/open_world.json")) as infos:
            self.sprite_info = json.load(infos)

        get_scale = lambda name: self.sprite_info[name]["sc"]

        self.music_manager = SoundManager(False, True, volume=0.75)
        self.music_manager.play_music("forest_theme")

        # John's house position and size
        jh_pos = self.positions["john_house"][0] - vec(1, 30)
        jh_siz = (
            self.sprite_info["john_house"]["w"] * get_scale("john_house"),
            self.sprite_info["john_house"]["h"] * get_scale("john_house"),
        )
        jh_sc = get_scale("john_house")

        # Mano's hut position and scale
        mano_pos = self.positions["manos_hut"][0]
        mano_sc = get_scale("manos_hut")

        # horizontal road width
        hr_r_width = (
            self.sprite_info["hori_road"]["w"]
            * self.sprite_info["hori_road"]["sc"]
        )
        hhr_r_width = (
            self.sprite_info["hori_road_half"]["w"]
            * self.sprite_info["hori_road_half"]["sc"]
        )
        hr_s_width = (
            self.sprite_info["hori_sides"]["w"]
            * self.sprite_info["hori_sides"]["sc"]
        )
        hr_s_height = (
            self.sprite_info["hori_sides"]["h"]
            * self.sprite_info["hori_sides"]["sc"]
        )
        vr_r_height = (
            self.sprite_info["ver_road"]["h"]
            * self.sprite_info["ver_road"]["sc"]
        )
        hills_height = (
            self.sprite_info["hill_mid"]["h"]
            * self.sprite_info["hill_mid"]["sc"]
        )

        # Use super().load_objects() , when every model is ready
        self.objects = [
            # .prop_objects["box"]((200, 1200)),
            # Fences of john's house (values are calculated for scale = 3 considering this won't change)
            self.prop_objects["hori_fence_rev"](
                ((jh_pos[0] - 150) * jh_sc, (jh_pos[1] + 100) * jh_sc)
            ),
            self.prop_objects["hori_fence"](
                (
                    (jh_pos[0] - 83) * jh_sc + jh_siz[0],
                    (jh_pos[1] + 100) * jh_sc,
                )
            ),
            self.prop_objects["side_fence"](
                ((jh_pos[0] - 150) * jh_sc, (jh_pos[1] + 100) * jh_sc)
            ),
            self.prop_objects["side_fence"](
                (
                    (jh_pos[0] - 83 + 233 - 9) * jh_sc + jh_siz[0],
                    (jh_pos[1] + 100) * jh_sc,
                )
            ),
            self.prop_objects["hori_fence_rev"](
                ((jh_pos[0] - 150) * jh_sc, (jh_pos[1] + 100 + 254) * jh_sc)
            ),
            self.prop_objects["hori_fence"](
                (
                    (jh_pos[0] - 83) * jh_sc + jh_siz[0],
                    (jh_pos[1] + 100 + 254) * jh_sc,
                )
            ),
            # All the objects contained in open_world_pos.json
            *[
                self.prop_objects[object_](
                    (
                        pos[0] * get_scale(object_),
                        pos[1] * get_scale(object_),
                    )
                )
                for object_, pos_ in self.positions.items()
                for pos in pos_
            ],
            self.prop_objects["street_lamp"]((323 * 3 + 900, 888 * 3 + 800)),
            self.prop_objects["street_lamp"]((323 * 3 - 300, 888 * 3 + 800)),
            # Mano's hut custom collisions
            Rect(
                mano_pos[0] * mano_sc,
                (mano_pos[1] + 292) * mano_sc,
                41 * mano_sc,
                35 * mano_sc,
            ),
            Rect(
                (mano_pos[0] + 31) * mano_sc,
                (mano_pos[1] + 292) * mano_sc,
                11 * mano_sc,
                52 * mano_sc,
            ),
            Rect(
                (mano_pos[0] + 240) * mano_sc,
                (mano_pos[1] + 292) * mano_sc,
                11 * mano_sc,
                52 * mano_sc,
            ),
            Rect(
                (mano_pos[0] + 240) * mano_sc,
                (mano_pos[1] + 292) * mano_sc,
                41 * mano_sc,
                35 * mano_sc,
            ),
            Rect(
                (mano_pos[0] + 41) * mano_sc,
                (mano_pos[1] + 324) * mano_sc,
                75 * mano_sc,
                4 * mano_sc,
            ),
            Rect(
                (mano_pos[0] + 165) * mano_sc,
                (mano_pos[1] + 324) * mano_sc,
                75 * mano_sc,
                4 * mano_sc,
            ),
            Rect(
                (mano_pos[0] + 116) * mano_sc,
                (mano_pos[1] + 322) * mano_sc,
                6 * mano_sc,
                20 * mano_sc,
            ),
            Rect(
                (mano_pos[0] + 159) * mano_sc,
                (mano_pos[1] + 322) * mano_sc,
                6 * mano_sc,
                20 * mano_sc,
            ),
            # cave barrier
            Rect((4826, 6054, 130, 500)),
            # Bottom Cave route
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] + 152) * jh_sc,
                    (jh_pos[1] + 2196) * jh_sc,
                ),
                n_road=6,
                type_r="hori_road",
                end_type="hori_road_half",
            ),
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] + 152) * jh_sc,
                    (jh_pos[1] + 399) * jh_sc,
                ),
                n_road=4,
                type_r="hori_road",
                end_type="hori_road_half",
            ),
            # john dirt road
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] + 119) * jh_sc,
                    (jh_pos[1] + 279) * jh_sc,
                ),
                n_road=2,
                start_type="ver_dirt",
                end_type="ver_sides",
            ),
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] + 119) * jh_sc,
                    (jh_pos[1] + 432) * jh_sc,
                ),
                n_road=6,
                start_type="ver_road",
                end_type="Vhori_turn",
            ),
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] - 702) * jh_sc,
                    (jh_pos[1] + 399) * jh_sc,
                ),
                n_road=4,
                type_r="hori_road",
                end_type="hori_road_half",
            ),
            # Out of bounds before Chapter 2 map
            Rect(500, 3600, 100, 10000),
            *generate_chunk(
                self, "tree", 470, 3900, 13, 2, 100 * 3, 100 * 4, randomize=25
            ),
            # Out of bounds bottom of the map
            Rect(500, 9700, 9500, 100),
            Rect(7600, 7400, 100, 2250),
            Rect(7600, 7400, 1100, 100),
            *generate_chunk(
                self, "tree", 1950, 8750, 1, 6, 100 * 6, 0, randomize=5
            ),
            *generate_chunk(
                self, "tree", 1950, 9150, 2, 6, 100 * 6, 75, randomize=45
            ),
            # Manos dirt road
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] - 246) * jh_sc
                    + 4 * hr_r_width
                    + hhr_r_width
                    + hr_s_width,
                    (jh_pos[1] + 361 - 82) * jh_sc,
                ),
                start_type="ver_dirt",
                end_type="ver_sides",
                n_road=2,
            ),
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] - 247) * jh_sc
                    + 4 * hr_r_width
                    + hhr_r_width
                    + hr_s_width * 2,
                    (jh_pos[1] + 361 - 82 + 172 - 49 - 3) * jh_sc,
                ),
                n_road=3,
                type_r="hori_road",
                end_type="Vhori_sides",
            ),
            # Route 4
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] - 247 - 1) * jh_sc
                    + 6 * hr_r_width
                    + hhr_r_width
                    + hr_s_width * 2,
                    (jh_pos[1] + 361 - 82 + 172 - 49 - 3) * jh_sc
                    + hr_s_height,
                ),
                n_road=3,
                type_r="ver_road",
                end_type="Vhori_sides",
            ),
            # Cave Road
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] - 247) * jh_sc
                    + 4 * hr_r_width
                    + hhr_r_width
                    + hr_s_width * 2,
                    (jh_pos[1] + 361 - 82 + 240 - 49 - 3) * jh_sc
                    + hr_s_height
                    + 2 * vr_r_height,
                ),
                n_road=2,
                type_r="hori_road",
            ),
            # Hills above the john's and mano's hut
            *generate_hills(
                self,
                "right",
                (jh_pos[0] * jh_sc - 600, jh_pos[1] * jh_sc - 250),
                8,
                mid_type="hill_mid",
                end_type="none",
            ),
            *generate_hills(
                self,
                "down",
                (
                    jh_pos[0] * jh_sc - 600 + 3 * 224 * 7,
                    jh_pos[1] * jh_sc - hills_height * 7 + 77,
                ),
                7,
                no_begin=True,
                mid_type="hill_side_mid_rev",
                end_type="hill_side_inner_rev",
            ),
            # _____TOP_RIGHT_MAP_______
            # Out of bounds
            Rect(5700, 140 - 150, 5500, 300),
            *generate_chunk(
                self, "tree", 6600, 40, 1, 5, 100 * 5, 240, randomize=25
            ),
            *generate_chunk(
                self, "tree", 5800, 600, 5, 2, 100 * 3, 100 * 4, randomize=25
            ),
            # Collision at the top right of the john's home
            Rect(
                jh_pos[0] * jh_sc + 224 * 5 + 75,
                jh_pos[1] * jh_sc + 200,
                64,
                128,
            ),
            # Trees right from Johns room
            *generate_chunk(
                self,
                "tree",
                jh_pos[0] * jh_sc + 1250,
                jh_pos[1] * jh_sc,
                2,
                2,
                100 * 4,
                100 * 3,
                randomize=10,
            ),
            # Trees right from Manos hut
            *generate_chunk(
                self,
                "tree",
                mano_pos[0] * mano_sc + 950,
                jh_pos[1] * jh_sc,
                2,
                2,
                100 * 4,
                100 * 3,
                randomize=40,
            ),
            # Trees left from Manos hut
            *generate_chunk(
                self,
                "tree",
                mano_pos[0] * mano_sc - 730,
                jh_pos[1] * jh_sc,
                2,
                2,
                100 * 4,
                100 * 3,
                randomize=10,
            ),
            # grass details under those trees
            *generate_chunk(
                self,
                "grass",
                jh_pos[0] * jh_sc + 1340,
                jh_pos[1] * jh_sc + 460,
                3,
                9,
                100 * 2,
                100 * 2,
                randomize=20,
            ),
            # Under manos hut
            *generate_chunk(
                self, "tree", 5850, 3800, 6, 2, 650, 350, randomize=10
            ),
            *generate_chunk(
                self, "tree", 5850, 6500, 6, 2, 650, 350, randomize=10
            ),
            # "_________________ Right place of the map_________________"
            # Big Hill B
            *generate_hills(
                self,
                "right",
                (7200, 720),
                6,
                mid_type="hill_mid",
                end_type="hill_side_outer_rev",
            ),
            *generate_hills(
                self,
                "down",
                (7200, 720),
                10,
                start_type="hill_side_outer",
                mid_type="hill_side_mid",
                end_type="hill_side_outer",
            ),
            *generate_hills(
                self,
                "right",
                (7200, 720 + 140 * 3 * 13 + 102),
                5,
                mid_type="hill_mid",
                end_type="hill_side_inner_rev",
            ),
            # Route 7 -> Top Right
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] - 247 - 1) * jh_sc
                    + 6 * hr_r_width
                    + hhr_r_width
                    + hr_s_width * 2,
                    (jh_pos[1] + 361 - 82 + 172 - 49 - 3) * jh_sc
                    - 3 * vr_r_height,
                ),
                n_road=3,
                type_r="ver_road",
            ),
            # Route 8 -> Top right of map
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] - 247 - 1) * jh_sc
                    + 6 * hr_r_width
                    + hhr_r_width
                    + hr_s_width * 2,
                    (jh_pos[1] + 361 - 82 + 172 - 49 - 3) * jh_sc
                    - 3 * vr_r_height
                    - 33 * 3,
                ),
                n_road=8,
                type_r="hori_road",
                start_type="VHhori_turn",
            ),
            # Route 5 Bottom Right
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] - 247 - 1) * jh_sc
                    + 6 * hr_r_width
                    + hhr_r_width
                    + hr_s_width * 2,
                    (jh_pos[1] + 498 - 3) * jh_sc + hr_s_height * 18,
                ),
                n_road=2,
                type_r="ver_road",
                end_type="Hver_turn",
            ),
            # Road that connect bottom cave route with
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] - 247 - 1) * jh_sc
                    + 6 * hr_r_width
                    + hhr_r_width
                    + hr_s_width * 2,
                    4994,
                ),
                n_road=5,
                type_r="ver_road",
                end_type="VHver_turn",
            ),
            # Route 6 Bottom Right
            *build_road(
                self,
                start_pos=(
                    (jh_pos[0] - 247 - 1) * jh_sc
                    + 6 * hr_r_width
                    + hhr_r_width
                    + hr_s_width * 3,
                    (jh_pos[1] + 361 - 82 + 172 - 50 - 3 - 65) * jh_sc
                    + 2 * hr_s_height
                    + 3 * vr_r_height,
                ),
                n_road=6,
                type_r="hori_road_half",
                end_type="Vver_end",
            ),
            *generate_chunk(
                self, "grass", 7100, 7300, 4, 8, 90, 140, randomize=35
            ),
            # """_________________Cave Borders_________________"""
            # Top
            *generate_hills(
                self,
                "right",
                (jh_pos[0] * jh_sc + 600, jh_pos[1] * jh_sc + 1400),
                6,
                mid_type="hill_mid",
                end_type="hill_side_outer_rev",
            ),
            # Bottom
            *generate_hills(
                self,
                "right",
                (
                    jh_pos[0] * jh_sc + 600,
                    jh_pos[1] * jh_sc + 1400 + 160 * 3 * 9 + 102,
                ),
                6,
                mid_type="hill_mid",
                end_type="hill_side_outer_rev",
            ),
            # Left Border
            *generate_hills(
                self,
                "down",
                (
                    jh_pos[0] * jh_sc + 600,
                    jh_pos[1] * jh_sc + 1400 + 160 * 3 - 102,
                ),
                8,
                no_begin=True,
                mid_type="hill_side_mid",
                end_type="hill_side_outer",
            ),
            # Right up border
            *generate_hills(
                self,
                "down",
                (
                    jh_pos[0] * jh_sc + 600 + 3 * 224 * 5,
                    jh_pos[1] * jh_sc + 1400 + 160 * 3 - 102,
                ),
                4,
                no_begin=True,
                mid_type="hill_side_mid_rev",
                end_type="hill_side_inner_rev",
            ),
            # Right down border
            *generate_hills(
                self,
                "down",
                (
                    jh_pos[0] * jh_sc + 600 + 3 * 224 * 5,
                    jh_pos[1] * jh_sc
                    + 1500
                    + 160 * 3
                    - 102
                    + 4 * hills_height,
                ),
                mid_type="hill_side_mid_rev",
                end_type="hill_side_inner_rev",
                n_hills=4,
                start_type="hill_side_outer_rev",
            ),
        ]

        self.exit_rects = {
            "kitchen": (
                Rect(
                    (jh_pos[0] + 846 - 728) * jh_sc + 3,
                    (jh_pos[1] + 268) * jh_sc,
                    100,
                    60,
                ),
                "Go back to your house?",
            ),
            # mandatory forced level switch, useless requires input
            # exit_rects and spawn must have the same keys else the entire level will crash because it wont be found
            "cave_garden": (Rect(5350, 6130, 200, 380), "", "mandatory"),
            "training_field": (Rect(8700, 6680, 600, 800), "", "mandatory"),
            "gymnasium": (Rect(10500, 200, 300, 600), "", "mandatory"),
            "manos_hut": (
                Rect(
                    (mano_pos[0] + 124) * mano_sc,
                    (mano_pos[1] + 337 - 43 + 12) * mano_sc,
                    100,
                    50,
                ),
                "Enter Mano's hut ?",
            ),
        }
        self.spawn = {
            "kitchen": self.exit_rects["kitchen"][0].bottomleft,
            "cave_garden": self.exit_rects["cave_garden"][0].midright
            + vec(120, -140),
            "training_field": self.exit_rects["training_field"][0].midleft
            - vec(100, 100),
            "gymnasium": vec(10300, 500),
            "manos_hut": self.exit_rects["manos_hut"][0].midbottom,
        }

        self.spawn_mh = False
        self.pop_g_exit = False

    def update(self, camera, dt):
        self.screen.blit(self.green_leaf, (0, 0))

        update = super().update(camera, dt)

        if self.player.game_instance.quest_manager.quests[
            "A new beginning"
        ].quest_state["Ask alexia"]:
            if not self.pop_g_exit:
                self.exit_rects.pop("gymnasium")
                self.spawn.pop("gymnasium")
                self.objects.append(Rect(9000, 100, 600, 1000))
                self.pop_g_exit = True

        return update


class Training_Field(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(Training_Field, self).__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "training_field",
            light_state="day",
        )

        hills_width = self.prop_objects["hill_mid"]((0, 0)).idle[0].get_width()
        hills_height = (
            self.prop_objects["hill_side_mid"]((0, 0)).idle[0].get_width()
        )

        self.music_manager = SoundManager(False, True, volume=0.75)
        self.sound_manager = SoundManager(True, False, volume=0.75)

        self.objects = [
            # *generate_chunk(
            #    "grass", -600, 600, 20, 25, 120, 150, randomize=45
            # ),
            # OUT OF BOUNDS
            Rect(-400, 200, 300, 2600),  # Left
            Rect(2800, 200, 300, 2600),  # Right
            # No need Top, we have the hills
            Rect(-400, 2800, 2600, 300),
            *generate_hills(
                self,
                "right",
                (-700, 0),
                10,
                mid_type="hill_mid",
                end_type="hill_side_outer_rev",
            ),
            *build_road(
                self,
                (-700, hills_height + 50),
                n_road=2,
                start_type="hori_road",
                end_type="Vver_end",
            ),
            self.prop_objects["feevos_shop"]((1100, 800)),
            # ____ TREES ____
            # Up
            *generate_chunk(
                self, "tree", 300, 200, 2, 8, 250, 180, randomize=30
            ),
            # Right
            *generate_chunk(
                self, "tree", 2200, 722, 2, 2, 250, 400, randomize=30
            ),
            # Down
            *generate_chunk(
                self, "tree", 0, 2200, 2, 8, 400, 250, randomize=30
            ),
            # Left
            *generate_chunk(
                self, "tree", -200, 1000, 3, 2, 150, 400, randomize=30
            ),
            npc.Candy((1250, 1470), awake=True),
            npc.Manos((1150, 1480)),
            Chest((1630, 1410), {"items": Training_Sword(), "coins": 50}),
            Dummy(self, (1850, 1534)),
            Dummy(self, (1850, 1734)),
        ]

        self.exit_rects = {
            "johns_garden": (
                Rect(-100, hills_height - 200, 100, 900),
                "Go back to open world ?",
                "mandatory",
            )
        }

        self.spawn = {
            "johns_garden": self.exit_rects["johns_garden"][0].topright
            + vec(100, 280)
        }

        self.ended_script = True
        self.spawned = False
        self.started_script = False
        self.radius_circles = 0
        self.delay_radius = 0
        self.max_radius = 250
        self.shockwave_radius = 100
        self.exploded = False
        self.centers = [(0, 0), (0, 0)]
        self.dummies = []

        from .scripts import TRAINING_FIELD_SCENE_1, TRAINING_FIELD_SCENE_2

        self.script_1 = TRAINING_FIELD_SCENE_1
        self.script_2 = TRAINING_FIELD_SCENE_2

        self.camera_script = self.script_1
        self.cutscene_index = 0
        self.reset_scr = False
        self.killed_enemies = False
        self.played_3 = False

    def update(self, camera, dt) -> None:
        self.screen.blit(self.green_leaf, (0, 0))

        quests = self.player.game_instance.quest_manager.quests[
            "A new beginning"
        ]

        if not self.started_script:

            if quests.quest_state["Talk to manos in the training field"]:
                self.started_script = True
                self.ended_script = False
                self.player.is_interacting = False
                self.player.InteractPoint = 0

            if quests.quest_state["Talk back to manos"]:
                self.started_script = True
                self.ended_script = False
                self.player.is_interacting = False
                self.player.InteractPoint = 0

        # Cutscene 2 script
        if quests.quest_state["Talk back to manos"]:
            if not self.reset_scr:
                reset_cutscene(self.id)
                self.started_script = False
                self.camera_script = self.script_2
                self.reset_scr = True

            if self.started_script and not self.spawned:
                self.spawned = True

                self.dummies = [
                    ShadowDummy(
                        self,
                        (1700, 1540),
                        hp=150,
                        xp_drop=125,
                    ),
                    ShadowDummy(
                        self,
                        (1700, 1720),
                        hp=150,
                        xp_drop=125,
                    ),
                ]
                self.centers = [dummy.rect.center for dummy in self.dummies]
                self.radius_circles += 2
                self.sound_manager.play_sound("magic_shooting")
                self.sound_manager.play_sound("ShadowSummon")

                if self.music_manager.playing_music != "garden_theme":
                    self.music_manager.play_music("garden_theme")

                self.exploded = True

        update = super(Training_Field, self).update(camera, dt)

        if (
            quests.quest_state["Talk back to manos"]
            and self.shockwave_radius < 7000
        ):
            if self.exploded:
                self.shockwave_radius += 100  # vel of shockwave

                pg.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    vec((1000, 1000)) - self.scroll,
                    self.shockwave_radius,
                    width=10,
                )

            if (
                self.spawned
                and self.radius_circles < self.max_radius
                and self.dummies == []
            ):
                if pg.time.get_ticks() - self.delay_radius > 40:
                    self.radius_circles += 15
                    self.player.camera.offset.x += randint(-4, 4)
                    self.player.camera.offset.y += randint(-4, 4)
                    self.delay_radius = pg.time.get_ticks()

                for pos in self.centers:
                    pg.draw.circle(
                        self.screen,
                        (128, 0, 128),
                        vec(pos) - self.scroll,
                        self.radius_circles,
                        4,
                    )
                    pg.draw.circle(
                        self.screen,
                        (255, 255, 255),
                        vec(pos) - self.scroll,
                        self.radius_circles + 4,
                        2,
                    )

            # 884 = the distance between explosion start and first dummy
            if self.shockwave_radius > 884 and self.dummies != []:
                # Fix aura bug before re implementing them
                self.objects.extend(self.dummies)
                self.dummies = []

        return update


class Gymnasium(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(Gymnasium, self).__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "gymnasium",
            light_state="day",
        )
        hills_width = self.prop_objects["hill_mid"]((0, 0)).idle[0].get_width()
        hills_height = (
            self.prop_objects["hill_side_mid"]((0, 0)).idle[0].get_width()
        )
        center_spawn = 200

        self.objects = [
            *generate_chunk(
                self,
                "tree",
                hills_width // 2 + 20,
                -hills_height * 3 + 270,
                4,
                2,
                400,
                320,
                randomize=45,
            ),
            # Right side trees
            *generate_chunk(
                self,
                "tree",
                hills_width * 6,
                -hills_height * 3 + 270,
                4,
                2,
                450,
                320,
                randomize=45,
            ),
            *generate_hills(
                self,
                "right",
                (-400, center_spawn),
                10,
                mid_type="hill_mid",
                end_type="hill_side_outer_rev",
            ),
            *build_road(
                self,
                start_pos=(-600, 40),
                n_road=2,
                start_type="hori_road",
                end_type="Vver_end",
            ),
            *build_road(
                self,
                start_pos=(350, 40),
                n_road=2,
                start_type="hori_road",
                end_type="Vver_end",
            ),
            *build_road(
                self,
                start_pos=(1320, 40),
                n_road=2,
                start_type="hori_road",
                end_type="Vver_end",
            ),
            # ___OUT_OF_BOUNDS
            Rect(5160, -900, 50, 2100),  # Right
            Rect(40, -900, 50, 2100),  # Left
            Rect(40, -900, hills_width * 8, 50),  # Up
            self.prop_objects["school_entrance"](
                (hills_width * 2 - 150, -hills_height * 2 + 30)
            ),
            npc.Alex((2702, -75)),
            npc.CynthiaSchool((2782, -75)),
        ]

        self.exit_rects = {
            "johns_garden": (
                Rect(-100, -center_spawn - 121, 300, 600),
                "Go back to open world ?",
                "mandatory",
            ),
        }

        self.spawn = {"johns_garden": (500, 0), "cave_passage": (4790, -150)}

        self.cave_stuff = generate_chunk(
            self,
            "h_ladder",
            x=4970,
            y=-200,
            row=1,
            col=1,
            step_x=0,
            step_y=0,
            randomize=0,
        )

        self.sound_manager = SoundManager(True, False, volume=1)
        self.ended_script = True
        self.spawned = False
        self.started_script = False

        from .scripts import GYMNASIUM_SCENE

        self.camera_script = GYMNASIUM_SCENE

        self.cyn_gone = False

    def update(self, camera, dt):
        self.screen.blit(self.green_leaf, (0, 0))

        if (
            self.player.game_instance.quest_manager.quests[
                "A new beginning"
            ].quest_state["Go find Cynthia in school"]
            and not self.cyn_gone
        ):
            self.objects.pop()  # pop cynthia
            self.spawn.pop("johns_garden")
            self.objects.append(Rect(-200, -200 - 121, 500, 600))
            self.cyn_gone = True

        if not get_cutscene_played(self.id) and not self.started_script:
            # gets player's current main mission and then sub mission
            if self.player.game_instance.quest_manager.quests[
                "A new beginning"
            ].quest_state["Ask alexia"]:
                self.started_script = True
                self.ended_script = False
                self.objects.extend(self.cave_stuff)
                self.exit_rects["cave_passage"] = (
                    Rect(4970, -200, 64, 64),
                    "Are you sure you want to get in ?",
                )

        return super(Gymnasium, self).update(camera, dt)


class ManosHut(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super().__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "manos_hut",
            light_state="inside_dark",
        )
        self.world = pg.transform.scale(
            l_path("data/sprites/world/manos_hut.png"), (1280, 720)
        )
        sc_x = 1280 / 453
        sc_y = 720 / 271
        self.objects = [
            Rect(-40, 0, 40, 720),  # Left borders
            Rect(1270, 134, 40, 586),  # Right borders
            Rect(0, 4 - 0, 1280, 133 + 40),  # Up borders
            Rect(0, 711, 1280, 40),  # Down borders
            self.prop_objects["m_hut_bed"]((381 * sc_x, 47 * sc_y)),
            self.prop_objects["m_hut_sofa"]((97 * sc_x, 88 * sc_y)),
            self.prop_objects["m_hut_table"]((163 * sc_x, 37 * sc_y)),
            self.prop_objects["m_hut_fireplace"](
                (5 * sc_x, (193 - 236) * sc_y)
            ),
        ]

        self.spawn = {"johns_garden": (630, 490)}

        self.exit_rects = {
            "johns_garden": (
                Rect(560, 635, 150, 75),
                "Go back to open world ?",
            )
        }

        self.spawn_npcs = False

        self.ended_script = True
        self.spawned = False
        self.started_script = False
        self.camera_script = [
            {
                "duration": 4000,
                "pos": (235 * sc_x, 115 * sc_y),
                "zoom": 1.2,
                "text": "Manos: John! did you find your sister?",
                "text_dt": 1500,
            },
            {
                "duration": 4000,
                "text": "John: I was too late. We gotta get her back!",
                "text_dt": 1500,
            },
            {
                "duration": 4000,
                "text": "John: What did you want to explain to me before?",
                "text_dt": 1500,
            },
            {
                "duration": 4000,
                "text": "Manos: I think I know who did it John.",
                "text_dt": 1500,
            },
            {
                "duration": 4000,
                "text": "Manos: This aura is no one else's but my old nemesis Alcemenos",
                "text_dt": 1500,
            },
            {
                "duration": 4000,
                "text": "Manos: There is a good chance he is using his old base.",
                "text_dt": 1500,
            },
            {
                "duration": 4000,
                "zoom": 1,
                "text": "Manos: We must go to Porto Rafth before the sun goes down.",
                "text_dt": 1500,
            },
        ]

    def update(self, camera, dt):

        if self.player.game_instance.quest_manager.quests[
            "A new beginning"
        ].quest_state["Kill the big dummie"]:
            if not self.spawn_npcs:
                sc_x = 1280 / 453
                sc_y = 720 / 271

                self.objects.extend(
                    [
                        npc.Manos((235 * sc_x, 115 * sc_y), (300, 100)),
                        npc.Candy((205, 395)),
                        Chest(
                            (422 * sc_x, 47 * 4 * sc_y - 45),
                            {"items": ManosSword(), "coins": 30},
                        ),
                    ]
                )

                self.spawn_npcs = True

        if self.player.game_instance.quest_manager.quests[
            "A new beginning"
        ].quest_state["Reach Manos in his hut"]:
            if not get_cutscene_played(self.id) and not self.started_script:
                self.started_script = True
                self.ended_script = False

        return super(ManosHut, self).update(camera, dt)


class CaveGarden(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(CaveGarden, self).__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "cave_garden",
            light_state="day",
            has_boss=True,
        )
        hills_width = self.prop_objects["hill_mid"]((0, 0)).idle[0].get_width()
        hills_height = (
            self.prop_objects["hill_side_mid"]((0, 0)).idle[0].get_width()
        )

        self.hh = hills_height
        self.ww = hills_width

        self.objects = [
            *generate_chunk(
                self,
                "cave_spike",
                2060,
                160 * 17 + 30,
                1,
                3,
                150,
                0,
                randomize=10,
            ),
            *generate_chunk(
                self,
                "cave_spike_small",
                2150,
                160 * 17 + 80,
                1,
                3,
                150,
                0,
                randomize=10,
            ),
            *generate_chunk(
                self,
                "cave_spike",
                2080,
                160 * 17 + 220,
                1,
                3,
                150,
                0,
                randomize=10,
            ),
            *generate_chunk(
                self,
                "cave_spike_small",
                2150,
                160 * 17 + 220 + 30,
                1,
                3,
                150,
                0,
                randomize=10,
            ),
            # """_________________Cave Borders_________________"""
            # Top
            *generate_hills(
                self,
                "right",
                (0, 160 * 3 * 2),
                6,
                mid_type="hill_mid",
                end_type="hill_side_outer_rev",
            ),
            # Bottom
            *generate_hills(
                self,
                "right",
                (0, 160 * 3 * 9 + 102),
                6,
                mid_type="hill_mid",
                end_type="hill_side_outer_rev",
            ),
            # Left Border
            *generate_hills(
                self,
                "down",
                (0, 160 * 3 - 102),
                8,
                no_begin=True,
                mid_type="hill_side_mid",
                end_type="hill_side_outer",
            ),
            # Right up border
            *generate_hills(
                self,
                "down",
                (0 + 3 * 224 * 5, 160 * 3 - 102),
                5,
                no_begin=True,
                mid_type="hill_side_mid_rev",
                end_type="hill_side_inner_rev",
            ),
            # Right down border
            *generate_hills(
                self,
                "down",
                (0 + 3 * 224 * 5, 160 * 3 - 102 + 4 * hills_height),
                mid_type="hill_side_mid_rev",
                end_type="hill_side_inner_rev",
                n_hills=5,
                start_type="hill_side_outer_rev",
            ),
            self.prop_objects["cave_entrance"](
                (hills_width + 100, hills_height * 4 - 255)
            ),
            *generate_chunk(
                self,
                "tree",
                hills_width * 3 - 50,
                hills_height * 2 - 50,
                4,
                2,
                100 * 5,
                100 * 3,
            ),
            *generate_chunk(
                self,
                "tree",
                hills_width,
                hills_height * 2 - 50,
                2,
                2,
                100 * 4,
                100 * 3,
            ),
            *generate_chunk(
                self, "tree", hills_width + 10, 3350, 2, 2, 200, 200
            ),
            *generate_chunk(self, "tree", 2100, 2970, 2, 1, 100 * 4, 100),
        ]

        self.spawn = {
            "johns_garden": (hills_width * 5 - 100, hills_height * 4 + 100),
            "cave_entrance": (2150, 2830),
        }

        self.exit_rects = {
            "johns_garden": (
                Rect(hills_width * 5 + 50, hills_height * 4, 200, 400),
                "",
                "mandatory",
            ),
            # Cave has been removed to avoid more complex code.
            # it will be returned once john has defeated the boss
        }

        self.ended_script = True
        self.spawned = False
        self.started_script = False

        self.camera_script = [
            {
                "duration": 4000,
                "pos": (2080, 2800),
                "text": "John: well that was.. dangerous.",
                "text_dt": 1500,
            },
            {
                "duration": 4000,
                "pos": (2080, 2800),
                "text": "John: Mmmm? what is that?",
                "text_dt": 1500,
            },
            {
                "duration": 3000,
                "pos": (2900, 2800),  # enemy position
                "zoom": 1.2,
            },
            {
                "duration": 4200,
                # Go back to the player
                "zoom": 1,
                "zoom_duration": 1800,
                "text": "John: Oh no!",
                "text_dt": 1500,
                "pos": (
                    2080,
                    2800,
                ),  # I assume I have to return the camera somewhere near the player?
            },
        ]

        self.spawn_b = False
        self.killed_b = False

    def update(self, camera, dt):
        self.screen.blit(self.green_leaf, (0, 0))

        # Spawn the big dummie and then play the cutscene
        if (
            self.player.game_instance.quest_manager.quests[
                "A new beginning"
            ].quest_state["Reach the main entrance"]
            and not self.spawn_b
        ):
            # Just for security
            if not self.player.game_instance.quest_manager.quests[
                "A new beginning"
            ].quest_state["Reach Manos in his hut"]:

                self.objects.append(
                    BigShadowDummy(
                        self,
                        (3000, self.hh * 4 + 10),
                    )
                )

                # Kill exits
                self.spawn = {}
                self.exit_rects = {}

                # Play cutscene
                if (
                    not get_cutscene_played(self.id)
                    and not self.started_script
                ):
                    self.started_script = True
                    self.ended_script = False

                # self.objects.append(
                #    Rect(self.ww * 5 + 200, self.hh * 4, 200, 400)
                # )

                self.spawn_b = True

        if (
            self.player.game_instance.quest_manager.quests[
                "A new beginning"
            ].quest_state["Kill the big dummie"]
            and not self.killed_b
        ):
            self.spawn = {
                "johns_garden": (self.ww * 5 - 100, self.hh * 4 + 100),
                "cave_entrance": (2150, 2830),
            }

            self.exit_rects = {
                "johns_garden": (
                    Rect(self.ww * 5 + 50, self.hh * 4, 200, 400),
                    "",
                    "mandatory",
                ),
                "cave_entrance": (
                    Rect(self.ww * 3, self.hh * 4 + 177, 100, 100),
                    "Get inside the cave ?",
                ),
            }

            self.killed_b = True

        return super(CaveGarden, self).update(camera, dt)


class CaveEntrance(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(CaveEntrance, self).__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "cave_entrance",
            light_state="inside_dark",
        )

        self.spawn = {
            "cave_entrance": (
                self.prop_objects["hill_mid"]((0, 0)).idle[0].get_width() * 3
                + 50,
                self.prop_objects["hill_side_mid"]((0, 0)).idle[0].get_width()
                * 4
                + 100,
            ),
            "cave_garden": (1300, 100),
            "cave_room_1": (-2400, 120),
        }

        self.objects = [
            *generate_cave_walls(
                self,
                direction="right",
                dep_pos=self.spawn["cave_garden"]
                - vec(1350 * 4, self.spawn["cave_garden"][1] * 2),
                n_walls=14,
                start_type="c_wall_corner",
                end_type="c_flipped_corner",
            ),
            *generate_cave_walls(
                self,
                direction="right",
                dep_pos=self.spawn["cave_garden"]
                - vec(1350 * 4, -self.spawn["cave_garden"][1] * 2),
                n_walls=14,
                start_type="c_wall_corner_turn",
                end_type="c_flipped_corner",
            ),
            # Since cave exit is optional, I need to add a bound
            Rect(1400 + 140, self.spawn["cave_garden"][1], 150, 300),
            Rect(-(2700 + 140), self.spawn["cave_garden"][1], 150, 300),
            Goblin(
                self,
                (-1400, self.spawn["cave_garden"][1] + 10),
            ),
            Goblin(
                self,
                (-1300, self.spawn["cave_garden"][1] + 20),
            ),
            Torch(
                self,
                tuple(vec(self.spawn["cave_garden"]) - vec(100, 80)),
                radius=80,
            ),
            Torch(
                self,
                tuple(vec(self.spawn["cave_garden"]) - vec(1100, 80)),
                radius=80,
            ),
            Torch(
                self,
                tuple(vec(self.spawn["cave_garden"]) - vec(2100, 80)),
                radius=80,
            ),
            Torch(
                self,
                tuple(vec(self.spawn["cave_garden"]) - vec(3100, 80)),
                radius=80,
            ),
        ]

        self.exit_rects = {
            "cave_garden": (
                Rect(1400, self.spawn["cave_garden"][1], 150, 300),
                "Go back to open world ?",
            ),
            "cave_room_1": (
                Rect(-2700, self.spawn["cave_garden"][1], 150, 300),
                "",
                "mandatory",
            ),
        }

        self.additional_lights = [
            PolygonLight(
                vec(2150, self.spawn["cave_garden"][1] + 95),
                68 * 3,  # height
                400,  # radius
                -15,  # dep_angle
                110,  # end_angle
                (255, 255, 255),  # color
                dep_alpha=70,
                horizontal=False,
                additional_alpha=175,
                rotated=True,
            )
        ]

    def update(self, camera, dt) -> None:
        # Background
        pg.draw.rect(
            self.screen, (23, 22, 22), [0, 0, *self.screen.get_size()]
        )

        # Top void
        pg.draw.rect(
            self.screen,
            (0, 0, 0),
            [*(vec(-3200, -335) - vec(self.scroll)), 5350, 400],
        )

        # Bottom and left void (it would be best if we could blit it after the cave objects)
        pg.draw.rect(
            self.screen,
            (0, 0, 0),
            [*(vec(-3200, 335) - vec(self.scroll)), 5350, 400],
        )

        return super(CaveEntrance, self).update(camera, dt)


class CaveRoomPassage(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(CaveRoomPassage, self).__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "cave_passage",
            light_state="inside_dark",
        )

        self.spawn = {"cave_room_2": (880, 2100), "gymnasium": (783, 730)}

        w = self.prop_objects["c_wall_mid"]((0, 0)).idle[0].get_width()

        self.objects = [
            *generate_cave_walls(
                self,
                direction="right",
                dep_pos=(300, 300),
                n_walls=2,
                start_type="c_wall_corner_turn",
                end_type="c_flipped_corner_turn",
            ),
            *generate_cave_walls(
                self,
                direction="down",
                dep_pos=(300, 300),
                n_walls=8,
                no_begin=True,
                start_type="none",
                end_type="none",
            ),
            *generate_cave_walls(
                self,
                direction="down",
                dep_pos=(800 + 150 + 300 - 32, 300),
                n_walls=8,
                no_begin=True,
                start_type="none",
                end_type="none",
            ),
            *generate_cave_walls(
                self,
                direction="right",
                dep_pos=(300, (w * 6) + 1),
                n_walls=2,
                start_type="c_wall_corner",
                end_type="c_flipped_corner",
            ),
            *generate_chunk(
                self,
                "ladder",
                x=770,
                y=300,
                row=1,
                col=1,
                step_x=0,
                step_y=0,
                randomize=0,
            ),
            Goblin(self, (440, 920)),
            Goblin(self, (490, 920)),
            Goblin(self, (940, 920)),
            Goblin(self, (970, 920)),
        ]

        self.exit_rects = {
            "gymnasium": (
                Rect(732, 530, 150, 140),
                "Are you sure you want to exit the cave ?",
            ),
            "cave_room_2": (
                Rect(300, self.spawn["cave_room_2"][1] + 420, 950, 140),
                "",
                "mandatory",
            ),
        }

        self.additional_lights = [
            PolygonLight(
                vec(800, 300),
                68 * 3,  # height
                350,  # radius
                50,  # dep_angle
                85,  # end_angle
                (255, 255, 255),  # color
                dep_alpha=50,
                horizontal=True,
                additional_alpha=175,
            )
        ]

    def update(self, camera, dt) -> None:
        # Background
        pg.draw.rect(
            self.screen, (23, 22, 22), [0, 0, *self.screen.get_size()]
        )

        # Flashlight
        pg.draw.circle(
            self.screen,
            (240, 240, 240, 30),
            (
                self.screen.get_width() // 2 + 20,
                self.screen.get_height() // 2 + 92,
            ),
            70,
        )

        pg.draw.rect(
            self.screen,
            (0, 0, 0),
            [*(vec(-294, -335) - vec(self.scroll)), 600, 4000],
        )

        pg.draw.rect(
            self.screen,
            (0, 0, 0),
            [*(vec(1244, -335) - vec(self.scroll)), 600, 4000],
        )

        return super(CaveRoomPassage, self).update(camera, dt)


class Credits(GameState):
    def __init__(self, DISPLAY: pg.Surface, player_instance, prop_objects):
        super(Credits, self).__init__(
            DISPLAY,
            player_instance,
            prop_objects,
            "credits",
            light_state="inside_clear",
        )
        self.sound_manager = SoundManager(True, False, volume=1)
        self.sound_manager.play_music("credits_theme")
        self.font = pg.font.Font(
            resource_path("data/database/menu-font.ttf"), 24
        )

        self.credits = [
            "--- Programming ---",
            "Marios Papazogloy | Theophile Aumont",
            " ",
            "--- Art ---",
            "Marios Papazogloy",
            " ",
            "--- Story Telling ---",
            "Manos Danezis",
            " ",
            "--- Music ---",
            "Thanos Pallis",
            " ",
            "Thank you for playing!",
        ]

        self.pos = 0
        self.dy = 50

        self.sound_manager = SoundManager(False, True, volume=0.75)

    def update(self, camera, dt) -> None:
        if self.sound_manager.playing_music != "credits":
            self.sound_manager.play_music("credits")

        pg.draw.rect(self.screen, (0, 0, 0), [0, 0, *self.screen.get_size()])

        self.pos -= dt * 32

        for idx, text in enumerate(self.credits):
            text_rendered = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(
                text_rendered,
                text_rendered.get_rect(
                    center=(
                        self.screen.get_width() // 2,
                        250
                        + self.screen.get_height() // 2
                        + idx * self.dy
                        + self.pos,
                    )
                ),
            )

        return super(Credits, self).update(camera, dt)
