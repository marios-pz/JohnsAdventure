extends Control
## Title screen: Continue / New Game / How to Play / Quit.
## Fully usable with a controller (buttons take focus, B closes How to Play).


func _ready() -> void:
	get_tree().paused = false
	RenderingServer.set_default_clear_color(Color.BLACK)
	Audio.play_music("main_theme")
	%ContinueButton.visible = Game.has_save()
	%ContinueButton.pressed.connect(_continue)
	%NewGameButton.pressed.connect(_new_game)
	%HowToPlayButton.pressed.connect(_show_how_to_play)
	%QuitButton.pressed.connect(get_tree().quit)
	%QuitButton.visible = not OS.has_feature("web")  # a browser tab can't quit itself
	%HowToPlay.hide()
	%HowToPlay.closed.connect(func() -> void:
		%Buttons.show()
		%HowToPlayButton.grab_focus())
	(%ContinueButton if Game.has_save() else %NewGameButton).grab_focus()
	# The two menu backgrounds alternate, like the original title screen.
	var tween := create_tween().set_loops()
	tween.tween_callback(func() -> void: %Background.texture = preload("res://assets/ui/menu_bg2.png"))
	tween.tween_interval(2.25)
	tween.tween_callback(func() -> void: %Background.texture = preload("res://assets/ui/menu_bg1.png"))
	tween.tween_interval(2.25)


func _unhandled_input(event: InputEvent) -> void:
	if %HowToPlay.visible and event.is_action_pressed("ui_cancel"):
		%HowToPlay.close()
		get_viewport().set_input_as_handled()


func _continue() -> void:
	Game.load_game()
	get_tree().change_scene_to_file("res://main.tscn")


func _new_game() -> void:
	Game.new_game()
	get_tree().change_scene_to_file("res://main.tscn")


func _show_how_to_play() -> void:
	%Buttons.hide()
	%HowToPlay.open()
