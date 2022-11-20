from typing import Any
import pygame
from ..utils import scale, resource_path

from ..PLAYER.items import make_save


class PauseMenu:
    def __init__(self, display: pygame.surface.Surface, ui: Any, state: str):
        self.screen: pygame.surface.Surface = display
        self.W: int = self.screen.get_width()
        self.H: int = self.screen.get_height()

        self.state = state

        # initialize font and load background
        self.font: pygame.font.Font = pygame.font.Font(
            resource_path("data/database/menu-font.ttf"), 25
        )
        self.background: pygame.surface.Surface = scale(
            ui.parse_sprite("catalog_button.png"), 5
        )

        self.buttons: list[pygame.surface.Surface] = [
            self.font.render("Resume", True, (0, 0, 0)),
            self.font.render("Save & Quit", True, (0, 0, 0)),
        ]

        self.btn_rect: list[pygame.rect.Rect] = [  # position of the rect
            button.get_rect(
                center=(
                    self.W // 2,
                    (
                        (
                            self.H // 2
                            - button.get_height()
                            * (len(self.buttons) * 2 - 1)
                            // 2
                        )
                        + i * 2 * button.get_height()
                        + 15
                    ),
                )
            )
            for i, button in enumerate(self.buttons)
        ]

    def handle_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    make_save(self.player, self.state)
                    pygame.quit()
                    raise SystemExit
                case pygame.MOUSEBUTTONDOWN:
                    for id_, rect in enumerate(self.btn_rect):
                        if rect.collidepoint(event.pos):
                            funcs: dict[int, str] = {
                                0: "resume",
                                1: "quit",
                            }
                            return funcs[id_]

    def update(self) -> None | str:

        # manage events
        events = self.handle_events()
        if events is not None:
            return events

        # draw background
        self.screen.blit(
            self.background,
            self.background.get_rect(center=(self.W // 2, self.H // 2)),
        )

        for button, button_rect in zip(self.buttons, self.btn_rect):
            mouse = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse):
                pygame.draw.rect(
                    self.screen,
                    (255, 255, 255),
                    [
                        button_rect.x - 0.1 * button_rect.w,
                        button_rect.y - 0.1 * button_rect.h,
                        button_rect.w * 1.2,
                        button_rect.h * 1.2,
                    ],
                    2,
                )
            self.screen.blit(button, button_rect)
