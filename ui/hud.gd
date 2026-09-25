class_name Hud
extends CanvasLayer
## In-game UI: health/dash/xp bars, objective tracker, tutorial tips, toasts,
## interaction hint, dialogue box, boss bar, the inventory/stats/quest menu,
## pause (with How to Play) and death screens, and the black fade between levels.
## Every element is anchored, so wider screens (ultrawide) just get more room.
## Menus take keyboard/controller focus when opened.
##
## It only reads Game/Quests state and listens to their signals; gameplay
## never calls into the HUD except Main (fade, level title, death).

const HEALTH_WIDTH := 162.0  ## widths match the holes in the UI sheet's health box (x3)
const DASH_WIDTH := 192.0
const XP_WIDTH := 192.0
const TOAST_TIME := 3.5

var _focus_name := ""

@onready var _health_fill: ColorRect = %HealthFill
@onready var _health_trail: ColorRect = %HealthTrail
@onready var _dash_fill: ColorRect = %DashFill
@onready var _xp_fill: ColorRect = %XpFill
@onready var _dialogue: Control = %Dialogue
@onready var _dialogue_text: Label = %DialogueText
@onready var _menus: Control = %Menus
@onready var _pause: Control = %Pause
@onready var _death: Control = %Death
@onready var _fade: ColorRect = %Fade
@onready var _boss_bar: Control = %BossBar


func _ready() -> void:
	Game.stats_changed.connect(_refresh)
	Game.inventory_changed.connect(_refresh)
	Game.dialogue_opened.connect(_on_dialogue_opened)
	Game.dialogue_closed.connect(_dialogue.hide)
	Game.focus_changed.connect(_on_focus_changed)
	Game.input_device_changed.connect(func(_pad: bool) -> void:
		_on_focus_changed(_focus_name)
		_refresh_tutorial()
		_refresh())
	Tutorial.changed.connect(_refresh_tutorial)
	Game.leveled_up.connect(func(new_level: int) -> void:
		_toast("Level up! Level %d - spend your upgrade point (%s)" % [new_level, Game.key_name("inventory")]))
	Quests.step_completed.connect(func(_quest: String, step: String) -> void:
		_toast("Completed: " + step)
		_refresh())
	Quests.step_started.connect(func(_quest: String, step: String) -> void:
		_toast("New objective: " + step))
	Quests.quest_finished.connect(func(quest: String) -> void:
		_toast("Quest complete: " + quest))
	%InventoryButton.pressed.connect(_toggle_menu)
	%CloseMenuButton.pressed.connect(_toggle_menu)
	%ResumeButton.pressed.connect(_toggle_pause)
	%QuitButton.pressed.connect(_save_and_quit)
	%HowToPlayButton.pressed.connect(func() -> void:
		%PausePanel.hide()
		%HowToPlay.open())
	%HowToPlay.closed.connect(func() -> void:
		%PausePanel.show()
		%HowToPlayButton.grab_focus())
	%DamageButton.pressed.connect(Game.upgrade.bind("damage"))
	%EnduranceButton.pressed.connect(Game.upgrade.bind("endurance"))
	%CritButton.pressed.connect(Game.upgrade.bind("crit_chance"))
	for node: Control in [_dialogue, _menus, _pause, _death, _boss_bar, %HowToPlay]:
		node.hide()
	_fade.color.a = 1.0
	_refresh()
	_refresh_tutorial()


func _process(delta: float) -> void:
	visible = not Cutscene.playing
	var player := get_tree().get_first_node_in_group("player") as Player
	if player:
		_dash_fill.size.x = DASH_WIDTH * player.dash_charge
	_health_trail.size.x = lerpf(_health_trail.size.x, _health_fill.size.x, 4.0 * delta)
	var boss := get_tree().get_first_node_in_group("boss") as Boss
	_boss_bar.visible = boss != null and not boss.dead
	if _boss_bar.visible:
		%BossName.text = boss.display_name
		%BossFill.size.x = (%BossBack.size.x - 8.0) * clampf(float(boss.hp) / boss.max_hp, 0.0, 1.0)


func _unhandled_input(event: InputEvent) -> void:
	if _death.visible:
		if event.is_action_pressed("interact"):
			_death.hide()
			Game.respawn()
		return
	if Cutscene.playing or Game.health <= 0 or _fade.color.a > 0.0:
		return  # during a level fade Main owns get_tree().paused
	if event.is_action_pressed("ui_cancel") and (_menus.visible or %HowToPlay.visible):
		if %HowToPlay.visible:
			%HowToPlay.close()
		else:
			_toggle_menu()
	elif event.is_action_pressed("pause"):
		if _menus.visible:
			_toggle_menu()
		else:
			_toggle_pause()
	elif event.is_action_pressed("inventory") and not _pause.visible:
		_toggle_menu()
	else:
		return
	get_viewport().set_input_as_handled()


# --- Called by Main ------------------------------------------------------------------

## Tweens the black overlay to `alpha` (1 = black). Await it.
func fade(alpha: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade, "color:a", alpha, 0.35)
	await tween.finished


func show_level_title(title: String) -> void:
	_refresh_tutorial()  # tips can be tied to a level
	var label: Label = %LevelTitle
	label.text = title
	label.modulate.a = 0.0
	var tween := create_tween()
	tween.tween_property(label, "modulate:a", 1.0, 0.5).set_delay(0.3)
	tween.tween_interval(1.5)
	tween.tween_property(label, "modulate:a", 0.0, 0.6)


