import pygame
from random import random

from ...utils import scale, get_sprite, flip_vertical, resource_path
from ...UI.UI_animation import InteractionName
from copy import copy

from .animation_handler import update_attack

pygame.font.init()
font = pygame.font.Font(resource_path("data/database/menu-font.ttf"), 35)


def get_crit(mod_dmg, wpn):
    crit = random()
    crit_chance = wpn.critical_chance
    if crit < crit_chance:
        return mod_dmg * crit_chance
    return 0


def get_player(img, row, col):
    """[summary]

    Args:
        img (pygame.Surface): [description]
        row (int): [description]
        col (int): [description]
    """
    img.set_colorkey(0x000000)
    return scale(get_sprite(img, 46 * row, 52 * col, 46, 52), 3)


def load_attack_anim(player, sheet):
    sheet_settings = {
        "right_a_1": {"row": 0, "col": 0, "frames": 5, "sheet": "weapon"},
        "right_a_2": {"row": 0, "col": 5, "frames": 6, "sheet": "weapon"},
        "stab_r": {"row": 0, "col": 14, "frames": 5, "sheet": "weapon"},
        "up_a_1": {"row": 1, "col": 0, "frames": 5, "sheet": "weapon"},
        "up_a_2": {"row": 1, "col": 5, "frames": 5, "sheet": "weapon"},
        "stab_u": {"row": 1, "col": 10, "frames": 7, "sheet": "weapon"},
        "down_a_1": {"row": 2, "col": 0, "frames": 5, "sheet": "weapon"},
        "down_a_2": {"row": 2, "col": 5, "frames": 4, "sheet": "weapon"},
        "stab_d": {"row": 2, "col": 10, "frames": 6, "sheet": "weapon"},
    }

    for key in sheet_settings:
        player.anim[key] = [
            get_player(
                sheet,
                sheet_settings[key]["col"] + i,
                sheet_settings[key]["row"],
            )
            for i in range(sheet_settings[key]["frames"])
        ]

    player.anim["left_a_1"] = [
        flip_vertical(sprite) for sprite in player.anim["right_a_1"]
    ]
    player.anim["left_a_2"] = [
        flip_vertical(sprite) for sprite in player.anim["right_a_2"]
    ]
    player.anim["stab_l"] = [
        flip_vertical(sprite) for sprite in player.anim["stab_r"]
    ]


def get_john(player):
    sheet_settings = {
        # MOVEMENT
        "right": {"row": 1, "col": 0, "frames": 5},
        "idle_r": {"row": 0, "col": 0, "frames": 2},
        "idle_d": {"row": 0, "col": 4, "frames": 2},
        "idle_u": {"row": 0, "col": 2, "frames": 2},
        "down": {"row": 3, "col": 0, "frames": 5},
        "up": {"row": 2, "col": 0, "frames": 5},
        "dash_r": {"row": 4, "col": 0, "frames": 5},
        "dash_d": {"row": 6, "col": 0, "frames": 5},
        "dash_u": {"row": 5, "col": 0, "frames": 5},
        # ATTACK
        "right_a_1": {"row": 0, "col": 0, "frames": 5, "sheet": "weapon"},
        "right_a_2": {"row": 0, "col": 5, "frames": 6, "sheet": "weapon"},
        "stab_r": {"row": 0, "col": 13, "frames": 6, "sheet": "weapon"},
        "up_a_1": {"row": 1, "col": 0, "frames": 5, "sheet": "weapon"},
        "up_a_2": {"row": 1, "col": 5, "frames": 5, "sheet": "weapon"},
        "stab_u": {"row": 1, "col": 10, "frames": 7, "sheet": "weapon"},
        "down_a_1": {"row": 2, "col": 0, "frames": 5, "sheet": "weapon"},
        "down_a_2": {"row": 2, "col": 5, "frames": 5, "sheet": "weapon"},
        "stab_d": {"row": 2, "col": 10, "frames": 6, "sheet": "weapon"},
    }

    anim = {
        # Right ANIMATION
        "right": [],
        "right_a_1": [],
        "right_a_2": [],
        "stab_r": [],
        # Up ANIMATION
        "up": [],
        "up_a_1": [],
        "up_a_2": [],
        "stab_u": [],
        # Down ANIMATION
        "down": [],
        "down_a_1": [],
        "down_a_2": [],
        "stab_d": [],
        # Dash ANIMATION
        "dash_r": [],
        "dash_u": [],
        "dash_d": [],
        # Idle ANIMATION
        "idle_r": [],
        "idle_l": [],
        "idle_u": [],
        "idle_d": [],
    }
    x_gap = y_gap = 0
    for key in anim:
        if key in sheet_settings:
            sheet = player.sheet
            if "sheet" in sheet_settings[key]:
                weapon = player.inventory.get_equipped("Weapon")
                if weapon is not None:
                    sheet = weapon.sheet
                elif "weapon" in sheet_settings[key]["sheet"]:
                    sheet = player.default_attack_sheet

            anim[key] = [
                get_player(
                    sheet,
                    sheet_settings[key]["col"] + i,
                    sheet_settings[key]["row"],
                )
                for i in range(sheet_settings[key]["frames"])
            ]

    # Load the reverse frames to the dict for the left animation
    anim["left"] = [flip_vertical(sprite) for sprite in anim["right"]]
    anim["left_a_1"] = [flip_vertical(sprite) for sprite in anim["right_a_1"]]
    anim["left_a_2"] = [flip_vertical(sprite) for sprite in anim["right_a_2"]]
    anim["stab_l"] = [flip_vertical(sprite) for sprite in anim["stab_r"]]
    anim["idle_l"] = [flip_vertical(sprite) for sprite in anim["idle_r"]]
    anim["dash_l"] = [flip_vertical(sprite) for sprite in anim["dash_r"]]
    return anim


