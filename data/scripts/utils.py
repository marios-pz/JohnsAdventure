"""
 Credits @Marios325346

 Functions to reduce typing :rofl:

"""
import json
import os
import pathlib
from typing import Any
import pygame
import sys

from functools import lru_cache
from random import gauss


def init_pause(w: int, h: int, display: pygame.surface.Surface) -> None:
    surf = pygame.Surface((w, h))
    surf.fill((0, 0, 0))
    surf.set_alpha(200)
    display.blit(surf, (0, 0))


# This class must be purged, useless class
class UI_Spritesheet:
    def __init__(self, filename: str) -> None:
        self.sprite_sheet = pygame.image.load(
            resource_path(filename)
        ).convert()
        with open(resource_path("data/database/ui.json")) as f:
            self.data = json.load(f)

    def get_sprite(self, x: int, y: int, w: int, h: int) -> pygame.Surface:
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((255, 255, 255))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, w, h))
        return sprite

    def parse_sprite(self, name: str):
        sprite = self.data["frames"][name]["frame"]
        return self.get_sprite(
            sprite["x"], sprite["y"], sprite["w"], sprite["h"]
        )


def load_sheet(sheet, coo, flip=False):

    """Load an animation sequence (of sprites) on a sprites,
    you obviously have to pass the coordinates of the sprites."""

    x, y, width, height = coo[:4]
    if coo[-1] != 0:  # check for scale
        if not flip:
            return [
                scale(
                    get_sprite(sheet, x + width * i, y, width, height),
                    coo[-1],
                )
                for i in range(coo[-2])
            ]
        else:
            return [
                flip_vertical(
                    scale(
                        get_sprite(sheet, x + width * i, y, width, height),
                        coo[-1],
                    )
                )
                for i in range(coo[-2])
            ]
    else:
        if not flip:
            return [
                get_sprite(sheet, x + width * i, y, width, height)
                for i in range(coo[-2])
            ]
        else:
            return [
                flip_vertical(
                    get_sprite(sheet, x + width * i, y, width, height)
                )
                for i in range(coo[-2])
            ]


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path: Any = sys._MEIPASS
    except AttributeError:
        base_path: str = os.path.abspath(".")

    return os.path.join(base_path, str(pathlib.Path(relative_path)))


@lru_cache(1000)
def l_path(relative_path: str, alpha: bool = False) -> pygame.surface.Surface:
    """Upgraded load function for PyInstaller"""
    if alpha:
        return pygame.image.load(resource_path(relative_path)).convert_alpha()
    return pygame.image.load(resource_path(relative_path)).convert()


@lru_cache(1000)
def load(path: str, alpha: bool = False):
    if alpha:
        return pygame.image.load(path).convert_alpha()
    return pygame.image.load(path).convert()


@lru_cache(1000)
def scale(img: pygame.Surface, n: int):
    return pygame.transform.scale(
        img, (img.get_width() * n, img.get_height() * n)
    )


@lru_cache(1000)
def smooth_scale(img: pygame.Surface, n: float):
    return pygame.transform.smoothscale(
        img, (img.get_width() * n, img.get_height() * n)
    )


@lru_cache(1000)
def double_size(img: pygame.Surface):
    return pygame.transform.scale(
        img, (img.get_width() * 2, img.get_height() * 2)
    )


@lru_cache(1000)
def flip_vertical(img: pygame.Surface):
    return pygame.transform.flip(img, True, False)


@lru_cache(1000)
def flip_horizontal(img: pygame.Surface):
    return pygame.transform.flip(img, False, True)


@lru_cache(1000)
def get_sprite(
    spritesheet: pygame.Surface, x: int, y: int, w: int, h: int
) -> pygame.surface.Surface:

    rect = pygame.Rect(
        x,
        y,
        w
        if x + w <= (W := spritesheet.get_width())
        else abs(W - x),  # adapt size if sprite goes out of the
        h
        if y + h <= (H := spritesheet.get_height())
        else abs(H - y),  # sheet.
    )
    result = (
        pygame.Surface((w, h))
        if x >= W or y >= H
        else spritesheet.subsurface(rect).convert()
    )
    result.set_colorkey((255, 255, 255))

    return result


"""These are now generation methods, to generate procedurally roads, hills and every other type of object
that is in open_world.json"""


