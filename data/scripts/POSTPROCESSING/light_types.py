import pygame as pg
from math import cos, sin, radians, sqrt


class LightSource:
    """Basically drawing a simulated light source"""

    def __init__(self, pos: pg.Vector2, radius: int, dep_opacity: int, color: tuple[int, int, int]) -> None:
        self.surface = pg.Surface((radius*2, radius*2), pg.SRCALPHA)
        self.radius = radius  # radius of the light
        self.pos = pos  # position on the screen of the light
        self.n_circles = self.radius // 2  # number of circles drawn
        self.opacity = dep_opacity  # opacity of the tiniest circle -> max opacity
        self.color = color  # color RGB

        # draw the lights on the surface (so you don't have to redraw it every frame)
        self.draw_light_circle()

    def get_alpha(self, i):
        # function calculated to manage the growth of alpha -> f(x) = sqrt(x/n_circles)^4 * final_opacity
        alpha = int((sqrt(i/self.n_circles)**4)*self.opacity)
        return alpha if alpha <= 255 else 255

    def draw_light_circle(self) -> list:
        # draw the circles progressively with growing alpha and decreasing radius
        return [pg.draw.circle(self.surface, (self.color[0], self.color[1], self.color[2], self.get_alpha(i)),
                               [self.radius, self.radius], int(self.radius - self.radius * i / self.n_circles))
                for i in range(self.n_circles)]

    def update(self, screen, scroll, LAYER) -> None:
        # display the light
        screen.blit(self.surface, self.pos-pg.Vector2(self.radius, self.radius)-scroll)
        # "cut" the light emplacement of the luminosity layer
        pg.draw.circle(LAYER, (0, 0, 0, 0), self.pos-scroll, self.radius)


class PolygonLight:

    def __init__(self, origin: pg.Vector2, height: int, radius: int, dep_angle: int, end_angle: int,
                 color: tuple[int, int, int], dep_alpha: int, horizontal: bool = False, additional_alpha: int = 0,
                 rotated: bool = False):

        self.pos = origin - pg.Vector2(radius, radius)  # position on the screen
        self.radius = radius  # radius of the light
        self.style = {"color": color, "alpha": dep_alpha, "undo_layer_alpha": additional_alpha}  # style
        self.dep_angle = dep_angle  # first angle
        self.end_angle = end_angle  # revolution angle (final point angle = first angle + end angle)

        self.start_point = pg.Vector2((self.radius, self.radius))  # middle of the surface
        self.diff = pg.Vector2(0, -height // 2) if not horizontal else pg.Vector2(height // 2, 0)  # opti variable
        self.top_point = self.start_point + self.diff  # top corner
        self.bot_point = self.start_point - self.diff  # bot corner

        # calculate the furthest point of the light
        self.top_edge = pg.Vector2(self.radius * (cos(radians(self.dep_angle)) + 1),
                                   self.radius * (sin(radians(self.dep_angle)) + 1))
        self.down_edge = pg.Vector2(self.radius * (cos(radians(self.dep_angle+self.end_angle)) + 1),
                                    self.radius * (sin(radians(self.dep_angle+self.end_angle)) + 1))

        # generate a surface of twice radius width/height
        self.surface = pg.Surface((self.radius * 2, self.radius * 2), pg.SRCALPHA)

        self.rotated = rotated
        # draw the actual light
        self.draw_light(self.surface)
        #if rotated:
        #    self.surface = pg.transform.rotate(self.surface, 180)

    def get_points(self, radius) -> list:
        # we take a variable radius, as we will need to generate points according to different radius
        if self.rotated:
            new_list = [pg.Vector2(self.radius - radius * cos(radians(self.dep_angle + i)),
                        self.radius - radius * sin(radians(self.dep_angle + i))) for i in range(self.end_angle)]
            new_list.reverse()
            return new_list
        return [pg.Vector2(self.radius+radius*cos(radians(self.dep_angle+i)),
                           self.radius+radius*sin(radians(self.dep_angle+i))) for i in range(self.end_angle)]

    def get_alpha(self, index_circle) -> int:
        alpha = int((sqrt(index_circle / (self.radius // 2)) ** 4) * self.style["alpha"])
        return alpha if alpha <= 255 else 255

    def draw_polygon(self, surface, radius, alpha) -> None:

        pts = self.get_points(radius)
        pg.draw.polygon(surface, (self.style["color"][0], self.style["color"][1], self.style["color"][2], alpha),
                        [self.top_point, *pts, self.bot_point])
        pg.draw.polygon(surface, (self.style["color"][0], self.style["color"][1], self.style["color"][2], alpha),
                        [self.top_point, pts[-1], self.start_point])
        pg.draw.polygon(surface, (self.style["color"][0], self.style["color"][1], self.style["color"][2], alpha),
                        [self.bot_point, pts[0], self.start_point])

    def undo_layer(self, layer, pos) -> None:
        vec = [pg.Vector2(self.radius, self.radius) + self.diff, pg.Vector2(self.radius, self.radius) - self.diff]
        pts = [pt + pos for pt in self.get_points(self.radius)]
        pg.draw.polygon(layer, (0, 0, 0, self.style["undo_layer_alpha"]), [pos + vec[0], *pts, pos + vec[1]])

    def draw_light(self, surface) -> list:
        return [self.draw_polygon(surface, self.radius-i*2, self.get_alpha(i)) for i in range(self.radius//2)]

    def update(self, screen, scroll, LAYER) -> None:
        self.undo_layer(LAYER, self.pos-scroll)
        screen.blit(self.surface, self.pos - scroll)
