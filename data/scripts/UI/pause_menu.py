import pygame as pg
from ..utils import scale, resource_path


class PauseMenu:

    def __init__(self, display, ui):

        # get screen + screen's size
        self.screen = display
        self.W, self.H = self.screen.get_size()

        # initialize font and load background
        self.font = pg.font.Font(resource_path("data/database/menu-font.ttf"), 25)
        self.background = scale(ui.parse_sprite("catalog_button.png"), 5)

        self.buttons = [  # generate all three buttons
            self.font.render("Resume", True, (0, 0, 0)),
            self.font.render("Settings", True, (0, 0, 0)),
            self.font.render("Save & Quit", True, (0, 0, 0)),
        ]
        self.btn_rect = [  # position of the rect
            button.get_rect(center=(
                self.W // 2, ((self.H // 2 - button.get_height() *
                               (len(self.buttons) * 2 - 1) // 2) + i * 2 * button.get_height() + 15)))
            for i, button in enumerate(self.buttons)
        ]
        self.funcs = {  # function assigned to the buttons (key = btn index, item = function associated)
            0: resume,  # func that will be executed if button with index 0 is clicked
            1: settings,
            2: save_and_quit
        }

    def handle_button_clicks(self, pos):  # get the click result
        for id_, rect in enumerate(self.btn_rect):
            if rect.collidepoint(pos):
                return self.funcs[id_]()

    def handle_events(self):  # handle events (including quit and button handling)
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    pg.quit()
                    raise SystemExit
                case pg.MOUSEBUTTONDOWN:
                    return self.handle_button_clicks(event.pos)

    def init_pause(self):  # setup the pause menu
        pg.mouse.set_visible(True)
        surf = pg.Surface(self.screen.get_size())
        surf.fill((0, 0, 0))
        surf.set_alpha(200)
        self.screen.blit(surf, (0, 0))

    def update(self):

        # manage events
        events = self.handle_events()
        if events is not None:
            return events

        # draw background
        self.screen.blit(self.background, self.background.get_rect(center=(self.W // 2, self.H // 2)))
        # display buttons, including hovering
        for i in range(len(self.buttons)):
            if self.btn_rect[i].collidepoint(pg.mouse.get_pos()):
                pg.draw.rect(self.screen, (255, 255, 255), [self.btn_rect[i].x - 0.1 * self.btn_rect[i].w,
                                                            self.btn_rect[i].y - 0.1 * self.btn_rect[i].h,
                                                            self.btn_rect[i].w * 1.2, self.btn_rect[i].h * 1.2], 2)
            self.screen.blit(self.buttons[i], self.btn_rect[i])


def quit_pause():
    pg.mouse.set_visible(False)


def resume():
    return "resume"


def settings():
    # TODO: make an in game settings screen
    return "settings"


def save_and_quit():
    return "quit"
