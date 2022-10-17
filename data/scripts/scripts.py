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

from .utils import scale, l_path
import pygame

infoObject = pygame.display.Info()

image_surface = pygame.surface.Surface((1280, 720))


PLAYER_ROOM_SCENE = [
    {
        "duration": 4000,
        "image": scale(l_path("data/sprites/cutscenes/cutscene1.png"), 3),
    },
    {
        "no_init": True,
        "duration": 4000,
        "centered_text": "PORTO RAFTH 202X ALTERNATIVE UNIVERSE",
        "centered_text_dt": 2000,
        "image": image_surface,
    },
    {
        "duration": 3000,
        "image": image_surface,
        "centered_text": "A universe, Humans and Monsters lived peacefully.",
        "centered_text_dt": 2000,
        "waiting_end": 1000,
    },
    {
        "duration": 3000,
        "image": image_surface,
        "centered_text": "But.. on this bare day.. the unpredictable happened.",
        "centered_text_dt": 2000,
        "waiting_end": 1000,
    },
    {
        "duration": 3000,
        "image": image_surface,
        "centered_text": "and John's Adventure started.",
        "centered_text_dt": 2000,
        "waiting_end": 1000,
    },
    {
        "duration": 3000,
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
        "waiting_end": 4000,
        "zoom": 1.4,
        "text_dt": 1600,
    },
    {
        "pos": (1100, 225),
        "duration": 1000,
        "waiting_end": 2000,
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
        "duration": 4000,
        "pos": (570, 220),
        "zoom": 1.2,
        "text": "Cynthia: Hello brother. you seem dread. are you alright?",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "pos": (570, 220),
        "text": "Cynthia: Anyway.. Manos is waiting for you in training field",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "pos": (570, 220),
        "text": "Cynthia: I will go meet my friends in school, see you around",
        "text_dt": 1500,
    },
    {
        # Show the door
        "duration": 3000,
        "pos": (620, 600),
    },
    {
        "duration": 1800,
        # Go back to the player
        "zoom": 1,
        "zoom_duration": 1800,
        "pos": (
            570,
            220,
        ),
    },
]


TRAINING_FIELD_SCENE_1 = [
    {"duration": 0, "pos": (1138, 1526), "zoom": 1.2},
    {
        "duration": 3000,
        "text": "Manos: Hello john, are you ready to fight?",
        "text_dt": 1500,
    },
    {"duration": 3000, "text": "Candy: *meow meow* ", "text_dt": 1500},
    {
        "duration": 4500,
        "pos": (1660, 1682),
        "text": "Manos: show me your sword skills in those dummies i've placed.",
        "text_dt": 1500,
    },
    {"duration": 2500},  # show the __static__ dummies
    {
        "duration": 2000,
        "pos": (1138, 1526),
        "zoom": 1,
        "zoom_duration": 1800,
    },
]

TRAINING_FIELD_SCENE_2 = [
    {
        "duration": 3000,
        "text": "Manos: Well done John. now its time for movement-",
        "text_dt": 1500,
    },
    {
        "duration": 1500,  # move at where dummies were
        "pos": (1660, 1682),
    },
    {"duration": 2500},  # at this point, the dummies appear
    {
        "duration": 4000,
        "pos": (1138, 1526),
        "text": "Manos: This purple aura.. It couldn't be HIM.",
        "text_dt": 1200,
    },
    {
        "duration": 4000,
        "pos": (1138, 1526),
        "text": "Manos: I need to go, defeat these monsters!",
        "text_dt": 1200,
    },
    {
        "duration": 4000,
        "pos": (1138, 1526),
        "text": "Manos: and get back Cynthia, I will be in my Hut",
        "text_dt": 1200,
    },
]

GYMNASIUM_SCENE = [
    {
        "duration": 4000,
        "pos": (2762, -75),
        "zoom": 1.2,
        "text": "Alex: John! monsters attacked the area!",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "text": "Alex: A huge monster is roaming the area! you cannot go back",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "text": "Alex: There is a secret spot around here",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "text": "Alex: find it, it will help you go back home through the cave.",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "zoom": 1,
        "text": "Alex: Good luck! hopefully it won't have any monsters.",
        "text_dt": 1500,
    },
]
