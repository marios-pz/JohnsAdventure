extends Node
## Global game state (autoload "Game").
##
## Everything that must survive a level change lives here: John's stats,
## inventory, story flags and the save file. Level and player scenes are
## disposable and read/write this state instead of owning it.
##
## It is also the event bus between gameplay and UI: gameplay code emits
## (open_dialogue, travel, ...) and the HUD / Main scene listen.

signal stats_changed
signal inventory_changed
signal leveled_up(new_level: int)
signal died
## Main listens and swaps levels. `position` null = use the level's spawn for `from_level`.
signal travel_requested(level_id: String, from_level: String, position: Variant)
signal dialogue_opened(text: String)
signal dialogue_closed
## Name of the interactable John is currently facing ("" = nothing).
signal focus_changed(display_name: String)
## Keyboard/mouse <-> controller switch, so on-screen prompts can show the right glyphs.
signal input_device_changed(gamepad: bool)

const SAVE_PATH := "user://save.json"
## Button names shown in prompts while a controller is in use (Xbox layout).
const PAD_NAMES := {
	JOY_BUTTON_A: "A", JOY_BUTTON_B: "B", JOY_BUTTON_X: "X", JOY_BUTTON_Y: "Y",
	JOY_BUTTON_BACK: "View", JOY_BUTTON_START: "Menu", JOY_BUTTON_LEFT_SHOULDER: "LB",
	JOY_BUTTON_RIGHT_SHOULDER: "RB",
}
const WEAPONS := {
	"training_sword": preload("res://items/training_sword.tres"),
	"knight_sword": preload("res://items/knight_sword.tres"),
}
const POTION_HEAL := 40
const MAX_ITEMS := 32

# --- Progression (saved) ------------------------------------------------------
var level := 1
var experience := 0
var upgrade_points := 0
var damage := 10
var endurance := 0          ## flat reduction of every hit John takes
var crit_chance := 0.05     ## added to the equipped weapon's crit chance
var max_health := 60
var health := 60
var potions := 3
var coins := 0
var weapons: Array[String] = []
var equipped := ""
var cutscenes_played: Array[String] = []
var opened_chests: Array[String] = []
var current_level := "johns_room"
var saved_position: Variant = null  ## Vector2 or null (null = level start)

# --- Runtime only ------------------------------------------------------------
var dialogue_source: Node = null
var seen_items := 0             ## for the HUD "new item" notification dot
var gamepad := false            ## last input came from a controller
var _checkpoint := {}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _input(event: InputEvent) -> void:
	var pad := event is InputEventJoypadButton \
			or (event is InputEventJoypadMotion and absf(event.axis_value) > 0.4)
	var keys := event is InputEventKey or event is InputEventMouseButton
	if (pad and not gamepad) or (keys and gamepad):
		gamepad = pad
		input_device_changed.emit(gamepad)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("fullscreen"):
		var fullscreen := DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if fullscreen
				else DisplayServer.WINDOW_MODE_FULLSCREEN)


# --- Stats ---------------------------------------------------------------------

## Experience needed to go from the current level to the next.
func xp_to_next() -> int:
	return 100 * level


func add_experience(amount: int) -> void:
	experience += amount
	while experience >= xp_to_next():
		experience -= xp_to_next()
		level += 1
		upgrade_points += 1
		health = max_health  # level-ups fully heal
		leveled_up.emit(level)
	stats_changed.emit()


## Returns the damage actually taken after endurance.
func take_damage(amount: int) -> int:
	if health <= 0:
		return 0
	var taken := maxi(1, amount - endurance)
	health = maxi(0, health - taken)
	stats_changed.emit()
	if health == 0:
		died.emit()
	return taken


func drink_potion() -> bool:
	if potions <= 0 or health >= max_health or health <= 0:
		return false
	potions -= 1
	health = mini(max_health, health + POTION_HEAL)
	stats_changed.emit()
	return true


## stat: "damage" | "endurance" | "crit_chance"
func upgrade(stat: String) -> void:
	if upgrade_points <= 0:
		return
	upgrade_points -= 1
	match stat:
		"damage": damage += 2
		"endurance": endurance += 1
		"crit_chance": crit_chance += 0.02
	stats_changed.emit()


# --- Inventory -------------------------------------------------------------------

