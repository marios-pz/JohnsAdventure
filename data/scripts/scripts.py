#
# This place is for cutscenes. Avoid touching it :')
#
# USE THIS BELOW AS A REFERENCE
#
# self.camera_script = [
#
#         # EXAMPLE OF CAMERA SCRIPT THAT INCLUDES EVERY FUNCTIONALITY EXCEPT IMAGE AND CENTERED TEXT
#
#         {
#             "pos": (self.screen.get_width() // 2 - 120, self.screen.get_height() // 2 - 20),
#             "duration": 0,
#             "text": f"Hello Player. Welcome to John's Adventure.",
#             "waiting_end": 2000,
#             "zoom": 1.4,
#             "text_dt": 1000
#         },
#         {
#             "pos": (1100, 225),
#             "duration": 1000,
#             "waiting_end": 2000,
#             "text": "Your quest is waiting for you downstairs.",
#             "text_dt": 1000
#         },
#         {
#             "pos": (self.screen.get_width() // 2 - 120, self.screen.get_height() // 2 - 20),
#             "duration": 750,
#             "waiting_end": 250,
#         },
#         {
#             "duration": 1200,
#             "next_cam_status": "follow",
#             "zoom": 1,
#             "zoom_duration": 1200
#         }
#     ]

from .utils import resource_path, scale, l_path
import pygame

infoObject = pygame.display.Info()

image_surface = pygame.surface.Surface((1280, 720))


with open(resource_path("data/database/data.json")) as f:
    import json

    CONTROLS = json.load(f)
    CONTROLS = CONTROLS["controls"]

PLAYER_ROOM_SCENE = [
    {
        "duration": 3000,
        "image": scale(l_path("data/sprites/cutscenes/cutscene1.png"), 3),
    },
    {
        "no_init": True,
        "duration": 3000,
        "centered_text": "PORTO RAFTI 202X ALTERNATIVE UNIVERSE",
        "centered_text_dt": 2000,
        "image": image_surface,
    },
    {
        "duration": 2000,
        "image": image_surface,
        "centered_text": "A universe, Humans and Monsters lived peacefully.",
        "centered_text_dt": 2000,
        "waiting_end": 1000,
    },
    {
        "duration": 2000,
        "image": image_surface,
        "centered_text": "But on this day the unpredictable happend.",
        "centered_text_dt": 2000,
        "waiting_end": 1000,
    },
    {
        "duration": 2000,
        "image": image_surface,
        "centered_text": "and John's Adventure started.",
        "centered_text_dt": 2000,
        "waiting_end": 1000,
    },
    {
        "duration": 2000,
        "image": image_surface,
        "centered_text": "C.. Cynthia!",
        "centered_text_dt": 2000,
        "waiting_end": 1000,
    },
    {
        "pos": (
            infoObject.current_w // 2 - 120,
            infoObject.current_h // 2 - 20,
        ),
        "duration": 0,
        "text": "Man. what a dream.",
        "waiting_end": 3000,
        "zoom": 1.4,
        "text_dt": 1600,
    },
    {
        "pos": (1100, 225),
        "duration": 1000,
        "waiting_end": 1000,
        "text": "I better check on her.",
        "text_dt": 1600,
    },
    {
        "pos": (
            infoObject.current_w // 2 - 120,
            infoObject.current_h // 2 - 20,
        ),
        "duration": 750,
        "waiting_end": 250,
    },
    {
        "duration": 1200,
        "next_cam_status": "follow",
        "zoom": 1,
        "zoom_duration": 1200,
    },
]

KITCHEN_SCENE = [
    {
        "duration": 2500,
        "pos": (570, 220),
        "zoom": 1.2,
        "text": "Cynthia: Hello brother.",
        "text_dt": 1500,
    },
    {"duration": 500},
    {
        "duration": 3000,
        "pos": (570, 220),
        "text": "Cynthia: You seem dread. are you alright?",
        "text_dt": 1500,
    },
    {"duration": 500},
    {
        "duration": 3000,
        "pos": (570, 220),
        "text": "John: I had a very weird nightmare.",
        "text_dt": 1500,
    },
    {"duration": 500},
    {
        # Show the door
        "duration": 3000,
        "pos": (620, 600),
        "text": "Cynthia: Anyway.. Manos is waiting for you in the training field",
        "text_dt": 1800,
    },
    {
        "duration": 1300,
        # Go back to the player
        "zoom": 1,
        "zoom_duration": 1500,
        "pos": (
            570,
            220,
        ),
    },
    {
        "duration": 4000,
        "pos": (570, 220),
        "text": "Cynthia: I will go meet my friends in school",
        "text_dt": 1800,
    },
    {"duration": 500},
    {
        "duration": 4000,
        "pos": (570, 220),
        "text": "Cynthia: See you around",
        "text_dt": 1800,
    },
    {"duration": 500},
]


