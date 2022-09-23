import pygame as pg
from ..utils import scale, get_sprite
from copy import copy
from ..utils import resource_path


class Inventory:

    def __init__(self, screen, sprite_sheet):

        # unpack variables
        self.spr_sh = sprite_sheet
        self.screen, self.w, self.h = screen, screen.get_width(), screen.get_height()
        self.font = pg.font.Font(resource_path("data/database/menu-font.ttf"), 18)

        # inventory button
        self.button_inv = scale(self.spr_sh.parse_sprite("inventory"), 3)

        self.button_inv_h = scale(self.spr_sh.parse_sprite("inventory_hover"), 3)

        self.bi_rect = self.button_inv.get_rect(right=self.w - 10, y=86)
        # the menu where all the items in the inventory will be displayed
        # only if the player is currently in this state
        self.inv_menu = pg.Surface((self.w // 3, self.h // 3), pg.SRCALPHA)
        self.im_rect = self.inv_menu.get_rect(right=self.w - 25, y=160)  # center

        # ui piece for the inventory
        self.ui_inv = scale(self.spr_sh.parse_sprite("catalog_button.png"), 5)
        self.uii_rect = self.ui_inv.get_rect(right=self.inv_menu.get_width(), y=0)
        self.hover_color = self.ui_inv.get_at((20, 20))
        self.hover_color = [self.hover_color[0] - 25, self.hover_color[1] - 25, self.hover_color[2] - 25]

        self.show_menu = False  
        self.items = [] 
        self.index_scroll = 0 
        self.backup_item_len = len(self.items)

    def scroll_down(self):
        self.index_scroll += 1 * (self.index_scroll < len(self.items) - 3)

    def scroll_up(self):
        self.index_scroll -= 1 * (self.index_scroll > 0)

    def update(self, parent_class):
        item_l = len(self.items)  # Length of the items
        self.screen.blit(self.button_inv, self.bi_rect)  # blit the inventory button

        if self.show_menu:  # if it shows the menu, then it does not show the down bar
            self.inv_menu.blit(self.ui_inv, self.uii_rect)  # blit the inventory ui

            # Hover img 
            self.screen.blit(self.button_inv_h, self.bi_rect)

            for index in range(item_l):  # loop through the items
                # avoid errors where the scroll applied is too far away 
                if index + self.index_scroll > item_l - 1:
                    break

                # getting the item, the first item is 0 + scroll
                item = self.items[index + self.index_scroll]

                # track if the item is blitted outside of the ui, if so it breaks the loop
                if index * item.image.get_height() + 16 > self.uii_rect.height - 15:
                    break
                
                weapon = parent_class.inventory.get_equipped("Weapon")
                damages = weapon.damage if weapon is not None else 0
               
                # display the item on the screen
                item.update(self.inv_menu, (self.uii_rect.x + 25, index * item.image.get_height() + 12), damages,
                            add_pos=self.im_rect.topleft)

              
            # Show menu
            self.screen.blit(self.inv_menu, self.im_rect)  
            self.screen.blit(self.font.render(f"{item_l}/32", True, (0, 0, 0)),
                             (self.im_rect[0] + 340, self.im_rect[1] + 175)) 
            self.screen.blit(self.font.render(f"HP Potions:{parent_class.health_potions}", True, (0, 0, 0)),
                             (self.im_rect[0] + 50, self.im_rect[1] + 175))


    def reset_equippement(self, type_: str, instance: object):

        for item in self.items:
            if item.type == type_ and item != instance:
                item.equipped = False

    def get_equipped(self, type_: str):

        for item in self.items:
            if item.type == type_ and item.equipped:
                return item

    def handle_clicks(self, pos, player):

        if self.show_menu:
            pos -= pg.Vector2(*self.im_rect.topleft)  # get the pos of the click on the surface
            for item in self.items:
                changes = item.handle_clicks(pos, player)  # Handle the clicks for all items
                if changes is not None:
                    if changes[0]:
                        self.reset_equippement(changes[1], changes[2])

    def set_active(self):  # Switch state of the inventory
        self.show_menu = not self.show_menu
