from typing import Any
import pygame

from .utils import resource_path

from .PLAYER.player import Player
from .AI.npc import NPC

from copy import copy


class Debugging:
    def __init__(
        self,
        game_instance: Any,
        no_rect: bool,
    ) -> None:

        self.no_rect = no_rect
        self.screen = game_instance.DISPLAY
        self.game: Any = game_instance
        self.player: Player = self.game.player

        self.colors = {
            "interaction_rect": (255, 255, 0),
            "collision_rect": (0, 255, 0),
            "attacking_rect": (255, 0, 0),
            "exit_rect": (255, 255, 0),
            "void": (0, 0, 0),
        }

        self.font = pygame.font.Font(
            resource_path("data/database/menu-font.ttf"), 15
        )

    def draw_text(
        self,
        txt: str,
        color: tuple[int],
        pos: tuple[int],
        bottomleft: bool = False,
    ) -> None:
        text: pygame.surface.Surface = self.font.render(
            txt, True, tuple(color)
        )

        rect: pygame.rect.Rect = text.get_rect(topleft=pos)
        if bottomleft:
            rect.bottomleft = tuple(pos)

        self.screen.blit(text, rect)

    def update(self) -> None:

        """Primitive debugging system showing rects.

        TODO: Improve it to show stats. And make it more readable."""

        if not self.no_rect:
            if not self.game.menu and not self.game.loading:
                scroll = self.player.camera.offset.xy
                objects: list[NPC | Player] = copy(
                    self.game.game_state.objects
                )
                objects.append(self.player)

                for obj in objects:
                    # Remove this once debugging stops
                    if type(obj) is pygame.Rect:
                        pygame.draw.rect(
                            self.screen,
                            self.colors["collision_rect"],
                            pygame.Rect(
                                obj.topleft - self.player.camera.offset.xy,
                                obj.size,
                            ),
                            2,
                        )
                    else:
                        for key, color in self.colors.items():
                            if hasattr(obj, key):
                                attr = getattr(obj, key)
                                if type(attr) is pygame.Rect:
                                    pygame.draw.rect(
                                        self.screen, color, attr, 1
                                    )

                        col_rect = copy(obj.rect)
                        if hasattr(obj, "IDENTITY"):
                            if obj.IDENTITY in ["NPC", "PROP", "ENEMY"]:
                                col_rect.topleft -= scroll

                            if hasattr(obj, "d_collision"):
                                col_rect.topleft += pygame.Vector2(
                                    *obj.d_collision[:2]
                                )
                                col_rect.size = obj.d_collision[2:]
                            pygame.draw.rect(
                                self.screen,
                                self.colors["collision_rect"],
                                col_rect,
                                2,
                            )

                            if obj.IDENTITY == "ENEMY":
                                self.draw_text(
                                    f"STATUS: {obj.status}",
                                    (255, 255, 255),
                                    obj.rect.topleft - scroll,
                                )

                exit_rects = self.game.game_state.exit_rects
                for exit_rect in exit_rects:
                    r = copy(exit_rects[exit_rect][0])
                    r.topleft -= scroll
                    pygame.draw.rect(
                        self.screen, self.colors["exit_rect"], r, 2
                    )
                    self.draw_text(
                        f"To: {exit_rect[0]}",
                        tuple(self.colors["exit_rect"]),
                        r.topleft,
                        bottomleft=True,
                    )

                pl_col_rect = copy(self.player.rect)
                pl_col_rect.topleft -= scroll
                pl_col_rect.topleft -= pygame.Vector2(15, -70)
                pl_col_rect.w -= 70
                pl_col_rect.h -= 115
                pygame.draw.rect(
                    self.screen, self.colors["collision_rect"], pl_col_rect, 1
                )

                try:
                    pygame.draw.rect(
                        self.screen,
                        (255, 0, 0),
                        self.player.attacking_hitbox,
                        2,
                    )
                except TypeError:
                    pass

                position: tuple[int] = (
                    self.player.rect.topleft - self.player.camera.offset.xy
                )

                itr_box: pygame.Rect = pygame.Rect(
                    *position, self.player.rect.w // 2, self.player.rect.h // 2
                )

                # Manual Position tweaks
                itr_box.x -= 17
                itr_box.y += 45
                pygame.draw.rect(self.screen, (0, 0, 0), itr_box, 2)