func show_death() -> void:
	Game.close_dialogue()
	%DeathHint.text = "Press %s to try again" % Game.key_name("interact")
	_death.modulate.a = 0.0
	_death.show()
	create_tween().tween_property(_death, "modulate:a", 1.0, 1.2)


# --- Internals ------------------------------------------------------------------------

func _refresh() -> void:
	var weapon := Game.weapon()
	_health_fill.size.x = HEALTH_WIDTH * float(Game.health) / Game.max_health
	_xp_fill.size.x = XP_WIDTH * float(Game.experience) / Game.xp_to_next()
	%LevelLabel.text = str(Game.level)
	%Potions.text = "Potions x%d  (%s)" % [Game.potions, Game.key_name("heal")]
	%Coins.text = "Coins %d" % Game.coins
	%NotifDot.visible = Game.upgrade_points > 0 or Game.weapons.size() > Game.seen_items
	%Objective.text = _objective()

	# Inventory
	var list: Control = %ItemList
	for child in list.get_children():
		child.queue_free()
	for id in Game.weapons:
		var item: Weapon = Game.WEAPONS[id]
		var button := Button.new()
		button.text = "%s%s   +%d dmg" % ["> " if id == Game.equipped else "", item.display_name, item.damage]
		button.icon = item.icon
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.pressed.connect(func() -> void:
			Game.toggle_equip(id)
			_focus_first.call_deferred(list))  # the pressed button was just freed
		list.add_child(button)
	if Game.weapons.is_empty():
		var empty := Label.new()
		empty.text = "Nothing yet. Chests hold treasure!"
		list.add_child(empty)
	%InventoryFooter.text = "Items %d/%d" % [Game.weapons.size(), Game.MAX_ITEMS]

	# Stats
	var points := Game.upgrade_points
	%PointsLabel.text = "Upgrade points: %d" % points
	%DamageButton.text = "Damage  %d%s   (+2)" % [Game.damage, "  +%d" % weapon.damage if weapon else ""]
	%EnduranceButton.text = "Endurance  %d   (+1)" % Game.endurance
	%CritButton.text = "Crit chance  %d%%   (+2%%)" % roundi((Game.crit_chance + (weapon.crit_chance if weapon else 0.0)) * 100)
	for button: Button in [%DamageButton, %EnduranceButton, %CritButton]:
		button.disabled = points == 0

	# Quest log: finished steps struck through, current step highlighted, future hidden.
	var quest_log := ""
	for quest in Quests.quest_names():
		quest_log += "[b]%s[/b]\n" % quest
		var current: Dictionary = Quests.current_step(quest)
		for step in Quests.steps_of(quest):
			if Quests.is_done(step.name):
				quest_log += "[color=#6b4a1a][s]%s[/s][/color]\n" % step.name
			elif step == current:
				quest_log += "> %s\n" % step.name
				break
		quest_log += "\n"
	%QuestLog.text = quest_log


func _objective() -> String:
	for quest in Quests.quest_names():
		var step: Dictionary = Quests.current_step(quest)
		if not step.is_empty():
			return step.name
	return "Chapter 1 complete!"


func _toggle_menu() -> void:
	_menus.visible = not _menus.visible
	get_tree().paused = _menus.visible
	if _menus.visible:
		Game.seen_items = Game.weapons.size()
		_refresh()
		Tutorial.notify("inventory")
		_focus_first.call_deferred(%ItemList)


func _toggle_pause() -> void:
	_pause.visible = not _pause.visible
	%PausePanel.show()
	%HowToPlay.hide()
	get_tree().paused = _pause.visible
	if _pause.visible:
		%ResumeButton.grab_focus()


## Gives controller/keyboard focus to the first button in `container` (or Close).
func _focus_first(container: Control) -> void:
	for child in container.get_children():
		if child is Button and not child.is_queued_for_deletion():
			child.grab_focus()
			return
	%CloseMenuButton.grab_focus()


func _refresh_tutorial() -> void:
	var tip := Tutorial.current()
	%TutorialPanel.visible = not tip.is_empty()
	if not tip.is_empty():
		%TutorialText.text = Tutorial.text_of(tip)


func _save_and_quit() -> void:
	Game.save_game()
	get_tree().paused = false
	get_tree().change_scene_to_file("res://ui/main_menu.tscn")


func _on_dialogue_opened(text: String) -> void:
	_dialogue.show()
	_dialogue_text.text = text
	_dialogue_text.visible_ratio = 0.0
	create_tween().tween_property(_dialogue_text, "visible_ratio", 1.0, text.length() * 0.025)


func _on_focus_changed(display_name: String) -> void:
	_focus_name = display_name
	%FocusLabel.text = "" if display_name == "" else "[%s]  %s" % [Game.key_name("interact"), display_name]


func _toast(text: String) -> void:
	var panel := PanelContainer.new()
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", 14)
	panel.add_child(label)
	panel.modulate.a = 0.0
	%Toasts.add_child(panel)
	var tween := panel.create_tween()
	tween.tween_property(panel, "modulate:a", 1.0, 0.25)
	tween.tween_interval(TOAST_TIME)
	tween.tween_property(panel, "modulate:a", 0.0, 0.4)
	tween.tween_callback(panel.queue_free)
