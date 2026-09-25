class_name Level
extends Node2D
## Base script of every level scene.
##
## Scene layout convention:
##   Ground         flat decoration drawn under everything (roads, grass, floor)
##   World          y-sorted: props, walls, NPCs, enemies, chests. John is added here.
##   Exits          Exit areas
##   Spawns         one Marker2D per entrance, named after the level John arrives from
##   CanvasModulate optional: present = dark level (lights on), absent = daylight
##
## Quest gates: any node may carry the metadata `show_after` and/or `hide_after`
## (quest step names). It is only part of the scene while `show_after` is done
## and `hide_after` is not, and it appears/disappears live as the story advances.

@export var level_id := ""
@export var title := ""
@export var music := ""                     ## "" keeps the current track
@export var background := Color.BLACK       ## clear colour behind everything
@export var camera_limits := Rect2()        ## zero size = camera follows freely
@export var start_position := Vector2.ZERO  ## fallback spawn (new game)

var _gated := {}        ## node -> parent it lives under
var _started := false

@onready var world: Node2D = $World


func _ready() -> void:
	var darkness := get_node_or_null("CanvasModulate") as CanvasModulate
	RenderingServer.set_default_clear_color(background * (darkness.color if darkness else Color.WHITE))
	if darkness == null:
		for light in find_children("*", "Light2D", true, false):
			light.hide()  # street lamps etc. are off during the day
	if music != "":
		Audio.play_music(music)
	for node in find_children("*", "", true, false):
		if node.has_meta("show_after") or node.has_meta("hide_after"):
			_gated[node] = node.get_parent()
	_apply_gates.call_deferred(false)
	Quests.step_completed.connect(_on_step_completed)


func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE:
		for node in _gated:
			if is_instance_valid(node) and not node.is_inside_tree():
				node.free()


func add_player(player: Player, from_level: String, position: Variant) -> void:
	world.add_child(player)
	var spawn := get_node_or_null("Spawns/" + from_level) as Node2D if from_level != "" else null
	if position is Vector2:
		player.global_position = position
	elif spawn:
		player.global_position = spawn.global_position
	else:
		player.global_position = start_position
	_apply_camera_limits(player.camera)
	get_viewport().size_changed.connect(_apply_camera_limits.bind(player.camera))
	player.camera.reset_smoothing()


## Camera limits, widened symmetrically when the screen is wider/taller than the
## level (ultrawide monitors), so small rooms stay centred instead of hugging a corner.
func _apply_camera_limits(camera: Camera2D) -> void:
	if not camera_limits.has_area() or not is_instance_valid(camera):
		return
	var view := get_viewport().get_visible_rect().size
	var limits := camera_limits.grow_individual(
			maxf(0.0, (view.x - camera_limits.size.x) / 2.0), maxf(0.0, (view.y - camera_limits.size.y) / 2.0),
			maxf(0.0, (view.x - camera_limits.size.x) / 2.0), maxf(0.0, (view.y - camera_limits.size.y) / 2.0))
	camera.limit_left = int(limits.position.x)
	camera.limit_top = int(limits.position.y)
	camera.limit_right = int(limits.end.x)
	camera.limit_bottom = int(limits.end.y)


## Called by Main once the fade-in is over.
func start() -> void:
	_started = true
	_try_cutscene()


func _on_step_completed(_quest: String, _step: String) -> void:
	_apply_gates.call_deferred(true)
	if _started:
		_try_cutscene.call_deferred()


func _apply_gates(live: bool) -> void:
	for node in _gated.keys():
		if not is_instance_valid(node):
			_gated.erase(node)
			continue
		var active: bool = Quests.is_done(node.get_meta("show_after", "")) \
				and not (node.has_meta("hide_after") and Quests.is_done(node.get_meta("hide_after")))
		if active and not node.is_inside_tree():
			_gated[node].add_child(node)
			if live and node.has_method("on_revealed"):
				node.on_revealed()
		elif not active and node.is_inside_tree():
			node.get_parent().remove_child(node)


func _try_cutscene() -> void:
	if Cutscene.playing:
		return
	var id := Cutscene.pending_for(level_id)
	if id != "":
		Cutscene.play(id)
