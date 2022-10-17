from typing import Any
import pygame as pg
from .quest_manager import QuestManager
from ..utils import resource_path, smooth_scale

# Please change the bg ui to these rgbs
bg_color = (239, 159, 26)
bg_color_hovered = (199, 134, 26)


class QuestUI:
    def __init__(self, world_instance: Any, quest_manager: QuestManager):
        # get the screen
        self.screen = world_instance.DISPLAY
        # get the quest manager
        self.quest_manager = quest_manager
        # variable to show or not
        self.show_menu = False

        # pos of the first header
        self.start_pos = (20, 30)
        self.gap = 20  # gap between the things
        self.gap_x = 42  # "indentation" for the inner tasks

        self.cross = pg.Surface((25, 25), pg.SRCALPHA)
        pg.draw.line(
            self.cross, (255, 0, 0), (0, 0), self.cross.get_size(), width=8
        )
        pg.draw.line(
            self.cross,
            (255, 0, 0),
            (self.cross.get_width(), 0),
            (0, self.cross.get_height()),
            width=8,
        )

        self.header_font = pg.font.Font(
            resource_path("data/database/menu-font.ttf"), 20
        )
        self.step_font = pg.font.Font(
            resource_path("data/database/menu-font.ttf"), 15
        )
        self.step_font2 = pg.font.Font(
            resource_path("data/database/menu-font.ttf"), 13
        )

        # background for headers (main titles)
        self.bg_headers = pg.Surface((250, 100))
        self.bg_headers.fill((255, 255, 255))  # remove it when you change it

        # background for quests (must be resizable)
        self.bg_quests = pg.Surface((100, 100))
        self.bg_quests.fill((255, 255, 255))

        # main titles of the quests
        self.headers: list[pg.Surface] = [
            pg.Surface((300, 50)) for _ in self.quest_manager.quests
        ]

        # will be updated later (for the right positions)
        self.header_rects: list[pg.Rect] = [
            header.get_rect() for header in self.headers
        ]
        for header in self.headers:
            header.fill(
                (255, 255, 255)
            )  # -> TODO: change the color with your new fancy UI's color

        # write the titles on the headers
        for index, quest in enumerate(self.quest_manager.quests.values()):
            header_text = self.header_font.render(quest.name, True, (0, 0, 0))
            self.headers[index] = header_text

        self.quests_inside: list[list[pg.Surface]] = [
            [
                self.step_font.render(step_name, True, (0, 0, 0))
                for step_name in quest.steps_names
            ]
            for quest in self.quest_manager.quests.values()
        ]
        self.quests_inside_done = [
            list(quest.quest_state.values())
            for quest in self.quest_manager.quests.values()
        ]

        self.header_active = [True for _ in self.headers]

        self.header_scroll = [0 for _ in self.header_active]
        self.scroll_incrementing = ["+" for _ in self.header_active]
        self.delays = [0 for _ in self.header_active]
        self.duration = 30

    def set_active(self):
        self.show_menu = not self.show_menu

    def handle_clicks(self, pos: tuple[int, int]):
        click = False
        for index, rect in enumerate(self.header_rects):
            if rect.collidepoint(pos):  # activate / switch off the header
                if not self.header_active[index]:
                    self.header_active[index] = True
                    self.scroll_incrementing[index] = "+"
                else:
                    self.scroll_incrementing[index] = "-"
                self.delays[index] = pg.time.get_ticks()
                click = True
        return click

    def get_n_steps(self, index) -> int:
        n_true = sum(
            list(
                list(self.quest_manager.quests.values())[
                    index
                ].quest_state.values()
            )
        )
        length = len(self.quests_inside[index])
        return n_true + 1 if n_true + 1 <= length else length

    def render(self):

        self.quests_inside_done = [
            list(quest.quest_state.values())
            for quest in self.quest_manager.quests.values()
        ]

        if self.show_menu:
            dy = 0
            for index, active in enumerate(self.header_active):

                if self.scroll_incrementing[index] == "." and active:
                    self.header_scroll[index] = self.get_n_steps(index)

                # MISSION HEADER TITLE
                header_color = (
                    bg_color
                    if not pg.Rect(
                        self.start_pos[0],
                        self.start_pos[1] + dy,
                        self.headers[index].get_width() + 10,
                        self.headers[index].get_height() + 10,
                    ).collidepoint(pg.mouse.get_pos())
                    else bg_color_hovered
                )

                # UI HEADER
                pg.draw.rect(
                    self.screen,
                    header_color,
                    [
                        self.start_pos[0],
                        self.start_pos[1] + dy,
                        self.headers[index].get_width() + 10,
                        self.headers[index].get_height() + 10,
                    ],
                    border_radius=8,
                )
                # OUTLINE
                pg.draw.rect(
                    self.screen,
                    (0, 0, 0),
                    [
                        self.start_pos[0],
                        self.start_pos[1] + dy,
                        self.headers[index].get_width() + 10,
                        self.headers[index].get_height() + 10,
                    ],
                    border_radius=8,
                    width=2,
                )

                self.screen.blit(
                    self.headers[index],
                    [self.start_pos[0] + 5, self.start_pos[1] + dy + 5],
                )
                self.header_rects[index].topleft = [
                    self.start_pos[0],
                    self.start_pos[1] + dy,
                ]
                dy += self.headers[index].get_height() + self.gap + 10

                if active:
                    if (
                        pg.time.get_ticks() - self.delays[index]
                        > self.duration
                    ):
                        self.delays[index] = pg.time.get_ticks()
                        if self.scroll_incrementing[index] == "+":
                            if self.header_scroll[
                                index
                            ] + 1 <= self.get_n_steps(index):
                                self.header_scroll[index] += 1
                            else:
                                self.scroll_incrementing[index] = "."
                        elif self.scroll_incrementing[index] == "-":
                            if self.header_scroll[index] > 0:
                                self.header_scroll[index] -= 1
                            else:
                                self.scroll_incrementing[index] = "."
                                self.header_active[index] = False

                    for index2, step in enumerate(self.quests_inside[index]):
                        if index2 >= self.header_scroll[index]:
                            break

                        # Check box
                        pg.draw.rect(
                            self.screen,
                            bg_color,
                            [
                                self.start_pos[0],
                                self.start_pos[1] + dy,
                                *self.cross.get_size(),
                            ],
                            width=1,
                        )

                        done = self.quests_inside_done[index][index2]
                        rect = step.get_rect(
                            topleft=[
                                self.start_pos[0] + self.gap_x,
                                self.start_pos[1] + dy,
                            ]
                        )
                        rect.topleft -= pg.Vector2(5, 5)
                        rect.size += pg.Vector2(10, 10)

                        # Smaller headers containing the mission
                        pg.draw.rect(
                            self.screen, header_color, rect, border_radius=8
                        )
                        pg.draw.rect(
                            self.screen,
                            (0, 0, 0),
                            rect,
                            border_radius=8,
                            width=1,
                        )

                        # Mission Completion
                        if done:
                            self.screen.blit(
                                self.cross,
                                (self.start_pos[0], self.start_pos[1] + dy),
                            )
                            self.screen.blit(
                                step,
                                [
                                    self.start_pos[0] + self.gap_x,
                                    self.start_pos[1] + dy,
                                ],
                            )
                            dy += step.get_height() + self.gap
                        else:
                            self.screen.blit(
                                step,
                                [
                                    self.start_pos[0] + self.gap_x,
                                    self.start_pos[1] + dy,
                                ],
                            )
                            dy += step.get_height() + self.gap
                            break  # don't show the next unavailable quest
        else:
            dy = 110
            dx = 10
            for index, text in enumerate(
                self.quest_manager.current_finished_steps
            ):
                render = self.step_font2.render(
                    f"Step completed:  {text}", True, (0, 0, 0)
                )
                rect = render.get_rect(topleft=(dx, dy))
                dy += rect.height + 15
                delay = self.quest_manager.finished_steps_delays[index]
                dt = pg.time.get_ticks() - delay
                if dt < 250:
                    rect.x = -rect.width + rect.width * dt / 250
                elif 250 < dt < 3750:
                    rect.x = dx
                else:
                    rect.x = -rect.width * (dt - 3750) / 250
                new_rect = pg.Rect(
                    rect.topleft - pg.Vector2(5, 5),
                    rect.size + pg.Vector2(10, 10),
                )
                pg.draw.rect(self.screen, bg_color, new_rect, border_radius=6)
                pg.draw.rect(
                    self.screen, (0, 0, 0), new_rect, border_radius=6, width=2
                )
                self.screen.blit(render, rect)
            for index, text in enumerate(self.quest_manager.current_new_steps):
                render = self.step_font2.render(
                    f"New step:  {text}", True, (0, 0, 0)
                )
                rect = render.get_rect(topleft=(dx, dy))
                dy += rect.height + 15
                delay = self.quest_manager.new_steps_delays[index]
                dt = pg.time.get_ticks() - delay
                if dt < 250:
                    rect.x = -rect.width + rect.width * dt / 250
                elif 250 < dt < 3750:
                    rect.x = dx
                else:
                    rect.x = -rect.width * (dt - 3750) / 250
                new_rect = pg.Rect(
                    rect.topleft - pg.Vector2(5, 5),
                    rect.size + pg.Vector2(10, 10),
                )
                pg.draw.rect(self.screen, bg_color, new_rect, border_radius=6)
                pg.draw.rect(
                    self.screen, (0, 0, 0), new_rect, border_radius=6, width=2
                )
                self.screen.blit(render, rect)
