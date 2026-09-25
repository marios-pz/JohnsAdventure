extends Control
## Title screen: Continue / New Game / Quit.
## Fully usable with a controller (buttons take focus).


func _ready() -> void:
	get_tree().paused = false
	RenderingServer.set_default_clear_color(Color.BLACK)
	Audio.play_music("main_theme")
	%ContinueButton.visible = Game.has_save()
	%ContinueButton.pressed.connect(_start.bind(true))
	%NewGameButton.pressed.connect(_start.bind(false))
	%QuitButton.pressed.connect(get_tree().quit)
	%QuitButton.visible = not OS.has_feature("web")  # a browser tab can't quit itself
	(%ContinueButton if Game.has_save() else %NewGameButton).grab_focus()
	# The two menu backgrounds alternate, like the original title screen.
	var tween := create_tween().set_loops()
	tween.tween_callback(func() -> void: %Background.texture = preload("res://assets/ui/menu_bg2.png"))
	tween.tween_interval(2.25)
	tween.tween_callback(func() -> void: %Background.texture = preload("res://assets/ui/menu_bg1.png"))
	tween.tween_interval(2.25)


func _start(from_save: bool) -> void:
	for button: Button in %Buttons.get_children():
		button.disabled = true  # no double start while the music fades
	if from_save:
		Game.load_game()
	else:
		Game.new_game()
	await Audio.fade_out_music()
	get_tree().change_scene_to_file("res://main.tscn")
