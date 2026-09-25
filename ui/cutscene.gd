extends CanvasLayer
## Cutscene player (autoload "Cutscene"), driven by data/cutscenes.json.
##
## Letterbox bars slide in, then each step moves/zooms John's camera, types
## text into the bottom bar (or the screen centre) and waits. While `playing`
## is true, John and enemies ignore input/AI. See the "_doc" key in the JSON
## for the step format.

signal finished(id: String)

const DATA_PATH := "res://data/cutscenes.json"
const BAR_HEIGHT := 90.0
const BAR_TIME := 0.8
const IMAGES := {"cutscene1": preload("res://assets/sprites/cutscenes/cutscene1.png")}

var playing := false
var _cutscenes: Dictionary = {}

@onready var _top: ColorRect = $TopBar
@onready var _bottom: ColorRect = $BottomBar
@onready var _image: TextureRect = $Image
@onready var _black: ColorRect = $Black
@onready var _text: Label = $BottomBar/Text
@onready var _centered: Label = $CenteredText


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_cutscenes = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	_cutscenes.erase("_doc")
	_reset()


## First unseen cutscene of `level_id` whose trigger step is done, or "".
func pending_for(level_id: String) -> String:
	for id in _cutscenes:
		var cutscene: Dictionary = _cutscenes[id]
		if cutscene.level == level_id and not id in Game.cutscenes_played \
				and Quests.is_done(cutscene.after_step):
			return id
	return ""


func play(id: String) -> void:
	var cutscene: Dictionary = _cutscenes[id]
	playing = true
	Game.cutscenes_played.append(id)
	Game.close_dialogue()
	var player := get_tree().get_first_node_in_group("player") as Player
	var camera := player.camera
	camera.top_level = true  # detach from John so the camera can travel
	camera.global_position = player.global_position

	await _bars(true)
	for step: Dictionary in cutscene.steps:
		await _play_step(step, camera)
	_image.hide()
	_black.hide()
	await _bars(false)

	if is_instance_valid(player):
		var back := create_tween().set_trans(Tween.TRANS_SINE)
		back.tween_property(camera, "global_position", player.global_position, 0.4)
		back.parallel().tween_property(camera, "zoom", Vector2.ONE, 0.4)
		await back.finished
		camera.top_level = false
		camera.position = Vector2.ZERO
	playing = false
	finished.emit(id)
	if cutscene.has("then"):
		Game.travel(cutscene.then)


func _play_step(step: Dictionary, camera: Camera2D) -> void:
	var duration: float = step.get("duration", 0) / 1000.0
	var wait := duration

	var image: String = step.get("image", "")
	_black.visible = image != ""
	_image.visible = IMAGES.has(image)
	if _image.visible:
		_image.texture = IMAGES[image]

	if step.has("pos"):
		var target := Vector2(step.pos[0], step.pos[1])
		if duration > 0.0:
			create_tween().set_trans(Tween.TRANS_SINE).tween_property(camera, "global_position", target, duration)
		else:
			camera.global_position = target
	if step.has("zoom"):
		var zoom := Vector2.ONE * float(step.zoom)
		var zoom_time: float = step.get("zoom_duration", 0) / 1000.0
		if zoom_time > 0.0:
			create_tween().set_trans(Tween.TRANS_SINE).tween_property(camera, "zoom", zoom, zoom_time)
			wait = maxf(wait, zoom_time)
		else:
			camera.zoom = zoom

	_type(_text, step.get("text", ""), step.get("text_dt", 1000) / 1000.0)
	_type(_centered, step.get("centered_text", ""), step.get("centered_text_dt", 1000) / 1000.0)
	await get_tree().create_timer(wait + step.get("waiting_end", 0) / 1000.0).timeout


func _type(label: Label, text: String, duration: float) -> void:
	label.text = text.format({
		"inventory": Game.key_name("inventory"),
		"dash": Game.key_name("dash"),
		"heal": Game.key_name("heal"),
	})
	label.visible_ratio = 0.0
	if text != "":
		create_tween().tween_property(label, "visible_ratio", 1.0, duration)


func _bars(show: bool) -> void:
	var tween := create_tween().set_parallel().set_trans(Tween.TRANS_CUBIC)
	tween.tween_property(_top, "position:y", 0.0 if show else -BAR_HEIGHT, BAR_TIME)
	var height := get_viewport().get_visible_rect().size.y  # taller than 720 on 16:10 screens
	tween.tween_property(_bottom, "position:y", height - BAR_HEIGHT if show else height, BAR_TIME)
	await tween.finished


func _reset() -> void:
	_top.position.y = -BAR_HEIGHT
	_bottom.position.y = get_viewport().get_visible_rect().size.y
	_image.hide()
	_black.hide()
	_text.text = ""
	_centered.text = ""
