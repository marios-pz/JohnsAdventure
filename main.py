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

    # state_game
    from data.scripts.PLAYER.player_sub.tools import set_camera_to

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

        # TODO
        def pause(self):
            return

            if self.player.paused:
                self.pause_menu.init_pause()
                while True:
                    upd = self.pause_menu.update()

                    if upd == "quit":
                        quit_pause()
                        self.menu = True
                        self.player.paused = False
                        self.menu_manager.start_game = False
                        break
                    elif upd == "resume":
                        quit_pause()
                        self.player.paused = False
                        break

                    pygame.display.update()

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


        def state_credits(self, events):
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.loop_state = self.state_quit

        def state_menu(self, events):
            self.menu_manager.update(events, pygame.mouse.get_pos())

            if self.menu_manager.start_game:  # start the game
                self.menu = False
                self.loading = False

                self.sync_new_level(
                    self.state,
                    first_pos=(
                        (self.DISPLAY.get_width() // 2 - 120, self.DISPLAY.get_height() // 2 - 20) if not self.first_state else None
                    ),
                )

        def state_game_over(self, events):
            for event in events:
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

        def state_game(self, events):
            # if the credits are playing, the player doesn't get updated, so the controls aren't checked, and
            # the quit event must be detected
            if self.state == "credits":
                self.state_credits(events)
                return
            elif self.menu:  # menu playing
                self.state_menu(events)
            elif self.death_screen:
                self.state_game_over(events)
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
