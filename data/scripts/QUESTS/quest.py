import json

from ..utils import resource_path
class Quest:

    def __init__(self,
                 name: str,
                 xp_reward: int,
                 player_instance
                 ):

        # ------ QUEST VALUES

        # get the name
        self.name = name
        # track if finished
        self.finished = False
        # track the finished steps
        self.quest_state = {}
        # track the steps themselves
        self.quest_steps = {}

        # load everything
        self.get_quest()

        # track the current step we're in
        self.index_step = sum(self.quest_state.values())
        self.steps_list = list(self.quest_steps.values())
        self.steps_names = list(self.quest_steps.keys())

        # steps
        self.type_step = ""
        self.target_step = ""
        self.level_step = ""
        self.define_steps()

        # ----- REWARDS
        self.xp_reward = xp_reward
        self.player = player_instance

    def get_quest(self):
        """
        Load everything from the json
        """

        with open(resource_path("data/scripts/QUESTS/quests.json"), "r") as quest:
            all_quests = json.load(quest)

        # var to track if finished yet (bool)
        self.finished = all_quests[self.name]["finished"]
        # load the finished/not finished steps of the quest
        self.quest_state = all_quests[self.name]["content"]["completed"]
        # load the quest steps
        self.quest_steps = all_quests[self.name]["content"]["steps"]
        # load the finished variable
        self.finished = all_quests[self.name]["finished"]

    def complete_quest(self):
        """
        Complete the quests, including json manipulations, and xp rewarding
        """
        self.finished = True

        with open(resource_path("data/scripts/QUESTS/quests.json"), "r") as quest:
            datas = json.load(quest)
            datas[self.name]["content"]["completed"] = self.quest_state
            datas[self.name]["finished"] = True
            with open(resource_path("data/scripts/QUESTS/quests.json"), "w") as quest_:
                json.dump(datas, quest_, indent=2)

        self.player.experience += self.xp_reward

    def complete_step(self):
        """
        Called everytime you finish a step
        """
        self.quest_state[list(self.quest_state.keys())[self.index_step]] = True

        with open(resource_path("data/scripts/QUESTS/quests.json"), "r") as quest:
            datas = json.load(quest)
            datas[self.name]["content"]["completed"][self.steps_names[self.index_step]] = True

        with open(resource_path("data/scripts/QUESTS/quests.json"), "w") as quest:
            json.dump(datas, quest, indent=2)

        self.index_step += 1
        self.define_steps()

    def define_steps(self):
        # read the "compressed" step and assign variables according to it
        if self.index_step > len(self.steps_list)-1:
            return self.complete_quest() if not self.finished else None

        for info in self.steps_list[self.index_step].split(" "):
            if "TARGET" in info:
                self.target_step = info.split(":")[-1]
            if "LEVEL" in info:
                self.level_step = info.split(":")[-1]
            if "TYPE" in info:
                self.type_step = info.split(":")[-1]

    def update(self):
        # check if quest is fully finished
        if False not in list(self.quest_state.values()) and not self.finished:
            self.complete_quest()

