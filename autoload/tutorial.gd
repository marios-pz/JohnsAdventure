extends Node
## Guided tutorial (autoload "Tutorial"), driven by data/tutorial.json.
##
## Shows one tip at a time and ticks it off when John actually performs the
## action (`done_on`). Gameplay code reports actions with Tutorial.notify():
## "move", "interact", "weapon", "attack", "combo", "dash", "heal", "inventory".
## A tip only shows in its `level` ("" = anywhere) once `after_step` is done.

signal changed

const DATA_PATH := "res://data/tutorial.json"
const MOVE_DISTANCE := 250.0  ## px John must walk to finish the "move" tip

var _tips: Array = []
var _done: Array[String] = []
var _walked := 0.0


func _ready() -> void:
	_tips = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH)).tips
	Quests.step_completed.connect(func(_q: String, _s: String) -> void: changed.emit())


## The tip to show right now, or {}.
func current() -> Dictionary:
	for tip in _tips:
		if tip.id in _done:
			continue
		if (tip.level == "" or tip.level == Game.current_level) and Quests.is_done(tip.after_step):
			return tip
		return {}  # tips are sequential: wait until this one becomes available
	return {}


## Tip text with the input prompts for the current device filled in.
func text_of(tip: Dictionary) -> String:
	return tip.text.format({
		"move": "the left stick" if Game.gamepad else "W A S D",
		"aim": "right stick" if Game.gamepad else "mouse",
		"attack": Game.key_name("attack"), "interact": Game.key_name("interact"),
		"dash": Game.key_name("dash"), "heal": Game.key_name("heal"),
		"inventory": Game.key_name("inventory"),
	})


func notify(action: String) -> void:
	var tip := current()
	if tip.is_empty() or tip.done_on != action:
		return
	_done.append(tip.id)
	Audio.play_sfx("select", 0.35)
	changed.emit()


## Called by the player every frame with the distance walked.
func walked(distance: float) -> void:
	_walked += distance
	if _walked >= MOVE_DISTANCE:
		_walked = 0.0
		notify("move")


func to_dict() -> Array:
	return _done.duplicate()


func from_dict(done: Array) -> void:
	_done.assign(done)
	changed.emit()