func weapon() -> Weapon:
	return WEAPONS.get(equipped)


func add_weapon(id: String) -> void:
	if weapons.size() >= MAX_ITEMS:
		return
	weapons.append(id)
	Tutorial.notify("weapon")
	if equipped == "":
		equipped = id
	inventory_changed.emit()


## Clicking the equipped weapon unequips it, like the original inventory.
func toggle_equip(id: String) -> void:
	equipped = "" if equipped == id else id
	inventory_changed.emit()


# --- Dialogue / world events -----------------------------------------------------

func open_dialogue(text: String, source: Node) -> void:
	dialogue_source = source
	dialogue_opened.emit(text)


func close_dialogue() -> void:
	if dialogue_source == null:
		return
	dialogue_source = null
	dialogue_closed.emit()


func travel(level_id: String) -> void:
	close_dialogue()
	travel_requested.emit(level_id, current_level, null)


# --- Save / load -------------------------------------------------------------------

func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)


func new_game() -> void:
	from_dict({})
	DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))


func load_game() -> void:
	var text := FileAccess.get_file_as_string(SAVE_PATH)
	var data: Variant = JSON.parse_string(text) if text != "" else null
	from_dict(data if data is Dictionary else {})


## Saves the current state. John's position is read from the live player, if any.
func save_game() -> void:
	var player := get_tree().get_first_node_in_group("player") as Node2D
	if player:
		saved_position = player.global_position
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file == null:
		push_error("Cannot write save file: %s" % error_string(FileAccess.get_open_error()))
		return
	file.store_string(JSON.stringify(to_dict(), "\t"))


func to_dict() -> Dictionary:
	var pos: Variant = saved_position
	return {
		"level": level, "experience": experience, "upgrade_points": upgrade_points,
		"damage": damage, "endurance": endurance, "crit_chance": crit_chance,
		"max_health": max_health, "health": health, "potions": potions, "coins": coins,
		"weapons": weapons, "equipped": equipped,
		"cutscenes_played": cutscenes_played, "opened_chests": opened_chests,
		"current_level": current_level,
		"position": [pos.x, pos.y] if pos is Vector2 else null,
		"quests": Quests.to_dict(),
		"tutorial": Tutorial.to_dict(),
	}


func from_dict(d: Dictionary) -> void:
	level = int(d.get("level", 1))
	experience = int(d.get("experience", 0))
	upgrade_points = int(d.get("upgrade_points", 0))
	damage = int(d.get("damage", 10))
	endurance = int(d.get("endurance", 0))
	crit_chance = d.get("crit_chance", 0.05)
	max_health = int(d.get("max_health", 60))
	health = int(d.get("health", max_health))
	potions = int(d.get("potions", 3))
	coins = int(d.get("coins", 0))
	weapons.assign(d.get("weapons", []))
	equipped = d.get("equipped", "")
	cutscenes_played.assign(d.get("cutscenes_played", []))
	opened_chests.assign(d.get("opened_chests", []))
	current_level = d.get("current_level", "johns_room")
	var pos: Variant = d.get("position")
	saved_position = Vector2(pos[0], pos[1]) if pos is Array else null
	Quests.from_dict(d.get("quests", {}))
	Tutorial.from_dict(d.get("tutorial", []))
	seen_items = weapons.size()
	stats_changed.emit()
	inventory_changed.emit()


## Called by Main each time a level finished loading.
func checkpoint(position: Vector2) -> void:
	saved_position = position
	_checkpoint = to_dict()


## Death: roll back to the state John had when he entered the level.
## Cutscenes already seen stay seen.
func respawn() -> void:
	var played := cutscenes_played.duplicate()
	from_dict(_checkpoint)
	cutscenes_played = played
	health = max_health
	travel_requested.emit(current_level, "", saved_position)


# --- Input prompts -------------------------------------------------------------------

## What to press for `action` on the current device, e.g. "Space" or "A".
func key_name(action: String) -> String:
	if action == "attack":
		return "X" if gamepad else "Left click"
	for event in InputMap.action_get_events(action):
		if gamepad and event is InputEventJoypadButton:
			return PAD_NAMES.get(event.button_index, "Button %d" % event.button_index)
		if not gamepad and event is InputEventKey:
			return OS.get_keycode_string(event.physical_keycode)
	return "?"
