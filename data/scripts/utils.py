'''
 Credits @Marios325346

 Functions to reduce typing :rofl:

'''
import json
import os
import pathlib
import pygame
import sys

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache


class UI_Spritesheet:
    def __init__(self, filename):
        self.sprite_sheet = pygame.image.load(resource_path(filename)).convert()
        with open(resource_path('data/database/ui.json')) as f:
            self.data = json.load(f)

    def get_sprite(self, x, y, w, h):  # Data from the json file
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((255, 255, 255))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, w, h))
        return sprite

    def parse_sprite(self, name):
        sprite = self.data['frames'][name]['frame']
        return self.get_sprite(sprite["x"], sprite["y"], sprite["w"], sprite["h"])


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, str(pathlib.Path(relative_path)))


@lru_cache(1000)
def l_path(relative_path, alpha=None):
    """ Upgraded load function for PyInstaller """
    if alpha:
        return pygame.image.load(resource_path(relative_path)).convert_alpha()
    return pygame.image.load(resource_path(relative_path)).convert()


@lru_cache(1000)
def load(path, alpha=None):
    if alpha:
        return pygame.image.load(path).convert_alpha()
    return pygame.image.load(path).convert()


@lru_cache(1000)
def scale(img, n):
    return pygame.transform.scale(img, (img.get_width() * n, img.get_height() * n))


@lru_cache(1000)
def smooth_scale(img, n: float):
    return pygame.transform.smoothscale(img, (img.get_width() * n, img.get_height() * n))


@lru_cache(1000)
def double_size(img):
    return pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))


@lru_cache(1000)
def flip_vertical(img):
    return pygame.transform.flip(img, True, False)


@lru_cache(1000)
def flip_horizontal(img):
    return pygame.transform.flip(img, False, True)


def get_sprite(spritesheet: pygame.Surface, x, y, w, h) -> pygame.Surface:  # Gets NPC from spritesheet

    rect = pygame.Rect(
        x, y, 
        w if x + w <= (W := spritesheet.get_width()) else abs(W - x),  # adapt size if sprite goes out of the 
        h if y + h <= (H := spritesheet.get_height()) else abs(H - y)  # sheet.
    )
    result = pygame.Surface((w, h)) if x >= W or y >= H else spritesheet.subsurface(rect).convert()
    result.set_colorkey((255, 255, 255))
    
    return result