def build_road(
    game_state: Any,
    start_pos: tuple[int, int],
    n_road: int,
    type_r: str = "",
    start_type: str = "",
    end_type: str = "",
    types: list = [],
):
    """Function to procedurally generate roads
    Parameters
    ----------
    start_pos : tuple[int, int]
                The position of the first road.
    n_road : int
             The number of roads.
    type_r : str
             The type of the roads generated (except end and start)
    start_type : str
                 *Optional* The type of the road first generated
    end_type : str
               *Optional* The type of the last generated road
    types : list
            *Optional* The generation will follow the list of types
    """

    roads = []  # list to store all the generated roads
    current_pos = list(
        start_pos
    )  # first pos, will be incremented according to the added roads
    default = type_r if type_r != "" else "ver_road"
    if not types:  # if types is empty
        for i in range(n_road):
            if end_type != "" and i == n_road - 1:
                road = end_type
            elif start_type != "" and i == 0:
                road = start_type
            else:
                road = default
            new_road = get_new_road_object(game_state, road, current_pos)
            roads.append(new_road)
            if "hori" in road:
                current_pos[0] += new_road.current_frame.get_width()
            else:
                current_pos[1] += new_road.current_frame.get_height()
    else:
        for index, road in enumerate(types):
            new_road = get_new_road_object(game_state, road, current_pos)
            if "hori" in road:
                current_pos[0] += new_road.current_frame.get_width()
            else:
                current_pos[1] += new_road.current_frame.get_height()
            roads.append(new_road)
    return roads


def generate_chunk(
    game_state: Any,
    type_: str,
    x: int,
    y: int,
    row: int,
    col: int,
    step_x: int,
    step_y: int,
    randomize: int = 20,
):

    """Generates a grid of objects, and randomize the positions a little, in order it not to look too much
    grid-ish, and more realistic.
    Parameters
    ----------
    type_ : str
            The type of object that will be generated.
    x : int
        x position of the beginning of the grid.
    y : int
        y position of the beginning of the grid.
    row : int
          Number of rows.
    col : int
          Number of columns.
    step_x : int
             Width separating each generated object.
    step_y : int
             Height separating each generated object.
    randomize : int
                *Optional* Using gaussian repartition, randomize is moving randomly each objects in the grid, in
                order to make the generation more realistic and less strict.
    """

    return [
        game_state.prop_objects[type_](
            (
                x + c * step_x + int(gauss(0, randomize)),
                y + r * step_y + int(gauss(0, randomize)),
            )
        )
        for c in range(col)
        for r in range(row)
    ]


def generate_hills(
    game_state: Any,
    direction: str,
    dep_pos: tuple[int, int],
    n_hills: int,
    mid_type: str = "left",
    end_type: str = "hill_side_inner",
    no_begin: bool = False,
    start_type: str = "none",
):
    """Generate hills procedurally.
    Parameters
    ----------
    direction : str
                Direction of the hill -> "down" to go down vertically, "right" to go right horizontally.
    dep_pos : tuple[int, int]
              Basic position of the hill, the position of the first hill part.
    n_hills : int
              The number of hills (counting the corners).
    mid_type : str
               The type of the middle hills (the ones between the two ends).
    end_type : str
               The type of the last hill.
    no_begin : bool
               Begins directly the hill by a middle.
    start_type : str
                 Type of first hill
    """

    corner_left = "hill_side_outer"
    corner_right = "hill_side_outer_rev"
    hill_middle = "hill_mid"
    hill_middle_down = "hill_mid" if mid_type == "left" else mid_type
    # dictionary containing all the sizes
    sizes = {
        corner_left: game_state.prop_objects[corner_left](
            (0, 0)
        ).current_frame.get_size(),
        corner_right: game_state.prop_objects[corner_right](
            (0, 0)
        ).current_frame.get_size(),
        hill_middle: game_state.prop_objects[hill_middle](
            (0, 0)
        ).current_frame.get_size(),
        hill_middle_down: game_state.prop_objects[hill_middle_down](
            (0, 0)
        ).current_frame.get_size(),
    }

    # first pos of the first hill, will be incremented
    current_pos = list(dep_pos)
    hills = []  # list that contains all the generated hills

    if not no_begin and start_type == "none":
        if direction == "right" or direction == "up" or direction == "down":
            hills.append(game_state.prop_objects[corner_left](dep_pos))
        else:
            hills.append(game_state.prop_objects[corner_right](dep_pos))

        # according to the direction, increment the position for the next hill according to the size of the
        # hill currently being added
        match direction:
            case "right":
                current_pos[0] += sizes[corner_left][0]
            case "down":
                current_pos[1] += sizes[corner_left][1]
                current_pos[1] -= 102
    elif not no_begin and start_type != "none":
        hills.append(game_state.prop_objects[start_type](dep_pos))
        match direction:
            case "right":
                current_pos[0] += sizes[start_type][0]
            case "down":
                current_pos[1] += sizes[start_type][1]
                current_pos[1] -= 102

    # n_hills - 2 because the ending and starting hills are generated outside the loop
    for i in range(n_hills - 2):
        new_hill = None
        # according to the direction, increment the position for the next hill according to the size of the
        # hill currently being added
        match direction:
            case "right":
                new_hill = game_state.prop_objects[hill_middle](current_pos)
                current_pos[0] += sizes[hill_middle][0]
            case "down":
                new_hill = game_state.prop_objects[hill_middle_down](
                    current_pos
                )
                current_pos[1] += sizes[hill_middle_down][1]

                # "cancel" the gap that the sprites are applying (can't take the height of the sprite without
                # generating a graphical gap
                current_pos[1] -= 51
            case _:
                pass
        if new_hill is not None:
            # appends the generated hill to the list
            hills.append(new_hill)

    # add the last hill
    if end_type != "none":
        hills.append(game_state.prop_objects[end_type](current_pos))

    return hills