def set_camera_to(camera, camera_mode, _KEY):
    """
    Look above for "Player's Camera Settings" for more info!
    """
    camera.set_method(camera_mode[_KEY])


def leveling(player):
    # PLAY THE SOUND OF THE LEVEL UPGRADING
    if player.experience >= 180:  # <- The max width of the bar
        player.level += 1  # Increase the level
        player.experience = player.experience - 180
        # Do the maths in case the exp is more than 180, else its 0
        player.level_index += 1  # a index for multiplying 180(width)
        player.upgrade_station.new_level()
        player.ring_lu = True  # Level UP UI starts

    # Player needs more and more exp on each level, therefore we have to cut it
    player.experience_width = player.experience / player.level_index


def update_camera_status(player):
    for key, cam_mode in player.camera_mode.items():
        if type(player.camera.method) is type(cam_mode):
            player.camera_status = key
            break


def update_ui_animations(player, dt):
    to_remove = []
    for UI_anim in player.UI_interaction_anim:
        alive = UI_anim.update(player.camera.offset.xy, dt)
        if not alive:
            to_remove.append(UI_anim)

    for remove in to_remove:
        player.UI_interaction_anim.remove(remove)


key_translator = {
    "player_room": "John's Room",
    "johns_garden": "Open World",
    "kitchen": "Kitchen",
    "manos_hut": "Mano's hut",
    "cave": "Cave",
    "cave2": "Cave Entrance",
    "cave_garden": "Cave garden",
    "cave_entrance": "Cave Entrance",
    "cave_room_1": "Cave floor 1",
    "cave_room_2": "Cave floor 2",
    "cave_passage": "? ? ?",
}


def movement(player):
    """Allowing the player to move when he is not attacking or checking inventory"""
    if player.inventory.show_menu or player.attacking:
        return

    if player.Up and player.move_ability["up"]:
        player.rect.y -= player.velocity[1]
        player.direction = "up"
    elif player.Down and player.move_ability["down"]:
        player.rect.y += player.velocity[1]
        player.direction = "down"
    if player.Left and player.move_ability["right"]:
        player.rect.x -= player.velocity[0]
        player.direction = "right"
    elif player.Right and player.move_ability["left"]:
        player.rect.x += player.velocity[0]
        player.direction = "left"

    # This stops the player animation from running, his movement as well
    if not (True in (player.Up, player.Down, player.Right, player.Left)):
        player.walking = False


