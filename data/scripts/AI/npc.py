"""
Credits @Marios325346

This script contains our lovely npcs! 


"""
from random import choice
import pygame as pg
from pygame import sprite
from ..utils import (
    load,
    get_sprite,
    flip_vertical,
    scale,
    resource_path,
    UI_Spritesheet,
)


class NPC:
    """Base class for every NPC."""

    def __init__(
        self,
        moving: bool,
        pos: pg.Vector2,
        sprite_sheet_path: str,
        idle: bool = False,
        idle_left=None,
        idle_right=None,
        idle_down=None,
        idle_up=None,
        move_anim: bool = False,
        move_left=None,
        move_right=None,
        move_down=None,
        move_up=None,
        tell_story="",
        remove_bubble=False,
    ):

        self.IDENTITY = "NPC"  # -> useful to check fastly the type of object we're dealing with

        self.move_ability = {
            "left": True,
            "right": True,
            "up": True,
            "down": True,
        }

        self.quest_interactions = {}

        # STATE
        self.state = "move" if moving else "idle"
        self.moving = moving
        self.velocity = pg.Vector2(1, 1)
        self.interacting = False
        self.interactable = True
        self.highlight = False

        # SPRITESHEET
        self.sprite_sheet = load(resource_path(sprite_sheet_path))

        # ANIMATION
        self.anim_delay = 0
        self.anim_index = 0
        self.anim_duration = {"idle": 100, "move": 100}

        # Story telling
        self.remove_bubble = remove_bubble
        self.tell_story = tell_story

        self.idle = idle
        self.move_anim = move_anim
        self.direction = "left"
        self.it_re_size = (100, 100)
        self.interaction_rect = None

        self.move_manager = {
            "right": self.load_from_spritesheet(move_right)
            if self.move_anim
            else None,
            "left": self.load_from_spritesheet(move_left)
            if self.move_anim
            else None,
            "up": self.load_from_spritesheet(move_up)
            if self.move_anim
            else None,
            "down": self.load_from_spritesheet(move_down)
            if self.move_anim
            else None,
        }

        self.idle_manager = {
            "right": self.load_from_spritesheet(idle_right)
            if self.idle
            else None,
            "left": self.load_from_spritesheet(idle_left)
            if self.idle
            else None,
            "up": self.load_from_spritesheet(idle_up) if self.idle else None,
            "down": self.load_from_spritesheet(idle_down)
            if self.idle
            else None,
        }

        self.anim_manager = {
            "idle": self.idle_manager,
            "move": self.move_manager,
        }

        # IMAGES AND COORDINATES
        self.image = pg.Surface((1, 1))
        self.rect = self.image.get_rect(center=pos)

    def load_from_spritesheet(self, coords):
        if coords == [0, 0, 0, 0, 0, 0] or coords is None:
            return None
        if coords[-1] == "flip":
            return [
                flip_vertical(
                    scale(
                        get_sprite(
                            self.sprite_sheet,
                            coords[0] + coords[2] * i,
                            coords[1],
                            coords[2],
                            coords[3],
                        ),
                        coords[4],
                    )
                )
                for i in range(coords[5])
            ]
        return [
            scale(
                get_sprite(
                    self.sprite_sheet,
                    coords[0] + coords[2] * i,
                    coords[1],
                    coords[2],
                    coords[3],
                ),
                coords[4],
            )
            for i in range(coords[5])
        ]

    def state_manager(self):
        if self.interacting:
            self.state = "idle"
        elif self.moving:
            self.state = "move"
        else:
            self.state = "idle"

    def animate(self):

        current_anim = self.anim_manager[self.state]
        if type(current_anim) is dict:
            current_anim = current_anim[self.direction]

        if (
            pg.time.get_ticks() - self.anim_delay
            > self.anim_duration[self.state]
        ):
            self.anim_delay = pg.time.get_ticks()
            self.anim_index = (self.anim_index + 1) % len(current_anim)
            self.image = current_anim[self.anim_index]
            self.rect = self.image.get_rect(center=self.rect.center)

    def update_interaction_rect(self, scroll):
        match self.direction:  # lgtm [py/syntax-error]
            case "left":
                self.interaction_rect = pg.Rect(
                    self.rect.x - self.it_re_size[0],
                    self.rect.centery - self.it_re_size[1] // 2,
                    *self.it_re_size
                )
            case "right":
                self.interaction_rect = pg.Rect(
                    self.rect.right,
                    self.rect.centery - self.it_re_size[1] // 2,
                    *self.it_re_size
                )
            case "up":
                self.interaction_rect = pg.Rect(
                    self.rect.centerx - self.it_re_size[0] // 2,
                    self.rect.y - self.it_re_size[1],
                    *self.it_re_size
                )
            case "down":
                self.interaction_rect = pg.Rect(
                    self.rect.centerx - self.it_re_size[0] // 2,
                    self.rect.bottom,
                    *self.it_re_size
                )
        self.interaction_rect.topleft -= scroll

    def render_highlight(self, screen, scroll):
        """Outlining the npcs, to show interactness
        Args:
            screen (pygame.Surface): main window of the game
            scroll (int tuple): the camera scroller offset
        """

        outline = pg.mask.from_surface(self.image).to_surface()
        outline.set_colorkey((0, 0, 0))
        outline.set_alpha(155)
        thickness = 2
        pos = self.rect.topleft - scroll
        screen.blits(
            [
                (outline, pos + pg.Vector2(thickness, 0)),
                (outline, pos + pg.Vector2(-thickness, 0)),
                (outline, pos + pg.Vector2(0, -thickness)),
                (outline, pos + pg.Vector2(0, thickness)),
            ]
        )

    def logic(self, scroll):
        self.state_manager()
        self.animate()
        self.update_interaction_rect(scroll)

    def update(self, screen, scroll):
        self.logic(scroll)
        if self.highlight:
            self.render_highlight(screen, scroll)
        screen.blit(
            self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1])
        )
        # pg.draw.rect(screen, (0, 0, 255), self.interaction_rect, 1)


