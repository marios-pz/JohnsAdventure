class_name Enemy
extends CharacterBody2D
## Generic melee enemy.
##
## Every enemy scene (goblin.tscn, guardian.tscn, ...) is this script with
## different exported stats and SpriteFrames. Animations used: "idle", "walk",
## "attack", optional "hit"; each may have "_left"/"_right" variants, otherwise
## the right-facing one is mirrored.
##
## AI: stand still -> chase John inside `sight_range` -> inside `attack_range`
## flash red for `windup` seconds (the telegraph), strike, then `recover`.
## The strike hitbox is aimed at John when the windup starts (any direction,
## so standing above/below an enemy is not a safe spot) and stays there: dodgeable.
## Knockable enemies are staggered out of their windup when hit.

signal died(enemy: Enemy)

const PARRY_STUN := 1.0             ## extra recover time after John parries a strike
const PARRY_PUSH := 420.0

enum State { IDLE, CHASE, WINDUP, RECOVER }

@export var kind := ""              ## quest target id, e.g. "Goblin"
@export var display_name := ""
@export var max_hp := 50
@export var xp := 20
@export var speed := 100.0
@export var damage := 5
@export var sight_range := 450.0
@export var attack_range := 80.0
@export var windup := 0.35
@export var recover := 0.8
@export var knockback := 300.0      ## how hard John is pushed when hit
@export var knockable := true
@export var is_static := false      ## training dummies never move or attack
@export var aura := false           ## shadow creatures glow purple

var hp := 0
var dead := false

var _state := State.IDLE
var _timer := 0.0
var _facing_left := false
var _knock := Vector2.ZERO
var _bleed_weapon: Weapon
var _bleed_left := 0.0
var _bleed_tick := 0.0

@onready var sprite: AnimatedSprite2D = $Sprite
@onready var _attack_area: Area2D = $AttackArea
@onready var _attack_shape: CollisionShape2D = $AttackArea/Shape
@onready var _reach: Vector2 = _attack_shape.position  ## authored for a strike to the right
@onready var _health_bar: Node2D = get_node_or_null("HealthBar")
@onready var _bar_width: float = $HealthBar/Fill.size.x if _health_bar else 0.0


func _ready() -> void:
	hp = max_hp
	add_to_group("enemies")
	if aura:
		sprite.modulate = Color(0.85, 0.7, 1.0)
	_play("idle")


func _physics_process(delta: float) -> void:
	if dead:
		return
	_tick_bleed(delta)
	_timer -= delta
	var move := Vector2.ZERO
	match _state:
		State.IDLE, State.CHASE:
			var player := get_tree().get_first_node_in_group("player") as Player
			_state = State.IDLE
			if player and not is_static and not Cutscene.playing and Game.health > 0:
				var to_player := player.global_position - global_position
				_facing_left = to_player.x < 0.0
				if to_player.length() <= attack_range:
					_start_windup(to_player)
				elif to_player.length() <= sight_range:
					# ponytail: straight-line chase, fine for open rooms; add NavigationAgent2D if levels become mazes
					move = to_player.normalized() * speed
					_state = State.CHASE
		State.WINDUP:
			if _timer <= 0.0:
				_strike()
		State.RECOVER:
			if _timer <= 0.0:
				_state = State.IDLE
	velocity = move + _knock
	_knock = _knock.move_toward(Vector2.ZERO, 1800.0 * delta)
	move_and_slide()
	_update_animation(move)


## Player sword hit. `push` is a velocity, `weapon` may add bleeding.
func take_hit(amount: int, crit: bool, push: Vector2, weapon: Weapon) -> void:
	if dead:
		return
	_damage(amount, Color.YELLOW if crit else Color.WHITE)
	Audio.play_sfx("hit", 0.4)
	if knockable:
		_knock = push
		if _state == State.WINDUP:  # stagger
			_state = State.RECOVER
			_timer = 0.3
			sprite.modulate = _base_color()
	if weapon and weapon.bleed_damage > 0:
		_bleed_weapon = weapon
		_bleed_left = weapon.bleed_duration
	if sprite.sprite_frames.has_animation("hit"):
		sprite.play("hit")
	var flash := create_tween()
	sprite.self_modulate = Color(3, 3, 3)
	flash.tween_property(sprite, "self_modulate", Color.WHITE, 0.12)


