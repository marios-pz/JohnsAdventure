import pygame
from .PLAYER.player import Player
from .sound_manager import SoundManager
from .UI.mainmenu import Menu
from .UI.interface import Interface
from .UI.loading_screen import LoadingScreen
from .UI.pause_menu import PauseMenu
from .utils import (
    init_pause,
    resource_path,
    l_path,
    UI_Spritesheet,
    smooth_scale,
)

from .utils import scale
from copy import copy
from .QUESTS.quest_manager import QuestManager
from .QUESTS.quest_ui import QuestUI
from .props import PropGetter, init_sheets, del_sheets
from threading import Thread
from .POSTPROCESSING.cutscene_engine import CutsceneManager
from math import floor
from .AI.enemy import Enemy
from .debugging import Debugging
from .levels import (
    Gymnasium,
    GameState,
    PlayerRoom,
    Kitchen,
    JohnsGarden,
    ManosHut,
    Training_Field,
    CaveGarden,
    CaveEntrance,
    CaveRoomPassage,
    Credits,
)

# Your lsp might think the below are unused, but thats wrong.
from .PLAYER.inventory import Inventory
from typing import Any
from .PLAYER.player_sub.tools import set_camera_to
from .PLAYER.player_sub.animation_handler import user_interface
from .levels import get_cutscene_played, play_cutscene

TITLE_TRANSLATOR = {
    "player_room": "John's Room",
    "johns_garden": "Open World",
    "training_field": "Training Field",
    "gymnasium": "Gymnasium",
    "kitchen": "John's Kitchen",
    "manos_hut": "Mano's hut",
    "cave_garden": "Cave Garden",
    "cave_entrance": "Cave Entrance",
    # "cave_room_1": "C-Floor 1",
    # "cave_room_2": "C-Floor 2",
    "cave_passage": "Cave Passage",
}