class MovingNPC(NPC):
    def __init__(
        self,
        movement: str,  # "random" | "lateral" | "vertical"
        range_rect: pg.Rect,  # basically the delimitations of the npc's movements
        velocity: pg.Vector2,
        pos: pg.Vector2,
        sprite_sheet_path: str,
        idle: bool = False,
        idle_left=None,
        idle_right=None,
        idle_down=None,
        idle_up=None,
        move_anim: bool = False,
        move_left=None,
        move_right=None,
        move_down=None,
        move_up=None,
        tell_story=None,
        remove_bubble=False,
    ):

        super().__init__(
            True,
            pos,
            sprite_sheet_path,
            idle,
            idle_left,
            idle_right,
            idle_down,
            idle_up,
            move_anim,
            move_left,
            move_right,
            move_down,
            move_up,
            tell_story,
        )

        self.remove_bubble = remove_bubble
        self.movement = movement
        self.range_rect = range_rect
        self.velocity = velocity

    def check_outside_rect(self):
        match self.direction:
            case "left":
                return (
                    True
                    if not pg.Rect(
                        self.rect.x - self.velocity[0],
                        self.rect.y,
                        *self.rect.size
                    ).colliderect(self.range_rect)
                    else False
                )
            case "right":
                return (
                    True
                    if not pg.Rect(
                        self.rect.x + self.velocity[0],
                        self.rect.y,
                        *self.rect.size
                    ).colliderect(self.range_rect)
                    else False
                )
            case "up":
                return (
                    True
                    if not pg.Rect(
                        self.rect.x,
                        self.rect.y - self.velocity[1],
                        *self.rect.size
                    ).colliderect(self.range_rect)
                    else False
                )
            case "down":
                return (
                    True
                    if not pg.Rect(
                        self.rect.x,
                        self.rect.y + self.velocity[1],
                        *self.rect.size
                    ).colliderect(self.range_rect)
                    else False
                )

    def move(self):

        # If the player has not click the button, keep the npc moving
        if not self.interacting:
            match self.direction:
                case "left":
                    self.rect.x -= (
                        self.velocity[0] if self.move_ability["left"] else 0
                    )
                case "right":
                    self.rect.x += (
                        self.velocity[0] if self.move_ability["right"] else 0
                    )
                case "down":
                    self.rect.y += (
                        self.velocity[1] if self.move_ability["up"] else 0
                    )
                case "up":
                    self.rect.y -= (
                        self.velocity[1] if self.move_ability["down"] else 0
                    )

    def switch_directions(self, blocked_direction=None):

        directions = ["left", "right", "down", "up"]
        directions.remove(self.direction)
        if blocked_direction is not None and blocked_direction in directions:
            directions.remove(blocked_direction)

        match self.movement:
            case "random":
                self.direction = choice(directions)
            case "lateral":
                if blocked_direction is not None:
                    if self.direction == blocked_direction == "left":
                        self.direction = "right"
                    elif self.direction == blocked_direction == "right":
                        self.direction = "left"
                else:
                    self.direction = (
                        "right" if self.direction == "left" else "left"
                    )

            case "vertical":
                if blocked_direction is not None:
                    if self.direction == blocked_direction == "up":
                        self.direction = "down"
                    elif self.direction == blocked_direction == "down":
                        self.direction = "up"
                else:
                    self.direction = (
                        "up" if self.direction == "down" else "down"
                    )

    def logic(self, scroll):
        super().logic(scroll)

        if self.check_outside_rect():
            self.switch_directions()

        self.move()

    def update(self, screen, scroll):
        self.update_interaction_rect(scroll)
        return super().update(screen, scroll)


