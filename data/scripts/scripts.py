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
        "duration": 3000,
        "pos": (570, 220),
        "zoom": 1.2,
        "text": "Cynthia: Hello brother. you seem dread. are you alright?",
        "text_dt": 1600,
    },
    {
        "duration": 2000,
        "pos": (570, 220),
        "text": "Cynthia: Anyway.. Manos is waiting for you in the training field",
        "text_dt": 1600,
    },
    {
        "duration": 2000,
        "pos": (570, 220),
        "text": "Cynthia: I will go meet my friends in school, see you around",
        "text_dt": 1600,
    },
    {
        # Show the door
        "duration": 2000,
        "pos": (620, 600),
    },
    {
        "duration": 1600,
        # Go back to the player
        "zoom": 1,
        "zoom_duration": 1500,
        "pos": (
            570,
            220,
        ),
    },
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
        "duration": 4000,
        "text": "John: The passage was blocked by monsters and I made it through the caves to get here.",
        "text_dt": 1500,
    },
    {
        "duration": 4000,
        "text": "John: The monsters took Cynthia, we got to get her back. Care to explain the situation?",
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
        "duration": 4000,
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
    {"duration": 3000, "text": "Candy: *meow meow* ", "text_dt": 1500},
    {
        "duration": 4500,
        "pos": (1660, 1682),
        "text": "Manos: good, pick up your sword from the chest and show me your skills in those dummies that i've placed",
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
        "text": "(GAME: you can press Shift to Dash!)",
        "text_dt": 1500,
    },
    {
        "duration": 2000,
        "text": "(GAME: you can press Q to Heal!)",
        "text_dt": 1500,
    },
]

TRAINING_FIELD_SCENE_2 = [
    {
        "duration": 3000,
        "text": "Manos: Good! you're getting better!",
        "text_dt": 1500,
        "waiting_end": 500,
    },
    {
        "duration": 2000,
        "text": "(GAME: you can press E to check your inventory!, you can also upgrade your stats!)",
        "text_dt": 1500,
    },
    {
        "duration": 1300,  # move at where dummies were
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
        "text": "Manos: Oh no.. Quickly defeat those monsters and meet me at my house, Quickly! I need to go to equip my stuff",
        "text_dt": 1200,
    },
    {
        "duration": 4000,
        "pos": (1138, 1526),
        "text": "Manos: I'll see you in my Hut, don't forget to get cynthia as soon as you can! she might be in danger",
        "text_dt": 1200,
    },
]

GYMNASIUM_SCENE = [
    {
        "duration": 3000,
        "pos": (2762, -75),
        "zoom": 1.2,
        "text": "Alexia: John! monsters kidnapped Cynthia but I managed to run away!",
        "text_dt": 1500,
    },
    {
        "duration": 3000,
        "text": "Alexia: Several monsters are roaming the area! you cannot go back",
        "text_dt": 1600,
    },
    {
        "duration": 3000,
        "text": "Alexia: There is a secret spot around here",
        "text_dt": 1600,
    },
    {
        "duration": 3000,
        "text": "Alexia: find it, it will help you go back home through the cave.",
        "text_dt": 1600,
    },
    {
        "duration": 3000,
        "zoom": 1,
        "text": "Alexia: Good luck! hopefully it won't have any monsters.",
        "text_dt": 1600,
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


CAVE_PASSAGE_SCENE = [
    {
        "zoom": 1.3,
        "duration": 3000,
        "pos": (2080, 2800),
        "text": "John: What are these monsters..",
        "text_dt": 1500,
    },
    {
        "duration": 4200,
        "zoom": 1,
        "zoom_duration": 1800,
        "text": "John: Time to go cyberpunk",
        "text_dt": 1500,
        "pos": (
            2080,
            2800,
        ),
    },
]
