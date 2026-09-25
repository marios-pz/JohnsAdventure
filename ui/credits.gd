extends Control
## Scrolling end credits. Any key (or the end of the scroll) returns to the title.

const SPEED := 45.0

@onready var _lines: Control = %Lines


func _ready() -> void:
	Audio.play_music("credits")
	_lines.position.y = size.y


func _process(delta: float) -> void:
	_lines.position.y -= SPEED * delta
	if _lines.position.y < -_lines.size.y:
		_back()


func _unhandled_input(event: InputEvent) -> void:
	if _lines.position.y > size.y - 120.0:
		return  # ignore the key press that finished the last cutscene
	if event.is_pressed() and not event.is_echo() and (event is InputEventKey or event is InputEventMouseButton):
		_back()


func _back() -> void:
	if not is_processing():
		return  # already leaving
	set_process(false)
	await Audio.fade_out_music()
	get_tree().change_scene_to_file("res://ui/main_menu.tscn")
