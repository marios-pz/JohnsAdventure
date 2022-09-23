import pygame as p


def start_dash(player):
    if not player.dashing and player.dash_available:
        player.dashing = True
        player.dash_start = p.time.get_ticks()
        player.dash_available = False
        player.delay_increasing_dash = p.time.get_ticks()
        if player.looking_down:
            player.dashing_direction = "down"
        elif player.looking_left:
            player.dashing_direction = "left"
        elif player.looking_right:
            player.dashing_direction = "right"
        else:
            player.dashing_direction = "up"


def update_dash(player, dt, pos):
    if player.dashing:

        if p.time.get_ticks() - player.delay_dash_animation > 50:
            player.delay_dash_animation = p.time.get_ticks()
            match player.dashing_direction:  # lgtm [py/syntax-error]
                case "left":
                    anim = player.anim['dash_l']
                case "right":
                    anim = player.anim['dash_r']
                case "up":
                    anim = player.anim['dash_u']
                case "down":
                    anim = player.anim['dash_d']
            player.index_dash_animation = (player.index_dash_animation + 1) % len(anim)
            player.current_dashing_frame = anim[player.index_dash_animation]
        player.screen.blit(player.current_dashing_frame, pos)

        if p.time.get_ticks() - player.dash_start > 200:
            player.dashing = False
            player.last_dash_end = p.time.get_ticks()
            player.delay_increasing_dash = player.last_dash_end
            player.dash_width = 0

        if p.time.get_ticks() - player.delay_increasing_dash > 2:
            player.delay_attack_animation = p.time.get_ticks()
            freq = 25  # Frequency of the dash
            if player.move_ability[player.dashing_direction]:
                match player.dashing_direction:
                    case "up":
                        player.rect.y -= dt * freq + 8
                    case "down":
                        player.rect.y += dt * freq + 8
                    case "right":
                        player.rect.x += dt * freq + 8
                    case "left":
                        player.rect.x -= dt * freq + 8
    else:
        #  Update the  UI

        if p.time.get_ticks() - player.delay_increasing_dash > player.dash_cd / ((11 / 3) * 2):
            player.dash_width += 200 / ((11 / 3) * 2)
            player.delay_increasing_dash = p.time.get_ticks()

        if p.time.get_ticks() - player.last_dash_end > player.dash_cd:
            player.dash_available = True
            player.dash_width = 200
