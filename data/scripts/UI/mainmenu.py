from re import L
from typing import Any
import pygame as p
import json

from pygame.key import name
from pygame.mouse import set_visible
from ..utils import scale, load, resource_path


class Menu:
    def __init__(
        self,
        game_instance: Any,
        title_font: p.font.Font,
        ui: Any,
    ):
        # Data from Game Class
        self.screen, self.title_font = game_instance.DISPLAY, title_font
        self.game_instance = game_instance

        # Macros
        self.half_w, self.half_h = (
            self.screen.get_width() // 2,
            self.screen.get_height() // 2,
        )

        # Setup the white colored title with black outline
        self.title_logo = [
            title_font.render(
                "John's Adventure", True, (255 * i, 255 * i, 255 * i)
            )
            for i in [0, 1]
        ]

        # Background image
        self.bg_img = p.transform.scale(
            load(resource_path("data/ui/main_menu/background1.png")),
            (
                1280,
                720,
            ),  # Due to its less size, I am transforming it to 720p because its the default res
        )

        self.bg_img2 = p.transform.scale(
            load(resource_path("data/ui/main_menu/background2.png")),
            (
                1280,
                720,
            ),  # Due to its less size, I am transforming it to 720p because its the default res
        )

        # Buttons
        self.btns = [
            [
                scale(ui.parse_sprite("button.png"), 4),
                scale(ui.parse_sprite("button_hover.png"), 4),
            ]  # 3 Buttons, 3 sublists...
            for i in range(3)
        ]

        self.f = p.font.Font(resource_path("data/database/menu-font.ttf"), 24)

        self.btns_text = [
            self.f.render("Play", True, (255, 255, 255)),
            self.f.render("Controls", True, (255, 255, 255)),
            self.f.render("Quit", True, (255, 255, 255)),
        ]

        self.btns_rects = [
            btn[
                0
            ].get_rect(  # We only need one of the two Gets the rect of its btn and positions them on the center
                # of the screen(50px a little down) with 60px gap on each
                center=(self.half_w, self.half_h + 50 + 60 * i)
            )
            for i, btn in enumerate(self.btns)
        ]

        # Function
        self.event = None  # This is a temp value for control saving

        self.show_settings = False  # if True, it will show the settings menu

        self.changing = False  # if True means the user clicked on the button that wishes to change

        self.controls_error = (
            False  # if True means the user put a duplicate key
        )

        self.blank_keys = (
            False  # if True, means the user left a blank key in Controls
        )

        self.change_key_index = None  # The index of the key we're changing

        # Settings
        self.settings_bg = scale(ui.parse_sprite("catalog_button.png"), 11)

        # Load/Save Data
        self.save = self.get_data(resource_path("data/database/data.json"))

        # Load the GUI keys and Text surfaces based on the above data
        self.keybinds = [
            scale(ui.parse_sprite("keybind.png"), 5)
            for key in self.save["controls"]
        ]
        self.settings_text = [
            self.f.render(f"{key}", True, (0, 0, 0))
            for key in self.save["controls"]
        ]
        self.start_game = False  # if True, player click Play button]

        self.start_time = p.time.get_ticks()

    """ Utils """

    @staticmethod
    def get_data(path):
        with open(resource_path(path), "r") as f:
            return json.load(f)

    def save_data(self):
        with open(resource_path("data/database/data.json"), "w+") as f:
            return json.dump(self.save, f, indent=4)

    # This function is for centering the keywords in control section
    def draw_txt(self, txt, rect, surf):
        y_gap = 8  # Y coords for the text
        x_gap = surf.get_width() // 2
        x_gap -= (
            55 if len(txt) == 5 or len(txt) == 10 else (12 if len(txt) else 0)
        )
        self.screen.blit(
            self.f.render(txt, True, (0, 0, 0))
            if len(txt) != 10
            else self.f.render(txt[-5:], True, (0, 0, 0)),
            (rect[0] + x_gap, rect[1] + y_gap),
        )

    def buttons_menu(self, m):
        # Black outline
        self.screen.blit(
            self.title_logo[0],
            (
                self.half_w + 20 - self.title_logo[0].get_width() // 2,
                self.half_h - 190,
            ),
        )
        # White Texture
        self.screen.blit(
            self.title_logo[1],
            (
                self.half_w + 20 - self.title_logo[1].get_width() // 2,
                self.half_h - 192,
            ),
        )

        # Draw buttons and also their hover image if the user hovers over it
        for i, btn in enumerate(self.btns):
            self.screen.blit(
                btn[1] if self.btns_rects[i].collidepoint(m) else btn[0],
                self.btns_rects[i],
            )
            self.screen.blit(
                self.btns_text[i],
                self.btns_text[i].get_rect(
                    centerx=self.half_w, centery=self.btns_rects[i].centery - 2
                ),
            )

    def settings_menu(self, m):
        """Settings"""
        if self.show_settings:
            self.screen.blit(
                self.settings_bg,
                (
                    self.half_w - self.settings_bg.get_width() // 2,
                    self.half_h - self.settings_bg.get_height() // 2,
                ),
            )

            if self.controls_error:
                self.screen.blit(
                    self.f.render("Please put another key!", True, (0, 0, 0)),
                    (self.half_w - 220, self.half_h - 200),
                )
            elif self.blank_keys:
                self.screen.blit(
                    self.f.render("Please fill the keys!", True, (0, 0, 0)),
                    (self.half_w - 220, self.half_h - 200),
                )

            #  Key Button
            key_data = list(self.save["controls"].values())
            for i, key in enumerate(self.keybinds):

                group_y = (
                    20  # A temp value to tweak the Y position of all of them
                )

                bind = (
                    f"{p.key.name(key_data[i])}"
                    if type(key_data[i]) is int
                    else " "
                )

                if i < 4:
                    rect = key.get_rect(
                        center=(
                            self.half_w - 120,
                            self.half_h - 110 + group_y + 60 * i,
                        )
                    )
                    self.screen.blit(key, rect), self.screen.blit(
                        self.settings_text[i], (rect[0] - 130, rect[1] + 10)
                    )
                else:
                    rect = key.get_rect(
                        center=(
                            self.half_w + 265,
                            self.half_h - 350 + group_y + 60 * i,
                        )
                    )
                    self.screen.blit(key, rect), self.screen.blit(
                        self.settings_text[i], (rect[0] - 220, rect[1] + 10)
                    )

                self.draw_txt(bind, rect, key)  # Center text

                # if the player clicks the button, reset the keybind and save the index for configuration
                if (
                    rect.collidepoint(m)
                    and self.event.type == p.MOUSEBUTTONDOWN
                    and self.event.button == 1
                ):
                    (
                        self.changing,
                        self.controls_error,
                        self.change_key_index,
                    ) = (True, False, i)
                    # Find the key using list()[index]
                    txt = list(self.save["controls"])[i]
                    self.save["controls"][txt] = 0  # Reset that key

    """ Drawing/ Function """

    def update(self, mouse):
        # Menu background

        if p.time.get_ticks() - self.start_time < 4500:

            if p.time.get_ticks() - self.start_time < 2250:
                self.screen.blit(self.bg_img2, (0, 0))
            else:
                self.screen.blit(self.bg_img, (0, 0))

        else:
            self.start_time = p.time.get_ticks()

        """ User interact with Settings button"""
        if self.show_settings:
            self.settings_menu(mouse)
        else:
            self.buttons_menu(mouse)

        self.controls(mouse)

    def controls(self, m):
        """
        Any input related to the menu. I am saving event to a value because Game Class needs it to execute the game.
        self.changing occurs when you click on the keybinds and show settings when you click the button 'Settings'.
        """
        for e in p.event.get():
            self.event = e  # I am passing this to the keybinds
            match e.type:
                case p.QUIT:
                    self.game_instance.quit_()
                case p.MOUSEBUTTONDOWN:
                    if not self.show_settings:
                        if self.btns_rects[0].collidepoint(m):
                            self.start_game = True
                        if self.btns_rects[1].collidepoint(m):
                            self.show_settings = True
                        if self.btns_rects[2].collidepoint(m):
                            raise SystemExit

                case p.KEYDOWN:

                    if e.key == self.save["controls"]["fullscreen"]:
                        p.display.toggle_fullscreen()

                    if self.changing:
                        controls = list(self.save["controls"])
                        # Find Duplicate among keys (amongus ??!?!?)
                        for key, btn in self.save["controls"].items():
                            if e.key == btn:
                                self.controls_error = True

                        if (
                            e.key != p.K_ESCAPE and not self.controls_error
                        ):  # Escape button is not allowed
                            txt = controls[self.change_key_index]
                            self.save["controls"][txt] = e.key
                            self.controls_error = (
                                self.changing
                            ) = (
                                self.blank_keys
                            ) = False  # Change the button and close it
                        else:
                            # Warn the user that he must fill the keys
                            self.blank_keys = True

                            # if everything is correct, write the new data to the json and close the menu
                    if (
                        self.show_settings
                        and e.key == p.K_ESCAPE
                        and not self.blank_keys
                    ):
                        self.save_data()
                        self.show_settings = False
