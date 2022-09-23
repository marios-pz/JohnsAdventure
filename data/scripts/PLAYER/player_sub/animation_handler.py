import pygame as p
import math

import pygame.math

from .dash import update_dash

vec = pygame.math.Vector2


def animate_level_up_ring(player):
    """
        Level up ring will be removed or disabled soon.
    
    if player.ring_lu:
        if p.time.get_ticks() - player.delay_rlu > 150:
            player.delay_rlu = p.time.get_ticks()

            if player.id_rlu + 1 < len(player.lvl_up_ring):
                player.id_rlu += 1
            else:
                player.ring_lu = False
                player.id_rlu = 0

            player.curr_frame_ring = player.lvl_up_ring[player.id_rlu]
            player.screen.blit(player.curr_frame_ring, player.curr_frame_ring.get_rect(
                center=player.rect.topleft - player.camera.offset.xy + p.Vector2(15, 80)
            ))
    """
    pass


def animation_handing(player, dt, m, pos):
    player.dust_particle_effet.update(player.screen)

    # Draw the Ring
    angle = math.atan2(
        m[1] - (player.rect.top + 95 - player.camera.offset.y),
        m[0] - (player.rect.left + 10 - player.camera.offset.x),
    )
    x, y = pos[0] - math.cos(angle), pos[1] - math.sin(angle) + 10
    angle = abs(math.degrees(angle)) + 90 if angle < 0 else 360 - math.degrees(angle) + 90
    image = p.transform.rotate(player.attack_pointer, angle)
    ring_pos = (x - image.get_width() // 2 + 69, y - image.get_height() // 2 + 139)

    # Blit attack ring only on this condition
    if not player.ring_lu and player.camera_status != "auto":
        player.screen.blit(image, ring_pos)

    update_attack(player, pos)

    if not player.attacking and not player.dashing:
        angle = math.atan2(
            m[1] - (player.rect.top + 95 - player.camera.offset.y),
            m[0] - (player.rect.left + 10 - player.camera.offset.x),
        )
        angle = abs(math.degrees(angle)) if angle < 0 else 360 - math.degrees(angle)
        if player.walking:
            if p.time.get_ticks() - player.delay_animation > 100:
                player.index_animation = (player.index_animation + 1) % len(player.anim["right"])
                player.delay_animation = p.time.get_ticks()

        else:
            if p.time.get_ticks() - player.delay_animation > 350:
                player.index_animation = (player.index_animation + 1) % len(player.anim["idle_r"])
                player.delay_animation = p.time.get_ticks()

        # Makes sure the players changes animation direction only when he is not in the inventory 
        if player.camera_status != "auto" and \
                (
                        player.inventory.show_menu  # and player.upgrade_station.show_menu
                ) is False:

            if 135 >= angle > 45:
                player.last_movement = "up"
            elif 225 >= angle > 135:
                player.last_movement = "left"
            elif 315 >= angle > 225:
                player.last_movement = "down"
            else:
                player.last_movement = "right"
        # END OF IF STATEMENT, GIVE THE PLAYER DIRECTION
        set_looking(player, player.last_movement, pos)

    update_dash(player, dt, pos)

    # Level UP ring
    # animate_level_up_ring(player)


def set_looking(player, dir_: str, pos):
    """
        This function is for coordinating the hit box
        and also playing the looking animation
    """
    if dir_ == "up":
        player.looking_up, player.looking_down, player.looking_right, player.looking_left = True, False, False, False
    elif dir_ == "down":
        player.looking_up, player.looking_down, player.looking_right, player.looking_left = False, True, False, False
    elif dir_ == "left":
        player.looking_up, player.looking_down, player.looking_right, player.looking_left = False, False, False, True
    elif dir_ == "right":
        player.looking_up, player.looking_down, player.looking_right, player.looking_left = False, False, True, False

    if player.walking:
        temp_anim = player.anim[dir_]
    else:
        temp_anim = player.anim["".join(["idle_", dir_[0]])]
    if player.index_animation > len(temp_anim) - 1:
        player.index_animation = 0

    player.screen.blit(temp_anim[player.index_animation], pos)


def user_interface(player, m, player_pos, dt):
    if player.camera_status != "auto":
        # Health bar
        p.draw.rect(player.screen, player.health_colours['normal'],
            p.Rect(
                player.hp_box_rect.x + 10,
                player.hp_box_rect.y + 10,
                int(player.health / player.health_ratio),
                40)
        )

        # Dash Cool down bar
        p.draw.rect(player.screen, (0, 255, 0),
                    p.Rect(player.hp_box_rect.x + 10, player.hp_box_rect.y + 80, player.dash_width,
                           15))

        # Experience bar
        p.draw.rect(player.screen, (0, 255, 255),
                    p.Rect(player.hp_box_rect.x + 10, player.hp_box_rect.y + 110, player.experience_width, 20))

        # Player UI
        player.screen.blit(player.health_box, player.hp_box_rect)

        # Level status button goes here
        player.upgrade_station.update(player)

        # Inventory Icon
        player.inventory.update(player)

        # quest UI
        player.quest_UI.render()

        if player.upgrade_station.new_points_available != 0 or len(player.inventory.items) != player.inventory.backup_item_len:
            player.show_notif = True

        if player.show_notif:
            p.draw.circle(player.screen, (0, 0, 0), (1185, 94), 11)  # outline
            p.draw.circle(player.screen, (255, 0, 0), (1185, 94), 9)  # red notif
            if player.inventory.show_menu:
                player.inventory.backup_item_len = len(player.inventory.items)
                player.show_notif = False

        # sending its own object in order that the inventory can access to the player's damages

    # recalculate the damages, considering the equipped weapon
    player.modified_damages = player.damage + (player.inventory.get_equipped("Weapon").damage
                                               if player.inventory.get_equipped("Weapon") is not None else 0)
    equipped = player.inventory.get_equipped("Weapon")
    if hasattr(equipped, "special_effect"):
        equipped.special_effect(player)

    # Summon the interaction block only when there is no script or interaction block
    if player.Interactable and player.is_interacting:
        if hasattr(player.interacting_with, "IDENTITY"):
            if player.interacting_with.IDENTITY == "NPC":
                if not player.interacting_with.remove_bubble:
                    player.npc_catalog.draw(player.npc_text, dt)
        # It's an object or other interaction area
        else:
            player.npc_catalog.draw(player.npc_text, dt)


def update_attack(player, pos):
    """ This function is for updating the players hit box based on the mouse position and also updating his animation"""
    if not (player.attacking and player.camera_status != "auto"):
        return

    hitbox_rect = p.Rect(
        player.rect.x - player.camera.offset.x - 50,
        player.rect.y - player.camera.offset.y - 40,
        *player.rect.size
    )

    hit_dict = {
        "up": p.Rect(*hitbox_rect.midtop - vec(41, 0), *player.attacking_hitbox_size),

        "down": p.Rect(*hitbox_rect.midbottom - vec(41, -8), *player.attacking_hitbox_size),

        "left": p.Rect(*hitbox_rect.midleft - vec(28, 0), *player.attacking_hitbox_size),

        "right": p.Rect(*hitbox_rect.midright - vec(50, 0), *player.attacking_hitbox_size)
    }

    # Loading hit box data based perspective
    if player.looking_up:
        player.attacking_hitbox = hit_dict["up"]
    elif player.looking_down:
        player.attacking_hitbox = hit_dict["down"]
    elif player.looking_left:
        player.attacking_hitbox = hit_dict["left"]
    elif player.looking_right:
        player.attacking_hitbox = hit_dict["right"]

    # Blit frame by frame by N ms
    if p.time.get_ticks() - player.delay_attack_animation > player.attack_speed and player.restart_animation:
        a = player.anim
        if player.looking_right:
            curr_anim = a['right_a_1'] if player.current_combo == 1 or player.current_combo == 3 else a['right_a_2']
        elif player.looking_left:
            curr_anim = a['left_a_1'] if player.current_combo == 1 or player.current_combo == 3 else a['left_a_2']
        elif player.looking_down:
            curr_anim = a['down_a_1'] if player.current_combo == 1 or player.current_combo == 3 else a['down_a_2']
        elif player.looking_up:
            curr_anim = a['up_a_1'] if player.current_combo == 1 or player.current_combo == 3 else a['up_a_2']

        # player.attacking = attacking state
        # player.current_combo = 1-2-3 attack combo, 3 does extra dmg
        # player.next_combo_available = di/allow to do next attack
        # player.restart_animation = di/allow the restart of the animation until a next combo is reached
        # player.index_attack_animation = resets animation without impacting frame order
        # player.walking = walking state

        # check if the animation didn't reach its end
        moves = (player.Up, player.Left, player.Right, player.Down)
        if player.index_attack_animation + 1 < len(curr_anim):
            player.delay_attack_animation = p.time.get_ticks()  # reset the delay
            player.attacking_frame = curr_anim[
                player.index_attack_animation + 1]  # change the current animation frame
            player.index_attack_animation += 1  # increment the animation index
        else:
            player.restart_animation = False
            player.index_attack_animation = 0
            player.next_combo_available = True

    # This resets the attack animation based on other combat rules
    if player.current_combo == player.last_attack and not player.restart_animation and \
            not player.index_attack_animation:
        player.attacking = False
        player.current_combo = 0
        player.index_attack_animation = 0
        player.next_combo_available = True
        player.restart_animation = True

    # Reset animation when player's is not repeating clicks
    if p.time.get_ticks() - player.last_attacking_click > player.attack_cooldown - 30:
        player.attacking = False
        player.current_combo = 0
        player.index_attack_animation = 0
        player.next_combo_available = True
        player.restart_animation = True

    # Last step draw the animation
    player.screen.blit(player.attacking_frame, pos)
