import pygame  


def check_content(player, pos):
    position = (player.rect.topleft - player.camera.offset.xy)
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

                            # Get npc's text
                            player.npc_text = obj.tell_story

                            # Stop browsing to reduce calcs
                            break
            elif obj.IDENTITY == "PROP":
                if obj.name == "chest":  # MUST BE BEFORE checking collision to avoid attribute errors
                    if itr_box.colliderect(obj.interaction_rect):
                        obj.on_interaction(player)  # Run Chest opening
