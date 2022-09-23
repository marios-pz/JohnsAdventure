import pygame as pg
from copy import copy
from .light_types import LightSource, PolygonLight


class LightManager:

    def __init__(self, DISPLAY):
        # ------------ DISPLAY ------------------
        self.DISPLAY = DISPLAY
        self.W, self.H = self.DISPLAY.get_size()

        # ------------ OBJECTS -----------------
        self.objects = []

        # ----------- LAYERS -------------------
        self.opacities = {
            "night": 128,
            "day": 0,
            "inside_dark": 100,
            "inside": 75,
            "inside_clear": 75
        }
        self.colors = {
            "night": (0, 7, 20),
            "day": (255, 255, 255),
            "inside_dark": (0, 0, 0),
            "inside": (0, 0, 0),
            "inside_clear": (0, 0, 0)
        }
        self.main_layer = pg.Surface(self.DISPLAY.get_size(), pg.SRCALPHA)

        # -------------- LIGHT SOURCES -----------
        self.lights = []
        self.light_state = ""

    def init_level(self, new_level_instance):
        """
        Initialize lights of a new level
        :param new_level_instance: levels.GameState, instance of the newly initialized level
        :return: None
        """
        self.lights = []  # empty the current lights
        for obj in new_level_instance.objects:  # loop through the objects to check if they've light sources
            if hasattr(obj, "light_sources"):  # detect the light source
                self.lights.extend(obj.light_sources)  # add it/them
        self.lights.extend(new_level_instance.additional_lights)  # add the "manually" added light sources
        self.light_state = new_level_instance.light_state  # set the light state

    def update(self, current_level):
        """
        Update the lights.
        :param current_level: levels.GameState, the current level being played.
        :return: None
        """

        # manage lights
        if self.light_state != "day" or "inside" in current_level.light_state:
            for light in self.lights:
                light.update(self.DISPLAY, current_level.scroll, self.main_layer)

        # blit layer
        self.DISPLAY.blit(self.main_layer, (0, 0))

        # update current layer
        self.main_layer.fill(self.colors[current_level.light_state])
        self.main_layer.set_alpha(self.opacities[current_level.light_state])


class LightTypes:

    """Class to reference all the lights available.
    It's useful for the props automatic generation, according to open_world.json file."""

    light_types = {
        "polygon_light": PolygonLight,
        "light_sources": LightSource
    }

    def __init__(self):
        pass

    def get_light_object(self, light_name, info, scale):

        """
        Returns a light object, with the proper size and position (according to scale)
        :param light_name: str, type of the light (must be referenced in self.light_types)
        :param info: dict, characteristics of the light
        :param scale: int, scale of the sprite
        :return: light object -> PolygonLight or LightSource
        """

        if light_name not in self.light_types:
            raise ValueError(f"Light type {light_name} is unknown.")

        args = []
        for key, item in info.items():
            item_ = copy(item)
            if key == "pos":
                item_[0] *= scale
                item_[1] *= scale
            elif key == "radius" or key == "height":
                item_ *= scale

            args.append(item_)

        return self.light_types[light_name](*args)
