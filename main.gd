extends Node
## Gameplay root: loads levels, spawns John and wires death to the HUD.

const PLAYER := preload("res://player/player.tscn")

var level: Level
var _travelling := false

@onready var hud: Hud = $HUD


func _ready() -> void:
	Game.travel_requested.connect(_travel)
	Game.died.connect(hud.show_death)
	_travel(Game.current_level, "", Game.saved_position)


func _travel(level_id: String, from_level: String, position: Variant) -> void:
	if _travelling:
		return
	_travelling = true
	get_tree().paused = true
	await hud.fade(1.0)

	if level_id == "credits":
		Game.save_game()  # keep the ending as seen, or Continue replays it
		get_tree().paused = false
		get_tree().change_scene_to_file("res://ui/credits.tscn")
		return

	if level:
		remove_child(level)
		level.queue_free()
	Game.current_level = level_id
	level = load("res://levels/%s.tscn" % level_id).instantiate()
	add_child(level)
	move_child(level, 0)
	level.add_player(PLAYER.instantiate(), from_level, position)
	Quests.enter_level(level_id)
	await get_tree().process_frame  # let quest gates and "reach" steps settle
	var player := get_tree().get_first_node_in_group("player") as Player
	Game.checkpoint(player.global_position)
	Game.save_game()

	get_tree().paused = false
	hud.show_level_title(level.title)
	level.start()  # under the black fade, so John never shows before an entry cutscene
	await hud.fade(0.0)
	_travelling = false