def get_new_road_object(game_state, name, pos):
    direction = "H" if "hori" in name else "V"  # get the direction
    flip = {
        "H": "H" in name,
        "V": "V" in name,
    }  # determine the axis to flip
    if flip["V"] and flip["H"]:
        name = name[2:]  # removing the useless letters to avoid KeyError
    elif flip["V"] and not flip["H"] or flip["H"] and not flip["V"]:
        name = name[1:]  # removing the useless letters to avoid KeyError
    road_obj = game_state.prop_objects[name](pos)  # get the object

    # apply the flip
    if flip["H"]:
        road_obj.idle[0] = flip_horizontal(road_obj.idle[0])
    if flip["V"]:
        road_obj.idle[0] = flip_vertical(road_obj.idle[0])

    return road_obj


def generate_cave_walls(
    game_state: Any,
    direction: str,
    dep_pos: tuple[int, int],
    n_walls: int,
    no_begin: bool = False,
    start_type: str = "none",
    end_type: str = "none",
    door_n: int | None = None,
) -> list:
    """Cave Walls (cave_walls) Title : tag
    "c_wall_mid":
    "c_wall_corner"
    "c_wall_corner_turn":
    "c_wall_side":
    "c_flipped_corner":
    "c_flipped_corner_turn":

    same as the above with slight changes
    """

    c_wall_mid = "c_wall_mid"
    c_wall_corner = "c_wall_corner"
    c_wall_corner_turn = "c_wall_corner_turn"
    c_wall_side = "c_wall_side"
    c_flipped_corner = "c_flipped_corner"
    c_flipped_corner_turn = "c_flipped_corner_turn"

    sizes = {
        c_wall_mid: game_state.prop_objects[c_wall_mid](
            (0, 0)
        ).current_frame.get_size(),
        c_wall_corner: game_state.prop_objects[c_wall_corner](
            (0, 0)
        ).current_frame.get_size(),
        c_wall_corner_turn: game_state.prop_objects[c_wall_corner_turn](
            (0, 0)
        ).current_frame.get_size(),
        c_wall_side: game_state.prop_objects[c_wall_side](
            (0, 0)
        ).current_frame.get_size(),
        c_flipped_corner: game_state.prop_objects[c_flipped_corner](
            (0, 0)
        ).current_frame.get_size(),
        c_flipped_corner_turn: game_state.prop_objects[c_flipped_corner_turn](
            (0, 0)
        ).current_frame.get_size(),
    }

    # first pos of the first hill, will be incremented
    current_pos = list(dep_pos)
    walls = []  # list that contains all the generated hills

    if start_type == "none" and no_begin:
        # according to the direction, increment the position for the next hill according to the size of the
        # hill currently being added
        # walls += game_state.prop_objects[c_wall_corner](dep_pos) if direction in ['right', 'up', 'down'] \
        # else game_state.prop_objects[c_flipped_corner](dep_pos)
        match direction:
            case "right":
                current_pos[0] += sizes[c_wall_corner][0]
            case "down":
                current_pos[1] += sizes[c_wall_corner][1]
                current_pos[1] -= 102
    else:
        walls.append(game_state.prop_objects[start_type](dep_pos))
        match direction:
            case "right":
                current_pos[0] += sizes[start_type][0]
            case "down":
                current_pos[1] += sizes[start_type][1]
                current_pos[1] -= 102

    # n_hills - 2 because the ending and starting hills are generated outside the loop
    for i in range(n_walls - 2):
        new_wall = None
        # according to the direction, increment the position for the next hill according to the size of the
        # hill currently being added
        match direction:
            case "right":
                new_wall = game_state.prop_objects[c_wall_mid](current_pos)
                current_pos[0] += sizes[c_wall_mid][0]
            case "down":
                new_wall = game_state.prop_objects[c_wall_side](current_pos)
                current_pos[1] += sizes[c_wall_side][1]
                # "cancel" the gap that the sprites are applying (can't take the height of the sprite without
                # generating a graphical gap
                current_pos[1] -= 51

        if new_wall is not None:
            if type(door_n) is list:
                if i not in door_n:
                    walls.append(new_wall)
            else:
                if door_n != i:
                    walls.append(new_wall)

    # add the last wall (this has a logic flaw, I will fix it later)
    if end_type != "none":
        walls.append(game_state.prop_objects[end_type](current_pos))

    return walls


