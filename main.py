'''
    Welcome to John's Adventure! Hope you like my new game!

    Please be patient with some pieces of the code, it will take some time to clean the code ;')

'''


import pygame as pg
import threading

from data.scripts.world import main, GameManager
from data.scripts.utils import resource_path


if __name__ == '__main__':
    game_instance = main()
    game_instance.update()