## Called when a quest step (or the boss) makes this enemy appear.
func on_revealed() -> void:
	Audio.play_sfx("magic", 0.4)
	_burst(Color(0.55, 0.2, 0.9), 50)
	var tween := create_tween()
	scale = Vector2(0.2, 0.2)
	tween.tween_property(self, "scale", Vector2.ONE, 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _start_windup(to_player: Vector2) -> void:
	_state = State.WINDUP
	_timer = windup
	# Swing the (unrotated) hitbox around the body toward John; its height offset stays put.
	_attack_shape.position = Vector2(_reach.x, 0.0).rotated(to_player.angle()) + Vector2(0.0, _reach.y)
	sprite.modulate = Color(1.8, 0.55, 0.55)  # the telegraph: dodge now!


func _strike() -> void:
	sprite.modulate = _base_color()
	_state = State.RECOVER  # before hurt(): a parry extends it
	_timer = recover
	for body in _attack_area.get_overlapping_bodies():
		if body is Player:
			body.hurt(damage, (body.global_position - global_position).normalized() * knockback, self)


## John parried this strike: stunned, and pushed back unless heavy.
func parried(direction: Vector2) -> void:
	_state = State.RECOVER
	_timer = recover + PARRY_STUN
	if knockable:
		_knock = direction * PARRY_PUSH
	var flash := create_tween()
	sprite.self_modulate = Color(0.6, 0.6, 0.6)
	flash.tween_property(sprite, "self_modulate", Color.WHITE, PARRY_STUN)


func _tick_bleed(delta: float) -> void:
	if _bleed_left <= 0.0:
		return
	_bleed_left -= delta
	_bleed_tick -= delta
	if _bleed_tick <= 0.0:
		_bleed_tick = _bleed_weapon.bleed_interval
		_damage(_bleed_weapon.bleed_damage, Color(0.75, 0.3, 1.0))


func _damage(amount: int, color: Color) -> void:
	hp -= amount
	FloatingText.spawn(get_parent(), global_position + Vector2(0, sprite.position.y), str(amount), color)
	if _health_bar:
		_health_bar.visible = true
		$HealthBar/Fill.size.x = _bar_width * clampf(float(hp) / max_hp, 0.0, 1.0)
	if hp <= 0:
		_die()


func _die() -> void:
	dead = true
	remove_from_group("enemies")
	Game.add_experience(xp)
	died.emit(self)
	Quests.refresh()
	$Shape.set_deferred("disabled", true)
	if _health_bar:
		_health_bar.hide()
	_burst(Color(0.2, 0.2, 0.25) if not aura else Color(0.45, 0.15, 0.75), 70)
	var tween := create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.5)
	tween.parallel().tween_property(sprite, "scale:y", sprite.scale.y * 0.2, 0.5)
	tween.tween_callback(queue_free)


## One-shot particle puff at the enemy's body (death, summon).
func _burst(color: Color, amount: int) -> void:
	var particles := CPUParticles2D.new()
	particles.one_shot = true
	particles.explosiveness = 0.9
	particles.amount = amount
	particles.lifetime = 0.7
	particles.emission_shape = CPUParticles2D.EMISSION_SHAPE_SPHERE
	particles.emission_sphere_radius = 30.0
	particles.direction = Vector2.UP
	particles.spread = 80.0
	particles.initial_velocity_min = 80.0
	particles.initial_velocity_max = 220.0
	particles.gravity = Vector2(0, 120)
	particles.scale_amount_min = 4.0
	particles.scale_amount_max = 9.0
	particles.color = color
	particles.position = global_position + Vector2(0, sprite.position.y * 0.5)
	particles.z_index = 40
	get_parent().add_child(particles)
	particles.emitting = true
	particles.finished.connect(particles.queue_free)


func _update_animation(move: Vector2) -> void:
	if sprite.animation == "hit" and sprite.is_playing():
		return
	if _state == State.WINDUP:
		_play("attack")
	elif move != Vector2.ZERO:
		_play("walk")
	else:
		_play("idle")


func _play(anim: String) -> void:
	var frames := sprite.sprite_frames
	var side := "_left" if _facing_left else "_right"
	if frames.has_animation(anim + side):
		_mirror(false)
		sprite.play(anim + side)
		return
	if frames.has_animation(anim + "_right"):
		anim += "_right"
	elif not frames.has_animation(anim):
		anim = "idle"
	_mirror(_facing_left)
	sprite.play(anim)


## Mirrors around the feet (negative scale) rather than flip_h: several sheets
## draw the body off-centre in wide cells (the guardian's spear), so flip_h would shift it.
func _mirror(left: bool) -> void:
	sprite.scale.x = absf(sprite.scale.x) * (-1.0 if left else 1.0)


func _base_color() -> Color:
	return Color(0.85, 0.7, 1.0) if aura else Color.WHITE
