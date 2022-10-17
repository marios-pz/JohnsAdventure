import pygame as pg
from ..utils import load, get_sprite, scale, resource_path
from copy import copy
import json


class LoadingScreen:
    def __init__(self, screen: pg.surface.Surface):

        # unpack constructor's arguments
        self.screen = screen
        self.W, self.H = screen.get_size()

        # cat
        self.cat_spr_sh = load(
            resource_path("data/sprites/npc_spritesheet.png")
        )
        self.cat_sprites = [
            scale(get_sprite(self.cat_spr_sh, 43 * i, 49, 43, 33), 2)
            for i in range(3)
        ]
        # colors
        self.bg_color = (0, 0, 0)
        self.font_color = (255, 255, 255)

        # text
        self.font = pg.font.Font(
            resource_path("data/database/menu-font.ttf"), 24
        )

        # animation
        self.current_time = pg.time.get_ticks()
        self.delay_cat_anim = (
            self.delay_dot_anim
        ) = self.index_dot_anim = self.index_cat_anim = 0

        # duration
        self.start_loading = 0
        self.duration = 2500
        self.next_state = None
        self.end_music = None

        # loading screen options
        self.text = True
        self.cat = True
        self.main_loading = False
        self.key_end = False
        self.ended_loading = False

        # big text "John's adventure"
        self.font2 = pg.font.Font(
            resource_path("data/database/Blacksword.otf"), 75
        )  # font
        self.john_text = self.font2.render(
            "John's Adventure", True, (255, 255, 255)
        )  # rendering of John's adventure
        self.txt_jhn = copy(
            self.john_text
        )  # copy the text in order to reblit it every frame
        self.txt_jhn_bg = copy(
            self.john_text
        )  # copy it once more, in order to blit it with a lower alpha as a background
        self.txt_jhn_bg.set_alpha(100)  # set this "lower alpha" noted before
        self.john_text_rect = self.john_text.get_rect(
            center=(
                self.screen.get_width() // 2,
                self.screen.get_height() // 2,
            )
        )  # place it in the center

        # "PRESS 'key' TO CONTINUE"
        self.delay_blinking = 0  # delay to animate
        self.decreasing = False  # decreasing alpha or not
        self.text_key = self.font.render(
            f"Press {pg.key.name(self.get_key())} to continue",
            True,
            (255, 255, 255),
        )  # rendering
        self.text_key_rect = self.text_key.get_rect(
            center=(
                self.screen.get_width() // 2,
                self.screen.get_height() // 2,
            )
        )  # placing
        self.has_to_kill = (
            False  # indicates if the loading screen has to be killed
        )

    def init(self, load_type: str, duration: int = 500):
        match load_type:
            case "loading...":
                pass
            case "main_loading":
                self.start_loading = pg.time.get_ticks()
                self.duration = duration

    def draw(self, screen: pg.Surface, load_type: str):

        if load_type == "loading...":
            if pg.time.get_ticks() - self.delay_dot_anim > 250:
                self.index_dot_anim = (self.index_dot_anim + 1) % 3
                self.delay_dot_anim = pg.time.get_ticks()
            # render loading text -> "Loading..."
            loading_text = self.font.render(
                f"Loading {'.' * (self.index_dot_anim + 1)}",
                True,
                self.font_color,
            )
            # blit loading text
            screen.blit(
                loading_text,
                loading_text.get_rect(bottomleft=(50, self.H - 50)),
            )

        elif load_type == "main_loading":
            self.john_text.fill((0, 0, 0))
            self.john_text.blit(self.txt_jhn, (0, 0))
            pg.draw.rect(
                self.john_text,
                (0, 0, 0, 0),
                [
                    self.john_text_rect.width
                    / self.duration
                    * (pg.time.get_ticks() - self.start_loading),
                    0,
                    self.john_text_rect.width,
                    self.john_text_rect.height,
                ],
            )
            self.screen.blit(self.txt_jhn_bg, self.john_text_rect)
            self.screen.blit(self.john_text, self.john_text_rect)

        elif load_type == "ended":
            if pg.time.get_ticks() - self.delay_blinking > 20:
                self.delay_blinking = pg.time.get_ticks()

                if self.decreasing:  # decrease key's alpha
                    if self.text_key.get_alpha() - 10 < 0:
                        self.decreasing = False
                    self.text_key.set_alpha(self.text_key.get_alpha() - 10)
                else:  # increase key's alpha
                    if self.text_key.get_alpha() + 10 > 255:
                        self.decreasing = True
                    self.text_key.set_alpha(self.text_key.get_alpha() + 10)

            self.screen.blit(
                self.text_key, self.text_key_rect
            )  # blit the key text

    def get_key(self):
        with open(resource_path("data/database/data.json"), "r") as f:
            return json.load(f)["controls"]["interact"]

    def update(self):

        if self.cat:
            # animate cat
            if self.current_time - self.delay_cat_anim > 100:
                self.index_cat_anim = (self.index_cat_anim + 1) % len(
                    self.cat_sprites
                )
                self.delay_cat_anim = self.current_time
            # blit cat
            self.screen.blit(
                self.cat_sprites[self.index_cat_anim],
                self.cat_sprites[self.index_cat_anim].get_rect(
                    bottomright=(self.W - 50, self.H - 50)
                ),
            )
