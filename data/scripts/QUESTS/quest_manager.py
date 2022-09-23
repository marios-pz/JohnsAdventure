import json
import pygame as pg

from .quest import Quest
from ..utils import resource_path


class QuestManager:

    def __init__(self, game_instance, player):
        self.game_instance = game_instance
        self.player = player

        self.quests: dict[str: Quest] = {}
        self.load_quests()

        self.current_finished_steps = []
        self.finished_steps_delays = []

        self.current_new_steps = []
        self.new_steps_delays = []

        self.pop_up_duration = 4000

    def load_quests(self):
        with open(resource_path("data/scripts/QUESTS/quests.json"), "r") as quests:
            data = json.load(quests)

        for key in data:
            self.quests[key] = Quest(key, data[key]["xp"], self.player)

    def get_current_level_tag(self):
        for tag, state_type in self.game_instance.state_manager.items():
            if type(self.game_instance.game_state) is state_type:
                return tag

    def complete_step(self, quest):
        self.current_finished_steps.append(quest.steps_names[quest.index_step])
        self.finished_steps_delays.append(pg.time.get_ticks())
        quest.complete_step()
        if not quest.finished:
            self.current_new_steps.append(quest.steps_names[quest.index_step])
            self.new_steps_delays.append(pg.time.get_ticks())

    def update_quests(self):

        to_remove = []
        for index, new in enumerate(self.new_steps_delays):
            if pg.time.get_ticks() - new > self.pop_up_duration:
                to_remove.append(self.current_new_steps[index])
        to_remove2 = []
        for index, finished in enumerate(self.finished_steps_delays):
            if pg.time.get_ticks() - finished > self.pop_up_duration:
                to_remove2.append(self.current_finished_steps[index])

        for remove in to_remove:
            self.new_steps_delays.remove(self.new_steps_delays[self.current_new_steps.index(remove)])
            self.current_new_steps.remove(remove)
        for remove2 in to_remove2:
            self.finished_steps_delays.remove(self.finished_steps_delays[self.current_finished_steps.index(remove2)])
            self.current_finished_steps.remove(remove2)

        for quest in self.quests.values():
            if quest.finished:
                continue

            if self.get_current_level_tag() == quest.level_step:
                if quest.type_step == "Reach":
                    self.complete_step(quest)
                elif quest.type_step == "Interact":
                    if self.player.interacting_with.__class__.__name__ == quest.target_step:
                        self.complete_step(quest)
                elif quest.type_step == "Kill":
                    for obj in self.game_instance.game_state.objects:
                        if obj.__class__.__name__ == quest.target_step:
                            break
                    else:
                        self.complete_step(quest)
