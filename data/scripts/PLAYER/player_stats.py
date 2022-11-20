import pygame as pg
from .items import Items, ItemSorter
from copy import copy
from ..utils import scale, get_sprite, resource_path


class UpgradeStation:
    def __init__(self, sprite_sheet, font, player_instance):

        # unpack variables
        self.font = font
        self.spr_sh = sprite_sheet
        self.screen, self.w, self.h = (
            player_instance.screen,
            player_instance.screen.get_width(),
            player_instance.screen.get_height(),
        )
        self.player_instance = player_instance
        self.new_points_available = 0

        # upgrade station button
        self.button_upgrade_station = scale(
            self.spr_sh.parse_sprite("level_status"), 3
        )  # The button that launches the upgrade station

        # LVL UI BOX
        self.bu_rect = self.button_upgrade_station.get_rect(
            right=self.w - 10, y=12
        )
        self.level_font = pg.font.Font(
            resource_path("data/database/menu-font.ttf"), 28
        )

        self.t_level = self.level_font.render(
            str(self.player_instance.level), True, (0, 0, 0)
        )

        #
        self.rect_t_level = self.t_level.get_rect(
            center=(self.bu_rect.centerx, self.bu_rect.centery)
        )

        self.up_st_menu = pg.Surface((self.w // 3, self.h // 3), pg.SRCALPHA)

        # UPGRADE STATION UI BOX
        self.us_rect = self.up_st_menu.get_rect(
            right=self.w - 25, y=160 + self.h // 3 - 25
        )  # center

        # ui piece for the upgrade station
        self.ui_inv = scale(self.spr_sh.parse_sprite("catalog_button.png"), 5)
        self.uii_rect = self.ui_inv.get_rect(
            right=self.up_st_menu.get_width(), y=0
        )

        self.show_menu = False  # upgrade station is shown if it's True

        # Player's items:
        self.stats = [
            Damage(self.player_instance.damage),
            Endurance(self.player_instance.endurance),
            CritChance(self.player_instance.critical_chance),
        ]
        self.index_scroll = 0  # Useful to track the scrolling

        self.txt_pt_av = self.font.render(
            f"Upgrade points available : {self.new_points_available}",
            True,
            (0, 0, 0),
        )

    def scroll_down(self):
        self.index_scroll += 1 * (self.index_scroll < len(self.items) - 3)

    def scroll_up(self):
        self.index_scroll -= 1 * (self.index_scroll > 0)

    def new_level(self):
        self.new_points_available += 1
        self.txt_pt_av = self.font.render(
            f"Upgrade points available : {self.new_points_available}",
            True,
            (0, 255, 0),
        )

    def upgrade_stat(self, stat):
        self.new_points_available -= 1
        self.txt_pt_av = self.font.render(
            f"Upgrade points available : {self.new_points_available}",
            True,
            (0, 0, 0),
        )
        new_stat = stat.value + stat.increment
        stat.update_value(new_stat)
        setattr(self.player_instance, stat.attribute, new_stat)

    def update(self, parent_class):
        self.t_level = self.level_font.render(
            str(self.player_instance.level), True, (0, 0, 0)
        )
        self.rect_t_level = self.t_level.get_rect(
            midtop=self.bu_rect.midtop + pg.Vector2(0, 10)
        )

        additionals = [
            parent_class.inventory.get_equipped("Weapon")
        ]  # support for multiples equiped items
        for stat in self.stats:

            addition = 0
            for item in additionals:
                if hasattr(item, stat.attribute):
                    if getattr(item, stat.attribute) > addition:
                        addition = getattr(item, stat.attribute)

            stat.update_value(
                getattr(parent_class, stat.attribute),
                None if not addition else addition,
            )
        stats_l = len(self.stats)  # Length of the items
        self.screen.blit(
            self.button_upgrade_station, self.bu_rect
        )  # blit the inventory button
        self.screen.blit(self.t_level, self.rect_t_level)

        if (
            self.show_menu
        ):  # if it shows the menu, then it does not show the down bar
            self.up_st_menu.blit(
                self.ui_inv, self.uii_rect
            )  # blit the inventory ui

            self.up_st_menu.blit(
                self.txt_pt_av,
                self.txt_pt_av.get_rect(
                    bottomright=self.ui_inv.get_size() + pg.Vector2(12, -10)
                ),
            )

            for index in range(stats_l):  # loop through the items
                # avoid errors where the scroll applied is too far away
                if index + self.index_scroll > stats_l - 1:
                    break

                # getting the item, the first item is 0 + scroll
                stat = self.stats[index + self.index_scroll]

                # track if the item is blitted outside of the ui, if so it breaks the loop
                if (
                    index * stat.image.get_height() + 16
                    > self.uii_rect.height - 15
                ):
                    break

                damages = (
                    parent_class.inventory.get_equipped("Weapon").damage
                    if parent_class.inventory.get_equipped("Weapon")
                    is not None
                    else 0
                )
                # display the item on the screen
                stat.update(
                    self.up_st_menu,
                    (
                        self.uii_rect.x + 25,
                        index * stat.image.get_height() + 12,
                    ),
                    add_args=self.us_rect.topleft,
                )

            # showing a scroll bar
            # h = self.uii_rect.height / item_l
            # step = h / item_l * self.index_scroll * item_l
            # pg.draw.rect(self.inv_menu, (255, 0, 0), [self.uii_rect.right-10, step+10, 5, h * 1.5])
            self.screen.blit(self.up_st_menu, self.us_rect)  # Show menu

    def get_equiped(self, type_: str):

        for item in self.items:
            if item.type == type_ and item.equipped:
                return item

    def handle_clicks(self, pos):

        if self.new_points_available > 0 and self.show_menu:
            pos -= pg.Vector2(
                *self.us_rect.topleft
            )  # get the pos of the click on the surface
            for stat in self.stats:
                # Handle the clicks for all stats
                if stat.handle_clicks(pos):
                    self.upgrade_stat(stat)
                    break

    def set_active(self):  # Switch state of the upgrade station
        self.show_menu = not self.show_menu


class StatHandler:
    def __init__(
        self,
        attribute: str,  # -> name of the attribute in the player class
        name: str,  # -> name shown on the stats menu
        value: float | int,  # -> value
        val_type=int,  # -> type of the value (useful for formating)
        optional_unit: str = None,
        # -> eg: crit chance is expressed in % so we pass "%" in order to show "Crit. Chance : 12%" instead of only "Crit. Chance : 12"
        color: tuple[int, int, int] = (0, 0, 0),  # -> color shown on the board
        increment: int | float = 1,
    ):

        self.max = max
        self.min = min
        self.name = name
        self.value = value
        self.increment = increment

        self.attribute = attribute
        self.val_type = val_type
        self.optional_unit = optional_unit
        self.color = color

        self.font = pg.font.Font(
            resource_path("data/database/menu-font.ttf"), 16
        )
        self.text = self.font.render(
            f"{self.name} : {int(self.value) if val_type is int else round(self.value, 2)}{optional_unit if optional_unit is not None else ''}",
            True,
            self.color,
        )
        self.addition = self.font.render("", True, (0, 0, 0))

        self.image = pg.Surface(self.text.get_size(), pg.SRCALPHA)
        self.rect = self.image.get_rect()

    def handle_clicks(self, pos):
        if self.rect.collidepoint(pos):
            return True
        return False

    def update_value(self, value, item_addition: int = None):

        self.value = value
        self.text = self.font.render(
            f"{self.name} : {int(self.value) if self.val_type is int else round(self.value, 2)}{self.optional_unit if self.optional_unit is not None else ''}",
            True,
            self.color,
        )
        if item_addition is not None:
            self.addition = self.font.render(
                f"+{item_addition}{self.optional_unit if self.optional_unit is not None else ''}",
                True,
                (
                    (self.color[0] - 25) % 255,
                    (self.color[1] - 25) % 255,
                    (self.color[2] - 25) % 255,
                ),
            )

        self.image = pg.Surface(
            (
                self.text.get_width() + self.addition.get_width(),
                self.text.get_height(),
            ),
            pg.SRCALPHA,
        )
        self.rect = self.image.get_rect()

    def update(
        self, surface: pg.Surface, pos: tuple[int, int], add_args=(0, 0)
    ):

        self.image.fill((239, 159, 26))
        rect = copy(self.rect)
        rect.topleft = pos + pg.Vector2(add_args)
        if rect.collidepoint(pg.mouse.get_pos()):
            self.image.fill((219, 139, 6))
        self.image.blit(self.text, (0, 0))
        self.image.blit(self.addition, (self.text.get_width(), 0))

        self.rect.topleft = pos
        surface.blit(self.image, pos)


class Endurance(StatHandler):
    def __init__(self, value: int):
        super().__init__(
            "endurance", "Endurance", value, color=(100, 100, 100)
        )


class CritChance(StatHandler):
    def __init__(self, value: float):
        super().__init__(
            "critical_chance",
            "Crit. Chance",
            value * 100,
            val_type=float,
            optional_unit="%",
            color=(255, 255, 0),
            increment=0.01,
        )

    def update_value(self, value, item_addition: int = None):
        if item_addition is not None:
            item_addition *= 100

        super().update_value(value, item_addition)


class Damage(StatHandler):
    def __init__(self, value: int):
        super().__init__(
            "damage",
            "Damages",
            value,
            val_type=int,
            color=(125, 255, 0),
            increment=2,
        )
