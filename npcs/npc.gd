class_name NPC
extends CharacterBody2D
## A friendly character John can talk to.
##
## What they say comes from data/dialogue.json: the last entry whose `after`
## quest step is done. Pressing interact again turns the page. Talking to the
## NPC a quest step is waiting for completes that step instead (a cutscene
## usually follows). Wandering NPCs pace left/right from where they stand.

const DIALOGUE_PATH := "res://data/dialogue.json"

static var _dialogue := {}

@export var id := ""                 ## key in dialogue.json and quest target id
@export var display_name := ""
@export var wander_distance := 0.0   ## 0 = stands still
@export var speed := 60.0

var _origin_x := 0.0
var _direction := 1.0
var _lines: Array = []
var _page := 0

@onready var sprite: AnimatedSprite2D = $Sprite


func _ready() -> void:
	_origin_x = position.x
	sprite.play("walk" if wander_distance > 0.0 else "idle")


func _physics_process(_delta: float) -> void:
	if wander_distance <= 0.0:
		return
	if Game.dialogue_source == self or Cutscene.playing:
		sprite.pause()
		return
	if position.x >= _origin_x + wander_distance:
		_direction = -1.0
	elif position.x <= _origin_x:
		_direction = 1.0
	velocity = Vector2(_direction * speed, 0.0)
	move_and_slide()
	if is_on_wall():
		_direction = -_direction
	sprite.flip_h = _direction < 0.0
	sprite.play("walk")


func interact() -> void:
	if Quests.notify_interact(id):
		Game.close_dialogue()
		return
	if Game.dialogue_source != self:
		_lines = _current_lines()
		_page = 0
	else:
		_page += 1
	if _page < _lines.size():
		Game.open_dialogue(_lines[_page], self)
	else:
		Game.close_dialogue()


func set_highlight(on: bool) -> void:
	sprite.self_modulate = Color(1.35, 1.35, 1.35) if on else Color.WHITE


func _current_lines() -> Array:
	if _dialogue.is_empty():
		_dialogue = JSON.parse_string(FileAccess.get_file_as_string(DIALOGUE_PATH))
	var lines: Array = []
	for entry in _dialogue.get(id, []):
		if Quests.is_done(entry.after):
			lines = entry.lines
	return lines
