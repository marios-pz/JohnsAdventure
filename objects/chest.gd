class_name Chest
extends StaticBody2D
## Opens once per save file and hands out its rewards.

@export var coins := 0
@export var potions := 0
@export var weapon_id := ""   ## key of Game.WEAPONS

var display_name := "Chest"

@onready var sprite: AnimatedSprite2D = $Sprite
@onready var _popup: Node2D = $Popup


func _ready() -> void:
	$Popup/Key.text = Game.key_name("interact")
	if is_open():
		sprite.animation = "open"
		sprite.frame = sprite.sprite_frames.get_frame_count("open") - 1


func is_open() -> bool:
	return _save_key() in Game.opened_chests


func can_interact() -> bool:
	return not is_open()


func interact() -> void:
	if is_open():
		return
	Game.opened_chests.append(_save_key())
	sprite.play("open")
	set_highlight(false)
	var rewards: PackedStringArray = []
	if weapon_id != "":
		Game.add_weapon(weapon_id)
		rewards.append(Game.WEAPONS[weapon_id].display_name)
	if coins > 0:
		Game.coins += coins
		rewards.append("+%d coins" % coins)
	if potions > 0:
		Game.potions += potions
		rewards.append("+%d potions" % potions)
	Game.stats_changed.emit()
	Audio.play_sfx("select")
	FloatingText.spawn(get_parent(), global_position + Vector2(0, -130), "\n".join(rewards), Color.GOLD, 2.5)


func set_highlight(on: bool) -> void:
	_popup.visible = on
	sprite.self_modulate = Color(1.3, 1.3, 1.3) if on else Color.WHITE


func _save_key() -> String:
	return "%s/%s" % [Game.current_level, name]
