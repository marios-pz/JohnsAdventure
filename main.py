#

#    Welcome to John's Adventure! Hope you like my new game!
#
#    Please be patient with some pieces of the code, it will take some time to clean the code ;')
#


import sys

if not sys.platform in ["emscripten"]:
    import pygame as pg
    import threading

    from data.scripts.world import main, GameManager


    if __name__ == "__main__":
        game_instance = main()
        game_instance.update()
else:
    import pygame
    import asyncio

    import data.scripts.world
    from data.scripts.utils import l_path, scale


    class Main(data.scripts.world.GameManager):

        pygame.init()


        if not sys.platform in ["emscripten"]:
            pygame.mixer.pre_init(44100, 32, 2, 4096)  # Frequency, 32 Bit sound, channels, buffer

        pygame.display.set_caption("iBoxStudio Engine")
        pygame.mouse.set_visible(False)

        # CONSTS

        DISPLAY = pygame.display.set_mode((1280, 720), flags=pygame.SRCALPHA)

        pygame.display.set_icon(l_path("data/ui/logo.png", True))
        W, H = DISPLAY.get_size()

        FPS = 55

        def state_quit(self):
            self.quit_()
            self.loop_state = None

        def state_loading(self, events):
            if pygame.time.get_ticks() > 6000:
                self.loop_state = self.state_game
                return

            self.DISPLAY.fill((255, 255, 255))

            if pygame.time.get_ticks() - self.delay_scaling > 25 and self.start_scale - self.current_scale > 0.75:
                self.delay_scaling = pygame.time.get_ticks()
                self.current_scale += 0.1

            scale_ = self.start_scale - self.current_scale
            img = scale(self.pygame_logo, scale_)
            self.DISPLAY.blit(img, img.get_rect(center=(self.W // 2, self.H // 2)))

            if pygame.time.get_ticks() - self.start_logo_time > 700:
                self.DISPLAY.blit(
                    self.font.render("@Copyright Logo by www.pygame.org", True, (0, 0, 0)),
                    img.get_rect(topleft=(self.W // 2 - 320, self.H // 2 + 230)),
                )

            self.framerate.tick(self.FPS)


        def start_new_level(self, level_id, last_state="none", first_pos=None, respawn=False):

            if level_id == "credits":
                self.player.UI_interaction_anim.clear()
                self.state = "credits"
                self.game_state = self.state_manager["credits"](self.DISPLAY, self.player, self.prop_objects)
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

            self.game_state = self.state_manager[level_id](self.DISPLAY, self.player, self.prop_objects) \
                    if level_id not in self.loaded_states else self.loaded_states[level_id]

            start = pygame.time.get_ticks()  # time to start (track the loading screen duration)
            self.state = level_id  # update the current state to the next one
            self.player.UI_interaction_anim.clear()  # empty the UI animations
            load_type = ["loading..." if first_pos is None else "main_loading", 750]  # [load_type, duration]
            self.loading_screen.init(load_type[0], duration=load_type[1])  # initialize the loading screen

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
            self.player.Left = self.player.Right = self.player.Up = self.player.Down = False

            self.new_level_popup = self.new_level_font.render(TITLE_TRANSLATOR[self.state], True, (255, 255, 255))
            self.new_level_popup_rect = self.new_level_popup.get_rect(centerx=self.W // 2, bottom=0)
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


        def state_game(self, events):
            # if the credits are playing, the player doesn't get updated, so the controls aren't checked, and
            # the quit event must be detected
            if self.state == "credits":
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.loop_state = self.state_quit
                            return

            if self.menu:  # menu playing

                self.menu_manager.update(pygame.mouse.get_pos())

                if self.menu_manager.start_game:  # start the game
                    self.menu = False
                    self.loading = False

                    self.start_new_level(
                        self.state,
                        first_pos=(
                            (self.DISPLAY.get_width() // 2 - 120, self.DISPLAY.get_height() // 2 - 20)
                            if not self.first_state
                            else None
                        ),
                    )

            elif self.death_screen:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit_()

                    if event.type == pygame.KEYDOWN:
                        if event.key == self.player.data["controls"]["interact"]:
                            self.respawn()
                            self.player.health = self.player.maximum_health

                self.black_layer.set_alpha(floor((200 / 1500) * (pygame.time.get_ticks() - self.begin_end_screen)))
                self.end_game_ui_texts[0].set_alpha(floor((255 / 1500) * (pygame.time.get_ticks() - self.begin_end_screen)))
                if pygame.time.get_ticks() - self.begin_end_screen > 1500:
                    self.black_layer.set_alpha(200)
                    self.end_game_ui_texts[0].set_alpha(255)

                self.DISPLAY.fill((0, 0, 0))
                self.DISPLAY.blit(self.end_game_bg, (0, 0))
                self.DISPLAY.blit(self.black_layer, (0, 0))
                self.DISPLAY.blit(self.end_game_ui_texts[0], self.end_game_ui_rects[0])
                if floor(pygame.time.get_ticks() / 1000) % 2 == 0 and self.black_layer.get_alpha() == 200:
                    self.DISPLAY.blit(self.end_game_ui_texts[1], self.end_game_ui_rects[1])

            else:

                self.DISPLAY.fill((0, 0, 0))
                update = self.game_state.update(self.player.camera, self.dt)
                if update is not None:  # if a change of state is detected

                    if self.state == "manos_hut" and update == "johns_garden":
                        if self.player.game_instance.quest_manager.quests["A new beginning"].quest_state["Reach Manos in his hut"]:
                            update = "credits"

                    self.start_new_level(update, last_state=self.state)

                """  RUN THE CAMERA ONLY WHEN ITS NOT IN DEBUGGING MODE  """
                if not self.debug and self.cutscene_engine.state != "inactive":
                    self.cutscene_engine.update()
                    self.FPS = 360  # if it works
                elif not self.debug:
                    set_camera_to(self.player.camera, self.player.camera_mode, "follow")

                    if not self.game_state.ended_script and len(self.game_state.camera_script) > 0:
                        self.cutscene_engine.init_script(self.game_state.camera_script)

                    self.FPS = 55
                else:
                    set_camera_to(self.player.camera, self.player.camera_mode, "follow")

                if self.player.health <= 0:
                    self.death_screen = True
                    self.end_game_bg = self.DISPLAY.copy()
                    self.init_death_screen()
                    self.player.health = self.player.backup_hp  # Return full hp

            self.routine()

        async def async_update(self):
            while main.loop_state:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        main.loop_state = main.state_quit
                        break
                else:
                    main.loop_state(events)
                pygame.display.update()
                await asyncio.sleep(0)

            pygame.quit()

    main = Main()
    main.loop_state = main.state_loading

    asyncio.run(main.async_update())