class GameManager:
    """

    Game class -> handles everything of the game.

    """

    def __init__(
        self,
        debug: bool = False,
        first_state: str = "player_room",
        no_rect: bool = False,
    ):

        pygame.init()

        pygame.event.set_allowed(
            [
                pygame.QUIT,
                pygame.KEYDOWN,
                pygame.KEYUP,
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEWHEEL,
                pygame.MOUSEBUTTONUP,
            ]
        )

        # FONTS
        pygame.mixer.pre_init(
            44100, 32, 2, 4096
        )  # Frequency, 32 Bit sound, channels, buffer
        pygame.display.set_caption("iBoxStudio Engine")

        # | pygame.DOUBLEBUF | pygame.SCALED | pygame.FULLSCREEN

        self.DISPLAY: pygame.surface.Surface = pygame.display.set_mode(
            (1280, 720),
            flags=pygame.SRCALPHA | pygame.HWSURFACE | pygame.RESIZABLE,
        )

        pygame.display.set_icon(l_path("data/ui/logo.png", True))

        self.W: int = self.DISPLAY.get_width()
        self.H: int = self.DISPLAY.get_height()

        self.FPS = 55

        # ------------- SPRITESHEET ---------------
        self.ui = UI_Spritesheet("data/ui/UI_spritesheet.png")

        # ------------ FRAMERATE ------------------
        self.framerate = pygame.time.Clock()
        self.dt = self.framerate.tick(self.FPS) / 1000

        # ----------- GAME STATE VARIABLES --------
        self.menu = True
        self.loading = False
        self.death_screen = False

        #
        self.font = pygame.font.Font(
            resource_path("data/database/menu-font.ttf"), 24
        )

        # (main menu title)
        self.blacksword = pygame.font.Font(
            resource_path("data/database/Blacksword.otf"), 113
        )

        # pygame powered
        self.pygame_logo = l_path(
            "data/sprites/pygame_powered.png", alpha=True
        )
        self.start_logo_time = pygame.time.get_ticks()
        self.pg_logo = False
        self.start_scale = 1
        self.current_scale = 0
        self.delay_scaling = 0

        # ---------- GAME MANAGERS ----------------
        self.sound_manager: SoundManager = SoundManager(False, True)
        self.sound_manager.play_music("city_theme")

        self.loading_screen: LoadingScreen = LoadingScreen(self.DISPLAY)
        self.menu_manager: Menu = Menu(self, self.blacksword, self.ui)
        self.interface: Interface = Interface(
            self.DISPLAY,
            scale(self.ui.parse_sprite("interface_button.png"), 8),
        )
        self.pause_menu: PauseMenu = PauseMenu(self.DISPLAY, self.ui)

        # ------------- PLAYER ----------------
        self.player = Player(
            self,
            self.DISPLAY,  # Screen surface
            self.font,  # Font
            self.interface,
            self.ui,  # Other UI like Inventory
            self.menu_manager.save,  # controls
        )
        self.last_player_instance: Player | None = copy(self.player)
        self.last_loaded_states: dict[str, GameState] = {}
        self.last_game_state_tag: str = first_state
        self.last_game_state: GameState | None = None
        self.last_positions: dict[int, tuple[int, int]] = {}

        # ----------- GAME STATE ------------------
        self.state: str = first_state
        self.first_state: bool = False
        self.prop_objects = PropGetter(self.player).PROP_OBJECTS

        # THIS IS WHERE YOU LOAD THE WORLDS
        self.state_manager = {
            "player_room": PlayerRoom,
            "kitchen": Kitchen,
            "johns_garden": JohnsGarden,
            "manos_hut": ManosHut,
            "training_field": Training_Field,
            "gymnasium": Gymnasium,
            "cave_garden": CaveGarden,
            "cave_entrance": CaveEntrance,
            # "cave_room_1": CaveRoomOne,
            # "cave_room_2": CaveRoomTwo,
            "cave_passage": CaveRoomPassage,
            "credits": Credits,
        }
        self.loaded_states: dict[str, GameState] = {}
        self.game_state: GameState | None = None

        # ------------ DEBUG ----------------------
        self.debug = debug
        self.debugger: Debugging = Debugging(self, no_rect)

        # -------- CAMERA SRC HANDLER -------------
        self.cutscene_engine: CutsceneManager = CutsceneManager(self)

        # ------------- QUESTS -------------------
        self.quest_manager: QuestManager = QuestManager(self, self.player)

        self.quest_UI: QuestUI = QuestUI(self, self.quest_manager)

        self.player.quest_UI = self.quest_UI

        # ------------- DEATH SCREEN --------------
        self.begin_end_screen = 0
        # layer + bg
        self.end_game_bg = self.DISPLAY.copy()
        self.black_layer = pygame.Surface(self.DISPLAY.get_size())
        self.black_layer.set_alpha(200)

        # text + font
        self.title_font = pygame.font.Font(
            resource_path("data/database/menu-font.ttf"), 75
        )
        self.subtitle_font = pygame.font.Font(
            resource_path("data/database/menu-font.ttf"), 15
        )
        self.end_game_ui_texts = [
            self.title_font.render("DEATH", True, (255, 0, 0)),
            self.subtitle_font.render(
                f"Press {pygame.key.name(self.player.data['controls']['interact'])} "
                f"to respawn.",
                True,
                (255, 255, 255),
            ),
        ]
        self.end_game_ui_rects = [
            self.end_game_ui_texts[0].get_rect(
                center=(self.W // 2, self.H // 2)
            ),
            self.end_game_ui_texts[1].get_rect(
                center=(self.W // 2, self.H * 3 / 4)
            ),
        ]

        # ------------ NEW LEVEL POPUP ----------------
        self.begin_new_level_popup = 0
        self.falling_duration = 750
        self.fade_duration = 500
        self.standing_duration = 1500
        # font
        self.new_level_font = pygame.font.Font(
            resource_path("data/database/menu-font.ttf"), 30
        )
        self.new_level_popup = self.new_level_font.render(
            TITLE_TRANSLATOR[self.state], True, (255, 255, 255)
        )
        self.new_level_popup_rect = self.new_level_popup.get_rect(
            centerx=self.W // 2, bottom=0
        )
        self.popup_target_y = self.new_level_popup.get_height() - 10
        # booleans
        self.showing_nl_popup = False

    def pause(self):
        if self.player.paused:
            init_pause(self.W, self.H, self.DISPLAY)
            while True:
                upd = self.pause_menu.update()

                if upd == "quit":
                    self.menu = True
                    self.player.paused = False
                    self.menu_manager.start_game = False
                    break
                elif upd == "resume":
                    self.player.paused = False
                    break

                pygame.display.update()

    def routine(self):

        """Method called every frame of the game.
        (Created to simplify the game loop)"""

        self.dt = self.framerate.tick(self.FPS) / 1000

        if (
            not self.menu and not self.loading and not self.death_screen
        ):  # if the game is playing
            if self.state != "credits":
                user_interface(
                    self.player,
                    pygame.mouse.get_pos(),
                    (
                        # 52 48 are players height and width
                        self.player.rect.x - 52 - self.player.camera.offset.x,
                        self.player.rect.y - self.player.camera.offset.y - 48,
                    ),
                    self.dt,  # <- is needed for the NPC interaction
                )
            self.pause()
            if hasattr(self.player.camera.method, "fov"):
                if self.player.camera.method.fov != 1:
                    surface = self.DISPLAY.subsurface(
                        self.player.camera.method.capture_rect
                    )
                    surface = smooth_scale(
                        surface, self.player.camera.method.fov
                    )
                    self.DISPLAY.blit(
                        surface,
                        surface.get_rect(
                            center=(
                                self.DISPLAY.get_width() // 2,
                                self.DISPLAY.get_height() // 2,
                            )
                        ),
                    )
            self.cutscene_engine.render()
            self.quest_manager.update_quests()

            if self.showing_nl_popup:
                self.DISPLAY.blit(
                    self.new_level_popup, self.new_level_popup_rect
                )
                time_elapsed = (
                    pygame.time.get_ticks() - self.begin_new_level_popup
                )
                if time_elapsed < self.falling_duration:
                    self.new_level_popup_rect.y = (
                        self.popup_target_y / self.falling_duration
                    ) * time_elapsed
                elif (
                    self.falling_duration
                    < time_elapsed
                    < self.standing_duration
                ):
                    pass
                elif (
                    time_elapsed
                    > self.standing_duration
                    + self.falling_duration
                    + self.fade_duration
                ):
                    self.showing_nl_popup = False
                else:
                    self.new_level_popup.set_alpha(
                        floor(
                            255
                            - 255
                            * (
                                time_elapsed
                                - self.falling_duration
                                - self.standing_duration
                            )
                            / self.fade_duration
                        )
                    )

        if self.debug:
            self.debugger.update()

        pygame.display.update()

    def pg_loading_screen(self):
        while pygame.time.get_ticks() < 3000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_()

            self.DISPLAY.fill((255, 255, 255))

            if (
                pygame.time.get_ticks() - self.delay_scaling > 25
                and self.start_scale - self.current_scale > 0.75
            ):
                self.delay_scaling = pygame.time.get_ticks()
                self.current_scale += 0.1

            scale_ = self.start_scale - self.current_scale

            img = scale(self.pygame_logo, scale_)
            self.DISPLAY.blit(
                img, img.get_rect(center=(self.W // 2, self.H // 2))
            )

            if pygame.time.get_ticks() - self.start_logo_time > 700:
                self.DISPLAY.blit(
                    self.font.render(
                        "@Copyright Logo by www.pygame.org", True, (0, 0, 0)
                    ),
                    img.get_rect(
                        topleft=(self.W // 2 - 320, self.H // 2 + 230)
                    ),
                )

            self.framerate.tick(self.FPS)
            pygame.display.update()

    def quit_(self):
        for key, level in self.loaded_states.items():
            for obj in level.objects:
                if hasattr(obj, "end_instance"):
                    obj.end_instance()
        for obj in self.game_state.objects:
            if hasattr(obj, "end_instance"):
                obj.end_instance()
        pygame.quit()
        raise SystemExit

    def start_new_level(
        self, level_id, last_state="none", first_pos=None, respawn=False
    ):

        if level_id == "credits":
            self.player.UI_interaction_anim.clear()
            self.state = "credits"
            self.game_state = self.state_manager["credits"](
                self.DISPLAY, self.player, self.prop_objects
            )
            return

        if self.game_state is not None:
            self.loaded_states[self.game_state.id] = self.game_state

        # load all the sheets (to delete them afterwards)
        init_sheets()

        if not respawn:
            if last_state != "none":
                self.last_game_state_tag = last_state
            if self.game_state is not None:
                self.last_game_state = copy(self.game_state)
                self.last_positions = {}
                for obj_ in self.game_state.objects:
                    if not isinstance(obj_, pygame.Rect):
                        self.last_positions[id(obj_)] = copy(obj_.rect.topleft)
                    else:
                        self.last_positions[id(obj_)] = copy(obj_.topleft)
                must_store_begin_pos = False
            else:
                must_store_begin_pos = True

            self.last_player_instance = copy(self.player)
            self.last_loaded_states = copy(self.loaded_states)

        # print(self.last_player_instance, self.last_game_state_tag, self.last_loaded_states)
        # print(self.player, self.state, self.loaded_states)

        def load_new_level(parent, level_):
            parent.game_state = (
                parent.state_manager[level_](
                    parent.DISPLAY, parent.player, parent.prop_objects
                )
                if level_ not in parent.loaded_states
                else parent.loaded_states[level_]
            )

        loading_thread = Thread(target=load_new_level, args=(self, level_id))
        loading_thread.start()

        start = (
            pygame.time.get_ticks()
        )  # time to start (track the loading screen duration)
        self.state = level_id  # update the current state to the next one
        self.player.UI_interaction_anim.clear()  # empty the UI animations
        load_type = [
            "loading..." if first_pos is None else "main_loading",
            750,
        ]  # [load_type, duration]
        self.loading_screen.init(
            load_type[0], duration=load_type[1]
        )  # initialize the loading screen
        run_loading = True
        while run_loading:
            # check if loading screen has to be ended
            is_load_alive = (
                loading_thread.is_alive()
                or pygame.time.get_ticks() - start < load_type[1]
            )

            # don't ask for a key if it's just an in-between level loading. (just exit the loading)
            if not is_load_alive and load_type[0] == "loading...":
                run_loading = False

            # ask for a key to end the loading screen
            load_type[0] = "ended" if not is_load_alive else load_type[0]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    del loading_thread  # quit the thread
                    self.quit_()
                elif (
                    event.type == pygame.KEYDOWN
                ):  # ask for a key to leave the loading
                    if (
                        event.key == self.loading_screen.get_key()
                        and not is_load_alive
                    ):
                        run_loading = False
            self.DISPLAY.fill((0, 0, 0))  # draw background
            self.loading_screen.draw(
                self.DISPLAY, load_type[0]
            )  # draw loading screen (according to load_type)
            pygame.display.update()

        if last_state == "none":  # update pos according to spawn points
            keys = [key for key in self.game_state.spawn]
            self.player.rect.topleft = self.game_state.spawn[keys[0]]
        else:
            self.player.rect.topleft = self.game_state.spawn[last_state]

        # replace the player for the cutscene (if needed)
        if first_pos is not None and not self.debug:
            self.player.rect.topleft = first_pos
            self.first_state = True

        # load all the lights in the game
        self.game_state.lights_manager.init_level(self.game_state)
        # unload the sheets (theoretically supposed to save RAM)
        del_sheets()
        # stop the player from moving
        self.player.Left = (
            self.player.Right
        ) = self.player.Up = self.player.Down = False

        self.new_level_popup = self.new_level_font.render(
            TITLE_TRANSLATOR[self.state], True, (255, 255, 255)
        )
        self.new_level_popup_rect = self.new_level_popup.get_rect(
            centerx=self.W // 2, bottom=0
        )
        self.begin_new_level_popup = pygame.time.get_ticks()
        self.showing_nl_popup = True

        if not respawn:
            if must_store_begin_pos:
                self.last_positions = {}
                for obj_ in self.game_state.objects:
                    if not isinstance(obj_, pygame.Rect):
                        self.last_positions[id(obj_)] = copy(obj_.rect.topleft)
                    else:
                        self.last_positions[id(obj_)] = copy(obj_.topleft)

    def respawn(self):
        self.player.rect = self.last_player_instance.rect
        self.player.xp = self.last_player_instance.xp
        self.player.experience = self.last_player_instance.experience
        self.player.inventory = self.last_player_instance.inventory
        self.player.health_target = self.last_player_instance.health_target
        self.player.health_ratio = self.last_player_instance.health_ratio
        self.player.health = self.last_player_instance.health
        self.loaded_states = copy(self.last_loaded_states)
        if self.last_game_state_tag in self.loaded_states:
            self.player.rect.topleft = self.loaded_states[
                self.last_game_state_tag
            ].spawn[self.state]
            self.game_state = self.loaded_states[self.last_game_state_tag]
            self.state = self.last_game_state_tag
        else:
            self.player.camera_status = "follow"
            self.start_new_level(
                self.state,
                first_pos=(
                    self.DISPLAY.get_width() // 2 - 120,
                    self.DISPLAY.get_height() // 2 - 20,
                ),
                respawn=True,
            )
        for obj_ in self.game_state.objects:
            if id(obj_) in self.last_positions:
                if isinstance(obj_, pygame.Rect):
                    obj_.topleft = self.last_positions[id(obj_)]
                else:
                    if isinstance(obj_, Enemy):
                        obj_.x, obj_.y = self.last_positions[id(obj_)]
                    else:
                        obj_.rect.topleft = self.last_positions[id(obj_)]
        self.death_screen = False

    def init_death_screen(self):
        self.begin_end_screen = pygame.time.get_ticks()
        self.black_layer.set_alpha(0)
        self.end_game_ui_texts[0].set_alpha(0)

    def update(self):

        if not self.debug:
            self.pg_loading_screen()
        else:
            self.start_new_level(
                self.state,
                first_pos=(
                    self.DISPLAY.get_width() // 2 - 120,
                    self.DISPLAY.get_height() // 2 - 20,
                ),
            )
            self.menu = False
            self.loading = False

        while True:

            # if the credits are playing, the player doesn't get updated, so the controls aren't checked, and
            # the quit event must be detected
            if self.state == "credits":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        raise SystemExit
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            raise SystemExit

            if self.menu:  # menu playing

                self.menu_manager.update(pygame.mouse.get_pos())

                if self.menu_manager.start_game:  # start the game
                    self.menu = False
                    self.loading = False

                    self.start_new_level(
                        self.state,
                        first_pos=(
                            (
                                self.DISPLAY.get_width() // 2 - 120,
                                self.DISPLAY.get_height() // 2 - 20,
                            )
                            if not self.first_state
                            else None
                        ),
                    )

            elif self.death_screen:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit_()

                    if event.type == pygame.KEYDOWN:
                        if (
                            event.key
                            == self.player.data["controls"]["interact"]
                        ):
                            self.respawn()
                            self.player.health = self.player.maximum_health

                self.black_layer.set_alpha(
                    floor(
                        (200 / 1500)
                        * (pygame.time.get_ticks() - self.begin_end_screen)
                    )
                )
                self.end_game_ui_texts[0].set_alpha(
                    floor(
                        (255 / 1500)
                        * (pygame.time.get_ticks() - self.begin_end_screen)
                    )
                )
                if pygame.time.get_ticks() - self.begin_end_screen > 1500:
                    self.black_layer.set_alpha(200)
                    self.end_game_ui_texts[0].set_alpha(255)

                self.DISPLAY.fill((0, 0, 0))
                self.DISPLAY.blit(self.end_game_bg, (0, 0))
                self.DISPLAY.blit(self.black_layer, (0, 0))
                self.DISPLAY.blit(
                    self.end_game_ui_texts[0], self.end_game_ui_rects[0]
                )
                if (
                    floor(pygame.time.get_ticks() / 1000) % 2 == 0
                    and self.black_layer.get_alpha() == 200
                ):
                    self.DISPLAY.blit(
                        self.end_game_ui_texts[1], self.end_game_ui_rects[1]
                    )

            else:

                self.DISPLAY.fill((0, 0, 0))
                update = self.game_state.update(self.player.camera, self.dt)
                if update is not None:  # if a change of state is detected

                    if self.state == "manos_hut" and update == "johns_garden":
                        if self.player.game_instance.quest_manager.quests[
                            "A new beginning"
                        ].quest_state["Reach Manos in his hut"]:
                            update = "credits"

                    self.start_new_level(update, last_state=self.state)

                """  RUN THE CAMERA ONLY WHEN ITS NOT IN DEBUGGING MODE  """
                if not self.debug and self.cutscene_engine.state != "inactive":
                    self.cutscene_engine.update()
                    self.FPS = 360
                elif not self.debug:
                    set_camera_to(
                        self.player.camera, self.player.camera_mode, "follow"
                    )

                    if (
                        not self.game_state.ended_script
                        and len(self.game_state.camera_script) > 0
                    ):
                        self.cutscene_engine.init_script(
                            self.game_state.camera_script
                        )

                    self.FPS = 55
                else:
                    set_camera_to(
                        self.player.camera, self.player.camera_mode, "follow"
                    )

                if self.player.health <= 0:
                    self.death_screen = True
                    self.end_game_bg = self.DISPLAY.copy()
                    self.init_death_screen()
                    self.player.health = (
                        self.player.backup_hp
                    )  # Return full hp

            print(self.framerate.get_fps())
            print(self.player.rect.topleft)

            self.routine()
