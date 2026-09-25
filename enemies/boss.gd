class_name Boss
extends Enemy
## The Big Dummie. Shows a HUD health bar instead of a floating one.
## Phase 2 at half health: roars, summons shadow dummies and gets faster.

@export var minion: PackedScene
@export var minion_count := 3

var enraged := false


func _ready() -> void:
	super()
	add_to_group("boss")


## Checked on every damage source, so bleed ticks can trigger phase 2 too.
func _damage(amount: int, color: Color) -> void:
	super(amount, color)
	if not enraged and not dead and hp <= max_hp / 2:
		_enrage()


func _enrage() -> void:
	enraged = true
	speed *= 1.5
	recover *= 0.6
	windup *= 0.8
	var player := get_tree().get_first_node_in_group("player") as Player
	if player:
		player.shake(14.0)
	for i in minion_count:
		var shadow: Enemy = minion.instantiate()
		shadow.position = position + Vector2.from_angle(TAU * i / minion_count) * 260.0
		get_parent().add_child.call_deferred(shadow)
		shadow.on_revealed.call_deferred()