def check_for_interaction(player, exit_rects):
    # TODO: find a font + adapt the texts + add a "background" to the font
    # gets all the ui animations tags (to know if an animation is already existing)
    all_current_animations = [anim.tag for anim in player.UI_interaction_anim]
    # player's interaction rect
    itr_box = pygame.Rect(
        *(
            (player.rect.topleft - player.camera.offset.xy)
            - pygame.Vector2(17, -45)
        ),
        player.rect.w // 2,
        player.rect.h // 2
    )
    text = ""

    for object_ in player.rooms_objects:
        if hasattr(object_, "IDENTITY"):
            if object_.IDENTITY == "NPC":
                if object_.interactable:
                    if object_.interaction_rect is not None:
                        object_.highlight = itr_box.colliderect(
                            object_.interaction_rect
                        )
                        if object_.highlight:
                            text = object_.__class__.__name__
            elif object_.IDENTITY == "PROP":
                if object_.name == "chest":
                    object_.highlight = (
                        itr_box.colliderect(object_.interaction_rect)
                        and not object_.has_interacted
                    )
                    if object_.highlight:
                        text = object_.__class__.__name__

    # look for usable exit rect
    for destination, exit_rect in exit_rects.items():
        exit_rect_ = copy(exit_rect[0])  # get the exit rect
        exit_rect_.topleft -= player.camera.offset.xy  # apply scroll
        # get the current animation (if there is one)
        UI_anim = (
            player.UI_interaction_anim[
                all_current_animations.index(str(id(exit_rect)))
            ]
            if str(id(exit_rect)) in all_current_animations
            else None
        )
        # check for the possible interaction and
        if exit_rect_.colliderect(itr_box):
            # draw the exit rect
            pygame.draw.rect(player.screen, (255, 255, 255), exit_rect_, 2)
        else:
            if UI_anim is not None:
                if not UI_anim.dying:
                    UI_anim.kill()

    # render the name of the next animation (TODO: choose if we remove it or not)
    render = font.render(text, True, (255, 255, 255))
    player.screen.blit(
        render, render.get_rect(center=(player.screen.get_width() // 2, 25))
    )


def check_for_hitting(player):
    """
    room_objects is a list containing only the enemies of the current environment,
    for each one, if they are attackable and player hits them, they will lose hp
    """
    for obj in player.rooms_objects:
        if hasattr(obj, "attackable"):
            if obj.attackable:
                if (
                    obj.rect is None or player.attacking_hitbox is None
                ):  # prevent from errors due to unassigned hitbox
                    continue

                t_e_rect = obj.hitbox_rect
                t_e_rect.topleft -= obj.scroll
                if player.attacking_hitbox.colliderect(t_e_rect):
                    equipped_weapon = player.inventory.get_equipped("Weapon")

                    # pygame.draw.line(player.screen, (255, 255, 255), obj.rect.topright, obj.rect.bottomleft)

                    # This is where it will play the object's hit sound NOT THE SWORD
                    player.sound_manager.play_sound("dummyHit")

                    knock_back = {}
                    if equipped_weapon.KB:
                        knock_back["duration"] = equipped_weapon.knock_back[
                            "duration"
                        ]

                        # print(player.rect.topleft - player.camera.offset.xy + pygame.Vector2(15, 60), obj.rect.center)

                        knock_back["vel"] = pygame.Vector2(
                            pygame.Vector2(obj.rect.center)
                            - pygame.Vector2(
                                player.rect.topleft + pygame.Vector2(15, 60)
                            )
                        )
                        knock_back["vel"].scale_to_length(
                            equipped_weapon.knock_back["vel"]
                        )

                        knock_back["friction"] = -knock_back["vel"]
                        knock_back["friction"].scale_to_length(
                            equipped_weapon.knock_back["friction"]
                        )
                        # print("apply knock back", knock_back)

                    crit = get_crit(
                        player.modified_damages,
                        player.inventory.get_equipped("Weapon"),
                    )

                    obj.deal_damage(
                        player.modified_damages + crit,
                        crit > 0,
                        knock_back=knock_back,
                    ) if player.current_combo != player.last_attack else obj.deal_damage(
                        player.modified_damages * player.max_combo_multiplier
                        + crit,
                        crit > 0,
                        knock_back=knock_back,
                    )
                    equipped_weapon.start_special_effect(obj)
                if obj.hp <= 0:  # Check if its dead , give xp to the player
                    player.experience += obj.xp_available
                    obj.xp_available = 0


def attack(player, pos):
    click_time = pygame.time.get_ticks()
    player.last_attacking_click = click_time

    sword_sound: str = player.inventory.get_equipped("Weapon").sound

    if not player.attacking:
        player.attacking = True
        player.current_combo += 1
        player.next_combo_available = False
        update_attack(player, pos)
        check_for_hitting(player)
        player.sound_manager.play_sound(sword_sound)
    else:
        # if It's time to show the next combo, make sure player isn't moving else cancel
        if player.next_combo_available:
            if click_time - player.last_attacking_click > player.attack_speed:
                player.attacking = False
                player.current_combo = 0
            else:
                player.restart_animation = True
                player.current_combo += 1
                player.last_attacking_click = click_time
                update_attack(player, pos)
                check_for_hitting(player)
                player.next_combo_available = False
                player.sound_manager.play_sound(sword_sound)
                if player.current_combo > player.last_attack:
                    player.last_combo_hit_time = pygame.time.get_ticks()


def check_content(player, pos):
    position = player.rect.topleft - player.camera.offset.xy
    itr_box = pygame.Rect(*position, player.rect.w // 2, player.rect.h // 2)
    # Manual Position tweaks
    itr_box.x -= 17
    itr_box.y += 45

    # Interact Rect for debugging
    # pygame.draw.rect(player.screen, (255,255,255), itr_box, 1)
    for obj in player.rooms_objects:
        if hasattr(obj, "IDENTITY"):
            if obj.IDENTITY == "NPC":
                if obj.interactable:
                    if itr_box.colliderect(obj.interaction_rect):
                        # If player clicks Interaction key
                        if player.Interactable:
                            # Stop the npcs from moving
                            obj.interacting = True

                            # Turn on interact zone
                            player.is_interacting = True

                            player.interacting_with = obj

                            # Get npc's text
                            player.npc_text = obj.tell_story

                            # Stop browsing to reduce calcs
                            break
            elif obj.IDENTITY == "PROP":
                if (
                    obj.name == "chest"
                ):  # MUST BE BEFORE checking collision to avoid attribute errors
                    if itr_box.colliderect(obj.interaction_rect):
                        player.interacting_with = obj
                        obj.on_interaction(player)  # Run Chest opening
