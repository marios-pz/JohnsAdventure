extends CanvasLayer
## Cutscene player (autoload "Cutscene"), driven by data/cutscenes.json.
##
## Letterbox bars slide in, then each step moves/zooms John's camera, types
## text into the bottom bar (or the screen centre) and waits: steps with text wait
## for Enter/A (the first press finishes the typing), the rest for their duration.
## A "continue" hint appears when the player idles on finished text. While `playing`
## is true, John and enemies ignore input/AI. See the "_doc" key in the JSON
## for the step format.

signal finished(id: String)
## A "boom" step went off: levels now reveal what the story step unlocked.
signal released

const DATA_PATH := "res://data/cutscenes.json"
const BAR_HEIGHT := 90.0
const BAR_TIME := 0.8
const HINT_DELAY := 1.5          ## idle seconds on finished text before the continue hint
const RADIAL := preload("res://assets/sprites/lights/radial.png")
const IMAGES := {"cutscene1": preload("res://assets/sprites/cutscenes/cutscene1.png")}

var playing := false
## True while a cutscene with a "boom" step has not reached it yet: levels hold
## back newly unlocked nodes (and kill steps wait) so they appear on the boom.
var holding := false
var _typers := {}                ## label -> its typing tween, so a press can finish it
var _waiting := false
var _pressed := false
var _hint := Label.new()
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
	_hint.add_theme_font_size_override("font_size", 13)
	_hint.modulate = Color(1, 1, 1, 0.75)
	_bottom.add_child(_hint)
	_hint.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
	_hint.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_hint.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_hint.position -= Vector2(24, 10)
	_hint.hide()
	_reset()


func _input(event: InputEvent) -> void:
	if _waiting and event.is_action_pressed("ui_accept") and not event.is_echo():
		get_viewport().set_input_as_handled()  # don't also interact / open things
		_pressed = true


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
	holding = cutscene.steps.any(func(s: Dictionary) -> bool: return s.has("boom"))
	Game.cutscenes_played.append(id)
	Game.close_dialogue()
	var player := get_tree().get_first_node_in_group("player") as Player
	var camera := player.camera
	camera.top_level = true  # detach from John so the camera can travel
	camera.global_position = player.global_position

	_show_image(cutscene.steps[0].get("image", ""))  # cover the level now, not after the bars
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
	_release()  # safety net: never keep things hidden past the cutscene
	playing = false
	finished.emit(id)
	if cutscene.has("then"):
		Game.travel(cutscene.then)


func _play_step(step: Dictionary, camera: Camera2D) -> void:
	var duration: float = step.get("duration", 0) / 1000.0
	var wait := duration

	_show_image(step.get("image", ""))
	if step.has("boom"):
		_boom(Vector2(step.boom[0], step.boom[1]))

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
	if _text.text != "" or _centered.text != "":
		await _wait_for_continue()
	else:
		await get_tree().create_timer(wait + step.get("waiting_end", 0) / 1000.0).timeout


## Waits for Enter/A. A press while text is still typing shows it all instead.
func _wait_for_continue() -> void:
	_pressed = false
	_waiting = true
	var idle := 0.0
	while true:
		await get_tree().process_frame
		var typing := _is_typing(_text) or _is_typing(_centered)
		if _pressed:
			_pressed = false
			if not typing:
				break
			for label: Label in _typers:
				_typers[label].kill()
				label.visible_ratio = 1.0
			idle = 0.0
		elif not typing:
			idle += get_process_delta_time()
			if idle >= HINT_DELAY and not _hint.visible:
				_hint.text = "[%s] Continue" % Game.key_name("ui_accept")
				_hint.show()
	_waiting = false
	_hint.hide()


func _is_typing(label: Label) -> bool:
	return label.text != "" and label.visible_ratio < 1.0


## Purple shockwave at `at` (world position); the held-back nodes appear with it.
func _boom(at: Vector2) -> void:
	var player := get_tree().get_first_node_in_group("player") as Player
	if player == null:
		_release()
		return
	var boom := Node2D.new()
	boom.position = at
	boom.z_index = 45
	player.get_parent().add_child(boom)

	# Normal blending: additive purple washes out to white over bright grass.
	var flash := Sprite2D.new()
	flash.texture = RADIAL
	flash.modulate = Color(0.55, 0.15, 0.85, 0.8)
	flash.scale = Vector2.ONE * 0.3
	boom.add_child(flash)
	var ring := Line2D.new()
	for i in 49:
		ring.add_point(Vector2.from_angle(TAU * i / 48.0) * 100.0)
	ring.width = 14.0
	ring.default_color = Color(0.62, 0.25, 1.0)
	ring.scale = Vector2.ONE * 0.1
	boom.add_child(ring)
	var wave := boom.create_tween().set_parallel().set_trans(Tween.TRANS_EXPO).set_ease(Tween.EASE_OUT)
	wave.tween_property(flash, "scale", Vector2.ONE * 7.0, 0.7)
	wave.tween_property(flash, "modulate:a", 0.0, 0.9)
	wave.tween_property(ring, "scale", Vector2.ONE * 9.0, 0.8)
	wave.tween_property(ring, "width", 2.0, 0.8)
	wave.tween_property(ring, "modulate:a", 0.0, 0.8)
	wave.chain().tween_callback(boom.queue_free)

	var sparks := CPUParticles2D.new()
	sparks.one_shot = true
	sparks.explosiveness = 1.0
	sparks.amount = 120
	sparks.lifetime = 0.9
	sparks.spread = 180.0
	sparks.gravity = Vector2.ZERO
	sparks.initial_velocity_min = 300.0
	sparks.initial_velocity_max = 900.0
	sparks.damping_min = 400.0
	sparks.damping_max = 700.0
	sparks.scale_amount_min = 4.0
	sparks.scale_amount_max = 9.0
	sparks.color = Color(0.6, 0.25, 0.95)
	boom.add_child(sparks)
	sparks.emitting = true

	player.shake(18.0)
	Audio.play_sfx("magic", 0.9)
	_release()


func _release() -> void:
	if holding:
		holding = false
		released.emit()


## "" = none, "black" = black screen, else a key of IMAGES.
func _show_image(image: String) -> void:
	_black.visible = image != ""
	_image.visible = IMAGES.has(image)
	if _image.visible:
		_image.texture = IMAGES[image]


func _type(label: Label, text: String, duration: float) -> void:
	label.text = text.format({
		"inventory": Game.key_name("inventory"),
		"dash": Game.key_name("dash"),
		"parry": Game.key_name("parry"),
		"heal": Game.key_name("heal"),
	})
	label.visible_ratio = 0.0
	if text != "":
		_typers[label] = create_tween()
		_typers[label].tween_property(label, "visible_ratio", 1.0, duration)


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
