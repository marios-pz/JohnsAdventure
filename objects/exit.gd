class_name Exit
extends Area2D
## Level transition.
## Without a `prompt`, walking into it travels right away (paths, cave tunnels).
## With one, John presses interact to see the prompt, then again to confirm (doors).

@export var target := ""             ## level id, or "credits"
@export var display_name := ""       ## shown in the HUD interaction hint
@export_multiline var prompt := ""


func _ready() -> void:
	if prompt == "":
		collision_layer = 0
		collision_mask = 2  # John's body
		body_entered.connect(func(body: Node2D) -> void:
			if body is Player:
				Game.travel(target))
	else:
		collision_layer = 8  # "interactables", found by John's Interactor
		collision_mask = 0


func interact() -> void:
	if Game.dialogue_source == self:
		Game.travel(target)
	else:
		Game.open_dialogue("%s\n[%s] Yes" % [prompt, Game.key_name("interact")], self)