class Mau(MovingNPC):
    def __init__(self, dep_pos, range_):
        super().__init__(
            pos=dep_pos,
            movement="lateral",
            range_rect=pg.Rect(*dep_pos, *range_),
            velocity=pg.Vector2(1, 1),
            sprite_sheet_path="data/sprites/npc_spritesheet.png",
            idle=True,
            idle_right=[131, 49, 43, 33, 2, 3],
            idle_left=[131, 49, 33, 33, 2, 3, "flip"],
            move_anim=True,
            move_right=[3 + 39, 49, 43, 33, 2, 3],
            move_left=[3 + 39, 49, 43, 33, 2, 3, "flip"],
            tell_story="Meow meow meow",
        )

        self.it_re_size = (75, 100)
        self.anim_duration = {"idle": 115, "move": 100}  # HE FLOPS


class Candy(MovingNPC):
    """
    Όταν
    """

    def __init__(self, pos, awake=False):
        super(Candy, self).__init__(
            movement="lateral",
            range_rect=pg.Rect(
                pos, (400, 200)
            ),  # TODO : get a real range rect (didn't know what to put)
            velocity=pg.Vector2(2, 0),
            pos=pos,
            sprite_sheet_path="data/sprites/npc_spritesheet.png",
            idle=True,
            idle_down=[119, 87, 37, 27, 2, 2],
            move_anim=True,
            move_right=[2, 86, 38, 29, 2, 2],
            move_left=[2, 86, 38, 29, 2, 2, "flip"],
        )
        self.direction = "down"
        self.state = "idle"
        self.it_re_size = (100, 100)

        self.anim_duration["idle"] = 1000
        self.anim_duration["move"] = 250
        self.status = "sleeping" if not awake else "awake"
        if awake:
            self.direction = "right"
            self.state = "move"
            self.tell_story = "Meow meow meow"
        else:
            self.tell_story = "Zzzz.\nshe is sleeping on the warm carpet.\nbetter not wake her up."

        self.animate()

    def state_manager(self):
        if self.status == "sleeping":
            return super(Candy, self).state_manager()
        else:
            self.state = "move"
            if self.interacting:
                self.anim_duration["move"] = 10000000
            else:
                self.anim_duration["move"] = 250

    def update(self, screen, scroll):
        if self.status == "awake" and self.direction == "down":
            self.direction = "right"
        return super(Candy, self).update(screen, scroll)

    def logic(self, scroll):
        if self.status == "awake":
            if self.direction == "down":
                self.direction = "right"
            self.state = "move"
            return super(Candy, self).logic(scroll)
        elif self.status == "sleeping":
            self.state = "idle"
            self.direction = "down"
            self.animate()


class Cynthia(NPC):
    def __init__(self, pos):
        super().__init__(
            moving=False,
            pos=pos,
            sprite_sheet_path="data/sprites/npc_spritesheet.png",
            idle=True,
            idle_down=[1, 1, 26, 42, 3, 3],
            remove_bubble=True,
        )
        self.direction = "down"
        self.state = "idle"
        self.anim_duration = {"idle": 750, "move": 100}
        self.it_re_size = (60, 60)


class CynthiaSchool(NPC):
    def __init__(self, pos):
        super().__init__(
            moving=False,
            pos=pos,
            sprite_sheet_path="data/sprites/npc_spritesheet.png",
            idle=True,
            idle_down=[1, 1, 26, 42, 3, 3],
            tell_story="John what are you doing here?\nYou are supposed to go to the training field ",
        )
        self.direction = "down"
        self.state = "idle"
        self.anim_duration = {"idle": 750, "move": 100}
        self.it_re_size = (60, 60)


class Manos(NPC):
    def __init__(self, pos, tell_story=""):
        super().__init__(
            moving=False,
            pos=pos,
            sprite_sheet_path="data/sprites/npc_spritesheet.png",
            idle=True,
            idle_down=[2, 120, 20, 45, 3, 3],
            remove_bubble=True,
        )
        self.direction = "down"
        self.state = "idle"
        self.anim_duration = {"idle": 750, "move": 100}
        self.it_re_size = (60, 60)


class Alexia(NPC):
    def __init__(self, pos):
        super(Alexia, self).__init__(
            moving=False,
            pos=pos,
            sprite_sheet_path="data/sprites/npc_spritesheet.png",
            idle=True,
            idle_down=[0, 169, 26, 43, 3, 3],
            remove_bubble=True,
        )
        self.direction = "down"
        self.state = "idle"
        self.anim_duration = {"idle": 750, "move": 100}
        self.it_re_size = (60, 60)
