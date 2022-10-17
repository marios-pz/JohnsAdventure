import pygame as pg
from ..PLAYER.player_sub.tools import set_camera_to
from ..levels import play_cutscene
from ..utils import resource_path, l_path
from typing import Any


class CutsceneManager:
    def __init__(self, world_instance: Any):
        # get game manager instance
        self._world = world_instance
        # get screen
        self.screen: pg.Surface = world_instance.DISPLAY
        # get screen's metrics
        self.W, self.H = self.screen.get_size()
        # init font
        self.font = pg.font.Font(
            resource_path("data/database/menu-font.ttf"), 20
        )
        self.font2 = pg.font.Font(
            resource_path("data/database/menu-font.ttf"), 23
        )

        # state
        self.state: str = (
            "inactive"  # "active", "initializing", "inactive", "quiting"
        )
        self.began_state_time = 0

        # cinema bars status
        self.cinema_bar_height = 100
        self.cinema_bars_dy: list[float | int] = [
            -self.cinema_bar_height,
            self.H,
        ]
        self.duration_cinema_bar_loading = 1000
        self.vel_cinema_bars = self.cinema_bar_height / (
            self.duration_cinema_bar_loading / 40
        )

        # ------------------ script

        # global script
        self.current_script: list[dict[str, Any]] = []
        self.began_script = 0  # time the script began
        self.index_script = 0
        self.finished_script = True
        self.ended_since = 0

        # phases
        self.current_phase: dict[str, Any] = {}
        self.continue_phase_until = 0
        self.phase_ended = False

        self.target_pos: tuple[int, int] | pg.Vector2 | None = None
        self.target_zoom: float | None = None
        self.wait_on_end = 0
        self.text = ""
        self.centered_text = ""
        self.next_cam_status: str | None = None
        self.displayed_image: pg.Surface | None = None

        self.delay_text = 0
        self.index_text = 0
        self.text_total_dt = 0
        self.index_ct_text = 0
        self.ct_text_total_dt = 0
        self.delay_ct_text = 0

    def init_script(self, script: list[dict[str, Any]]):
        self.state = "initializing"
        self.began_state_time = pg.time.get_ticks()
        set_camera_to(
            self._world.player.camera, self._world.player.camera_mode, "auto"
        )
        self.current_script = script
        self.began_script = pg.time.get_ticks()
        self.index_script = 0
        self.finished_script = False

        if "pos" in self.current_script[0]:
            self._world.player.camera.method.looking_at = self.current_script[
                0
            ]["pos"]
            self._world.player.camera.method.look_at(
                self.current_script[0]["pos"]
            )
        fov = (
            self.current_script[0]["zoom"]
            if "zoom" in self.current_script[0]
            else 0
        )
        if fov != 0:
            self._world.player.camera.method.start_zoom_out(
                fov, self.duration_cinema_bar_loading + 740
            )

        if "image" in self.current_script[0]:
            self.displayed_image = self.current_script[0]["image"]
            if isinstance(self.displayed_image, str):
                self.displayed_image = l_path(self.displayed_image)

        if "no_init" in self.current_script[0]:
            if self.current_script[0]["no_init"]:
                self.state = "active"
                self.cinema_bars_dy = [0, self.H - self.cinema_bar_height]
                self.init_phase()

    def end_script(self):
        if self.next_cam_status is not None:
            set_camera_to(
                self._world.player.camera,
                self._world.player.camera_mode,
                self.next_cam_status,
            )
            self.next_cam_status = None

        self.began_script = 0
        self.index_script = 0
        self.index_text = 0
        self.finished_script = True
        self.began_state_time = pg.time.get_ticks()
        play_cutscene(self._world.game_state.id)
        self._world.game_state.ended_script = True
        self.state = "inactive"

    def init_phase(self):
        self.current_phase = self.current_script[self.index_script]
        self.began_state_time = pg.time.get_ticks()
        self.state = "active"
        self.phase_ended = False

        # get duration
        duration = self.current_phase.get("duration")
        # check if duration is set
        if duration is None:
            raise KeyError(
                "key 'duration' must be set in the camera script, error occurred on id:",
                self.index_script,
            )
        # set the actual variable of duration
        self.continue_phase_until = pg.time.get_ticks() + duration

        # get the pos the camera has to look at
        self.target_pos = (
            self.current_phase["pos"] if "pos" in self.current_phase else None
        )
        if self.target_pos is not None:
            # initialize the camera movement
            self._world.player.camera.method.go_to(
                self.target_pos, duration=duration
            )

        # get the dt that will be waited at the end of the phase
        self.wait_on_end = (
            self.current_phase["waiting_end"]
            if "waiting_end" in self.current_phase
            else 0
        )

        # get the phase's text
        self.text = (
            self.current_phase["text"] if "text" in self.current_phase else ""
        )
        if self.text != "":
            if "text_dt" not in self.current_phase:
                raise KeyError(
                    "key 'text_dt' must be set in the camera script, text was set without a dt."
                )
            self.text_total_dt = self.current_phase["text_dt"]

        # get centered text
        self.centered_text = (
            self.current_phase["centered_text"]
            if "centered_text" in self.current_phase
            else ""
        )
        if self.centered_text != "":
            if "centered_text_dt" not in self.current_phase:
                raise KeyError(
                    "key 'centered_text_dt' must be set in the camera script..."
                )
            self.ct_text_total_dt = self.current_phase["centered_text_dt"]

        # get the next camera status
        self.next_cam_status = (
            self.current_phase["next_cam_status"]
            if "next_cam_status" in self.current_phase
            else None
        )

        # get displayed image
        if "image" in self.current_phase:
            if isinstance(self.current_phase["image"], pg.Surface):
                self.displayed_image = self.current_phase["image"]
            else:
                self.displayed_image = l_path(self.current_phase["image"])
        else:
            self.displayed_image = None

        if "zoom" in self.current_phase and self.displayed_image is None:
            if "zoom_duration" not in self.current_phase:
                # set directly the fov if the change has not to be seen
                self._world.player.camera.method.fov = self.current_phase[
                    "zoom"
                ]
            else:
                self._world.player.camera.method.start_zoom_out(
                    self.current_phase["zoom"],
                    self.current_phase["zoom_duration"],
                )
        elif self.displayed_image is not None:
            self._world.player.camera.method.fov = 1

    def end_phase(self):
        if self.index_script + 1 < len(self.current_script):
            self.index_script += 1
            self.index_text = 0
            self.index_ct_text = 0
            self.init_phase()
        else:
            self.state = "quiting"
            self.began_state_time = pg.time.get_ticks()

    def render(self):
        if self.state != "inactive":

            if self.state in ["active", "initializing", "quiting"]:
                if self.displayed_image is not None:
                    self.screen.blit(
                        self.displayed_image,
                        self.displayed_image.get_rect(
                            center=(self.W // 2, self.H // 2)
                        ),
                    )

            for i in range(2):  # draw cinema bars
                pg.draw.rect(
                    self.screen,
                    (0, 0, 0),
                    [
                        0,
                        self.cinema_bars_dy[i] + (-15 if not i else 15),
                        self.screen.get_width(),
                        self.cinema_bar_height,
                    ],
                )

            if self.state == "active":
                # draw text
                text_rendering = self.font.render(
                    self.text[: self.index_text], True, (255, 255, 255)
                )
                self.screen.blit(
                    text_rendering,
                    text_rendering.get_rect(
                        center=(
                            self.screen.get_width() // 2,
                            self.cinema_bars_dy[1]
                            + self.cinema_bar_height // 2,
                        )
                    ),
                )
                centered_text_rendering = self.font2.render(
                    self.centered_text[: self.index_ct_text],
                    True,
                    (255, 255, 255),
                )
                self.screen.blit(
                    centered_text_rendering,
                    centered_text_rendering.get_rect(
                        center=(self.W // 2, self.H // 2)
                    ),
                )

    def update(self):

        """self._world.player.camera.method.capture_rect = pg.Rect(0, self.cinema_bars_dy[0] + self.cinema_bar_height,
        self.screen.get_width(),
        self.cinema_bars_dy[1]-self.cinema_bar_height)"""

        if self.state != "inactive":
            if self.state == "initializing":
                self.cinema_bars_dy[0] = (
                    -self.cinema_bar_height
                    + (pg.time.get_ticks() - self.began_state_time)
                    * (
                        self.cinema_bar_height
                        / self.duration_cinema_bar_loading
                    )
                    / 2
                )
                self.cinema_bars_dy[1] = (
                    self.H
                    - (pg.time.get_ticks() - self.began_state_time)
                    * (
                        self.cinema_bar_height
                        / self.duration_cinema_bar_loading
                    )
                    / 2
                )

                if (
                    pg.time.get_ticks() - self.began_state_time
                    > self.duration_cinema_bar_loading + 740
                    and not self._world.player.camera.method.zooming_out
                ):
                    self.init_phase()

            elif self.state == "active":

                if (
                    pg.time.get_ticks() > self.continue_phase_until
                    and not self._world.player.camera.method.moving_cam
                    and not self._world.player.camera.method.zooming_out
                    and not self.phase_ended
                ):
                    self.phase_ended = True
                    self.ended_since = pg.time.get_ticks()

                if len(self.text) != 0:
                    if (
                        pg.time.get_ticks() - self.delay_text
                        > self.text_total_dt / len(self.text)
                    ):
                        if self.index_text + 1 <= len(self.text):
                            self.index_text += 1
                            self.delay_text = pg.time.get_ticks()

                if len(self.centered_text) != 0:
                    if (
                        pg.time.get_ticks() - self.delay_ct_text
                        > self.ct_text_total_dt / len(self.centered_text)
                    ):
                        if self.index_ct_text + 1 <= len(self.centered_text):
                            self.index_ct_text += 1
                            self.delay_ct_text = pg.time.get_ticks()

                if self.phase_ended:
                    if (
                        pg.time.get_ticks() - self.ended_since
                        > self.wait_on_end
                    ):
                        self.end_phase()

            elif self.state == "quiting":

                if pg.time.get_ticks() - self.delay_cinema_bars > 40:
                    self.cinema_bars_dy[0] -= self.vel_cinema_bars
                    self.cinema_bars_dy[1] += self.vel_cinema_bars
                    self.delay_cinema_bars = pg.time.get_ticks()

                if (
                    pg.time.get_ticks() - self.began_state_time
                    > self.duration_cinema_bar_loading + 740
                ):
                    self.end_script()