MANOS_HUT_SCENE = [
    {
        "duration": 4000,
        "pos": (235 * (1280 / 453), 115 * (720 / 271)),
        "zoom": 1.2,
        "text": "Manos: John! Why did you took so long?",
        "text_dt": 1500,
    },
    {
        "duration": 3000,
        "text": "John: The passage was blocked by monsters ",
        "text_dt": 1500,
    },
    {
        "duration": 3000,
        "text": "John: I made it through the caves to get here.",
        "text_dt": 1500,
    },
    {
        "duration": 3000,
        "text": "John: The monsters took Cynthia, we got to get her back.",
        "text_dt": 1500,
    },
    {
        "duration": 3000,
        "text": "John: Care to explain the situation?",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "text": "Manos: I think I know who did it John.",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "text": "Manos: This aura is no one else's but my old nemesis Alcemenos",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "text": "Manos: There is a good chance he is using his old base.",
        "text_dt": 1500,
    },
    {
        "duration": 3000,
        "zoom": 1,
        "text": "Manos: We must go to Porto Rafti before the sun goes down.",
        "text_dt": 1500,
    },
]

TRAINING_FIELD_SCENE_1 = [
    {"duration": 0, "pos": (1138, 1526), "zoom": 1.2},
    {
        "duration": 3000,
        "text": "Manos: Hey John ready for your usual training?",
        "text_dt": 1500,
    },
    {
        "duration": 2000,
        "text": "John: I sure am",
        "text_dt": 1200,
    },
    {"duration": 3000, "text": "Candy: *meow meow* ", "text_dt": 1500},
    {
        "duration": 3000,
        "pos": (1660, 1682),
        "text": "Manos: good, pick up your sword from the chest",
        "text_dt": 1500,
    },
    {
        "duration": 3000,
        "pos": (1660, 1682),
        "text": "Manos: show me your skills in those dummies",
        "text_dt": 1500,
    },
    {"duration": 2500},  # show the __static__ dummies
    {
        "duration": 2000,
        "pos": (1138, 1526),
        "zoom": 1,
        "zoom_duration": 1800,
    },
    {
        "duration": 2000,
        "text": "(HINT: Press Left Click to attack)",
        "text_dt": 1500,
    },
    {"duration": 500},
]

TRAINING_FIELD_SCENE_2 = [
    {
        "duration": 3000,
        "text": "Manos: Good! you're getting better!",
        "text_dt": 1500,
        "waiting_end": 500,
    },
    {
        "duration": 4000,
        "text": f"(HINT: you can press {pygame.key.name(CONTROLS['inventory'])} to check your inventory!)",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "text": "(HINT: you can also upgrade your stats in there!)",
        "text_dt": 1500,
    },
    {
        "duration": 1300,  # move at where dummies were
        "pos": (1660, 1682),
    },
    {"duration": 2500},  # at this point, the dummies appear
    {
        "duration": 3000,
        "pos": (1138, 1526),
        "text": "Manos: This purple aura.. It couldn't be HIM.",
        "text_dt": 1500,
    },
    {
        "duration": 3000,
        "pos": (1138, 1526),
        "text": "Manos: Oh no.. Quickly defeat those monsters",
        "text_dt": 1500,
    },
    {
        "duration": 3000,
        "pos": (1138, 1526),
        "text": "Manos: I need to go to equip my stuff",
        "text_dt": 1500,
    },
    {
        "duration": 2500,
        "text": f"(HINT: You can press {pygame.key.name(CONTROLS['dash'])} to Dash!)",
        "text_dt": 1500,
    },
    {
        "duration": 7000,
        "pos": (1138, 1526),
        "text": "Manos: Don't forget to get cynthia as soon as you can! she might be in danger",
        "text_dt": 1300,
    },
    {
        "duration": 3500,
        "pos": (1138, 1526),
        "text": "Manos: Then meet my at my hut",
        "text_dt": 1500,
    },
]

GYMNASIUM_SCENE = [
    {
        "duration": 3000,
        "pos": (2762, -75),
        "zoom": 1.2,
        "text": "Alexia: John! monsters kidnapped Cynthia but I managed to run away!",
        "text_dt": 1300,
    },
    {
        "duration": 3000,
        "text": "John: Oh no! where did they took her?",
        "text_dt": 1300,
    },
    {
        "duration": 3000,
        "text": "Alexia: Several monsters are roaming the area!",
        "text_dt": 1300,
    },
    {
        "duration": 3000,
        "text": "Alexia: You cannot go back",
        "text_dt": 1300,
    },
    {
        "duration": 3000,
        "text": "Alexia: There is a secret spot around here",
        "text_dt": 1300,
    },
    {
        "duration": 3000,
        "text": "Alexia: find it, it will help you go back home through the cave.",
        "text_dt": 1300,
    },
    {
        "duration": 3000,
        "zoom": 1,
        "text": "Alexia: Good luck! hopefully it won't have any monsters.",
        "text_dt": 1300,
    },
]


CAVE_GARDEN_SCENE = [
    {
        "duration": 4000,
        "pos": (2080, 2800),
        "text": "John: well that was.. dangerous.",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "pos": (2080, 2800),
        "text": "John: Hmm? what is that?",
        "text_dt": 1500,
    },
    {
        "duration": 3000,
        "pos": (2900, 2800),  # enemy position
        "zoom": 1.2,
    },
    {
        "duration": 4200,
        # Go back to the player
        "zoom": 1,
        "zoom_duration": 1800,
        "text": "John: Oh no!",
        "text_dt": 1500,
        "pos": (
            2080,
            2800,
        ),
    },
]
