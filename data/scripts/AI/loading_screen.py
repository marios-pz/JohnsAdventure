import pygame as pg
from ..utils import load, get_sprite, scale


class LoadingScreen:

    def __init__(self, screen:pg.Surface):

        # unpack constructor's arguments
        self.screen = screen
        self.W, self.H = screen.get_size()

        # cat
        self.cat_spr_sh = load("data/sprites/npc_spritesheet.png")
        self.cat_sprites = [scale(get_sprite(self.cat_spr_sh, 3 + 39 * i, 49, 39, 32), 2) for i in range(3)]
        # colors
        self.bg_color = (0, 0, 0)
        self.font_color = (255, 255, 255)

        # text
        self.font = pg.font.Font("data/database/pixelfont.ttf", 24)

        # animation
        self.current_time = pg.time.get_ticks()
        self.delay_cat_anim = self.delay_dot_anim = self.index_dot_anim = self.index_cat_anim = 0

        # duration
        self.start_loading = 0
        self.duration = 2500
        self.next_state = None
        self.end_music = None

        # loading screen options
        self.text = True
        self.cat = True

    def start(self, next_state:str, end_music:str=None, text:bool=True, cat:bool=True, duration:int=0):
        self.start_loading = pg.time.get_ticks()
        self.next_state = next_state
        self.end_music = end_music
        self.text = text
        self.cat = cat
        if duration != 0:
            self.duration = duration

    def handle_events(self):
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    pg.quit()
                    raise SystemExit
                
    def update(self):

        # handle events (only not to have error if the player quits)
        self.handle_events()

        # draw background
        self.screen.fill(self.bg_color)
    
        # update time
        self.current_time = pg.time.get_ticks()

        # animate dots
        if self.current_time - self.delay_dot_anim > 250:
            self.index_dot_anim = (self.index_dot_anim + 1) % 3
            self.delay_dot_anim = self.current_time

        # animate cat
        if self.current_time - self.delay_cat_anim > 100:
            self.index_cat_anim = (self.index_cat_anim + 1) % len(self.cat_sprites)
            self.delay_cat_anim = self.current_time

        if self.text:
            # render loading text -> "Loading..."
            loading_text = self.font.render(f"Loading {'.'*(self.index_dot_anim+1)}", True, self.font_color)
            # blit loading text
            self.screen.blit(loading_text, loading_text.get_rect(bottomleft=(self.W-400, self.H-50)))

        if self.cat:
            # blit cat
            self.screen.blit(self.cat_sprites[self.index_cat_anim], self.cat_sprites[self.index_cat_anim].get_rect(bottomright=(self.W-50,self.H-50)))

        # check if the loading duration is passed
        if pg.time.get_ticks() - self.start_loading > self.duration:
            return {"next_state": self.next_state, "next_music": self.end_music}
        