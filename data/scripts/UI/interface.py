import pygame as pg
import json
from ..utils import scale, resource_path, l_path, get_sprite


class Interface:

    def __init__(self, screen, ui_background) -> None:
        '''
            This System is mathematically taking each letter in all sizes.

            How to use:
                my_font = Font('font_name.extension') / # font_big.png 

                

                my_font.render(surface -> Pygame.Surface, 'text here' -> Str, position -> Tuple)
        
        '''
        self.screen = screen  # Screen surface is needed to blit the font surfaces

        # We might need a more detailed font
        self.img = scale(l_path('data/scripts/UI/interaction_font.png'), 2)

        # Your sprite sheet must be absolute identical to this list
        self.alphabet = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
            'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
            'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
            '!', '"', '(', ')', '$', '?'
        ]

        # To get mathematically the width of the characters (assuming there are no gaps between them)
        character_width = self.img.get_width() // len(self.alphabet)
        character_height = self.img.get_height()

        # Here contains the surfaces of the sprite sheet lexer
        self.text = [get_sprite(self.img, character_width * x, 0, character_width, character_height) for x in
                     range(len(self.alphabet))]

        self.current_gui_index = 0

        self.timer = 0

        self.ui_bg = ui_background
        self.pos = (screen.get_width() // 2 - 430, screen.get_height() // 2 + 110)
        self.sentence_end = False

    def reset(self):
        '''
            Resets the browsing index
        '''
        self.current_gui_index = -1

    def _get_data(self, entity):
        '''
            Try/except method will be temporary until the script is ready and implemented into json
        '''
        return entity

    def draw(self, txt, dt):
        """
        :param surf: Screen surface
        :param txt: Text content
               How to use:
                   variable_containing_class.render(Surface, 'Your content here', Position)


                   \n : To make a new line

                   Example: Apples are\nGreen and Red
                   Output:
                       Apples are
                       Green and Red

        :param pos:  (X,Y) coordinates
        """

        # Draw background UI
        self.screen.blit(self.ui_bg, (155, self.screen.get_height() // 2 + 80))

        text = self._get_data(txt)
        self.timer += dt * 2
        if self.timer > 0.060:  # 0.30 default delta time
            if self.current_gui_index < len(text):
                self.current_gui_index += 1
                # if text[self.current_gui_index] != ' ':  
                #    self.sound.play()  <- This will soon be implented
            else:
                # Something for the UI later on.
                self.sentence_end = True
                # Reset the timer
            self.timer = 0

        # Renders the text based on the currect_gui_index
        self.rendering(self.screen, text[:self.current_gui_index], self.pos)

    def rendering(self, surf, txt, pos):
        x_gap = y_gap = 0
        # For each letter passed
        for t in txt:
            # Browse the alphabet and blit the correct letter
            for i in range(len(self.alphabet)):
                if t.upper() == self.alphabet[i]:
                    surf.blit(self.text[i], (pos[0] + x_gap, pos[1] + y_gap))

            # Space
            x_gap += self.text[0].get_width() + 1

            if '\n' == t:
                y_gap += self.text[0].get_height() + 7
                x_gap = 0  # Reset X position