def generate_wall_chunk(
    game_state,
    n=0,  # N chunks of walls
    x_side=0,  # in case you want N*N+X rather than N*N
    y_side=0,
    pos=(0, 0),
    left_side=True,
    right_side=True,
    up_side=True,
    down_side=True,
    u_n=None,  # up gate
    d_n=None,  # down gate
    l_n=None,  # left gate
    r_n=None,  # right gate
    corner=None,
):
    """
    Easy and way creating blocks
    Reference:
        "c_wall_mid":
        "c_wall_corner"
        "c_wall_corner_turn":
        "c_wall_side":
        "c_flipped_corner":
        "c_flipped_corner_turn":
    Left sizes and Upsides are easy because we position based on top left.
    Right and Downside tho need a bit of calculations :')
    """

    w = game_state.prop_objects["c_wall_mid"]((0, 0)).idle[0].get_width()
    h = (
        game_state.prop_objects["c_wall_side"]((0, 0)).idle[0].get_width()
        * 3
        * 2
    ) + 23

    new_list = []

    if up_side:
        new_list.extend(
            generate_cave_walls(
                game_state,
                direction="right",
                dep_pos=pos,
                n_walls=n + x_side,
                start_type="c_wall_corner",
                end_type="c_flipped_corner_turn",
                door_n=u_n,
            )
        )

    if left_side:
        new_list.extend(
            generate_cave_walls(
                game_state,
                direction="down",
                dep_pos=pos,
                n_walls=n + y_side,
                start_type="c_wall_corner_turn",
                end_type="none",
                door_n=l_n,
            )
        )

    if right_side:
        if corner is None:
            new_list.extend(
                generate_cave_walls(
                    game_state,
                    direction="down",
                    dep_pos=(
                        pos[0]
                        + w * (n + (x_side := x_side if x_side != 0 else 1))
                        - 30,
                        pos[1],
                    ),
                    n_walls=n + y_side,
                    no_begin=True,
                    start_type="none",
                    end_type="none",
                    door_n=r_n,
                )
            )
        else:
            new_list.extend(
                generate_cave_walls(
                    game_state,
                    direction="down",
                    dep_pos=(
                        pos[0]
                        + w * (n + (x_side := x_side if x_side != 0 else 1))
                        - 30,
                        pos[1] - h * n - 90,
                    ),
                    n_walls=n + y_side,
                    start_type="c_wall_side",
                    end_type="c_wall_side",
                    door_n=r_n,
                )
            )

    if down_side:
        new_list.extend(
            generate_cave_walls(
                game_state,
                direction="right",
                dep_pos=(
                    pos[0],
                    pos[1] + h * n + 1,
                ),  # NOTE: do what you did on the below in here
                n_walls=n + x_side,
                start_type="c_wall_corner",
                end_type="c_flipped_corner",
                door_n=d_n,
            )
        )

    return new_list
