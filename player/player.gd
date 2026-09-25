class_name Player
extends CharacterBody2D
## John.
##
## Moves in 8 directions and faces where he walks. Attacks swing toward the
## mouse cursor (or the right stick / facing direction on a controller) and
## chain into a 3-hit combo whose 3rd hit is a finisher. Dash cancels an attack,
## gives a short burst of invulnerability, passes through enemies and kicks the
## camera (zoom punch + lean) while leaving afterimages.
## Stats live in the Game autoload; this node only handles feel and physics.

const SPEED := 280.0
const DASH_SPEED := 750.0
const DASH_TIME := 0.18
const DASH_COOLDOWN := 0.7
const COMBO_WINDOW := 0.35       ## after a swing ends, a click within this time continues the combo
const FINISHER_MULT := 1.5       ## 3rd hit of the combo
const FINISHER_KNOCKBACK := 1.6
const CRIT_MULT := 1.5
const HURT_INVULNERABILITY := 0.6
const DASH_ZOOM := 0.93          ## camera zooms out this much at the start of a dash
const DASH_LEAN := 55.0          ## camera leads the dash direction by this many px
const AFTERIMAGE_EVERY := 0.035
const AIM_HEIGHT := 70.0         ## aim from John's chest, not his feet
const DIRECTIONS := {"right": Vector2.RIGHT, "left": Vector2.LEFT, "up": Vector2.UP, "down": Vector2.DOWN}
## Sword hitbox position per facing, relative to John's feet.
const ATTACK_OFFSETS := {"right": Vector2(75, -40), "left": Vector2(-75, -40), "up": Vector2(0, -105), "down": Vector2(0, 25)}

var facing := "down"
var dash_charge := 1.0           ## 0..1, shown by the HUD

var _dash_left := 0.0
var _dash_dir := Vector2.ZERO
var _combo := 0
var _combo_timer := 0.0
var _queued_attack := false
var _invulnerable := 0.0
var _knockback := Vector2.ZERO
var _shake := 0.0
var _lean := Vector2.ZERO
var _afterimage_timer := 0.0
var _focus: Node = null

@onready var camera: Camera2D = $Camera
@onready var _body: AnimatedSprite2D = $Body
@onready var _swing: AnimatedSprite2D = $Swing
@onready var _attack_area: Area2D = $AttackArea
@onready var _interactor: Area2D = $Interactor
@onready var _pointer: Node2D = $Pointer
@onready var _dust: CPUParticles2D = $Dust


func _ready() -> void:
	add_to_group("player")
	_swing.animation_finished.connect(_on_swing_finished)
	_swing.frame_changed.connect(_on_swing_frame)
	Game.inventory_changed.connect(_on_inventory_changed)
	_on_inventory_changed()


func can_act() -> bool:
	return not Cutscene.playing and Game.health > 0


func is_attacking() -> bool:
	return _swing.visible


func is_dashing() -> bool:
	return _dash_left > 0.0


## Camera shake, e.g. when hit or when the boss roars.
func shake(strength: float) -> void:
	_shake = maxf(_shake, strength)


func _physics_process(delta: float) -> void:
	var input := Input.get_vector("move_left", "move_right", "move_up", "move_down") if can_act() else Vector2.ZERO
	if input != Vector2.ZERO:
		Game.close_dialogue()  # walking away ends a conversation

	_invulnerable = maxf(0.0, _invulnerable - delta)
	_combo_timer = maxf(0.0, _combo_timer - delta)

	if is_dashing():
		_dash_left -= delta
		velocity = _dash_dir * DASH_SPEED
		_afterimage_timer -= delta
		if _afterimage_timer <= 0.0:
			_afterimage_timer = AFTERIMAGE_EVERY
			_spawn_afterimage()
		if not is_dashing():
			set_collision_mask_value(3, true)
	elif is_attacking():
		velocity = Vector2.ZERO
	else:
		velocity = input * SPEED
		dash_charge = minf(1.0, dash_charge + delta / DASH_COOLDOWN)
		if input != Vector2.ZERO:
			facing = _direction_name(input)

	velocity += _knockback
	_knockback = _knockback.move_toward(Vector2.ZERO, 2200.0 * delta)
	var before := global_position
	move_and_slide()
	if input != Vector2.ZERO:
		Tutorial.walked(global_position.distance_to(before))

	_animate(input)
	_update_focus()
	_pointer.visible = can_act() and Game.weapon() != null
	_pointer.rotation = _aim().angle() - PI / 2.0  # the pointer art points down

	_shake = move_toward(_shake, 0.0, 30.0 * delta)
	_lean = _lean.lerp(Vector2.ZERO, 6.0 * delta)
	camera.offset = _lean + Vector2(randf_range(-_shake, _shake), randf_range(-_shake, _shake))


func _unhandled_input(event: InputEvent) -> void:
	if not can_act():
		return
	if event.is_action_pressed("attack"):
		_attack()
	elif event.is_action_pressed("dash"):
		_dash()
	elif event.is_action_pressed("heal"):
		if Game.drink_potion():
			Tutorial.notify("heal")
	elif event.is_action_pressed("interact"):
		if is_instance_valid(_focus) and _focus.is_inside_tree():
			_focus.interact()
			Tutorial.notify("interact")
		else:
			Game.close_dialogue()


## Enemies call this. Ignored while dashing or right after another hit.
func hurt(amount: int, push: Vector2) -> void:
	if _invulnerable > 0.0 or is_dashing() or Game.health <= 0:
		return
	var taken := Game.take_damage(amount)
	_invulnerable = HURT_INVULNERABILITY
	_knockback = push
	shake(8.0)
	FloatingText.spawn(get_parent(), global_position + Vector2(0, -170), str(taken), Color(1, 0.3, 0.3))
	var tween := create_tween()
	modulate = Color(1, 0.35, 0.35)
	tween.tween_property(self, "modulate", Color.WHITE, HURT_INVULNERABILITY)


# --- Combat -----------------------------------------------------------------------

## Direction of the next swing: right stick (or facing) on a controller, else the mouse.
func _aim() -> Vector2:
	if Game.gamepad:
		var stick := Input.get_vector("aim_left", "aim_right", "aim_up", "aim_down")
		return stick if stick != Vector2.ZERO else DIRECTIONS[facing]
	return get_global_mouse_position() - (global_position + Vector2(0, -AIM_HEIGHT))


func _attack() -> void:
	if Game.weapon() == null or is_dashing():
		return
	if is_attacking():
		_queued_attack = true  # buffer the click so combos don't need frame-perfect timing
		return
	_combo = 1 if _combo_timer <= 0.0 or _combo >= 3 else _combo + 1
	facing = _direction_name(_aim())
	var side := "right" if facing == "left" else facing
	_swing.flip_h = facing == "left"
	_swing.play("attack%d_%s" % [2 if _combo == 2 else 1, side])
	_swing.visible = true
	_body.visible = false
	_attack_area.position = ATTACK_OFFSETS[facing]
	Audio.play_sfx(Game.weapon().sound)
	Tutorial.notify("combo" if _combo == 3 else "attack")


## The sword connects on the second frame of the swing.
func _on_swing_frame() -> void:
	if _swing.visible and _swing.frame == 1:
		_hit_enemies()


func _hit_enemies() -> void:
	var weapon := Game.weapon()
	var base := float(Game.damage + weapon.damage) * (FINISHER_MULT if _combo == 3 else 1.0)
	var hit_any := false
	for body in _attack_area.get_overlapping_bodies():
		if body is Enemy and not body.dead:
			var crit := randf() < Game.crit_chance + weapon.crit_chance
			var push := (body.global_position - global_position).normalized() * weapon.knockback
			if _combo == 3:
				push *= FINISHER_KNOCKBACK
			body.take_hit(roundi(base * (CRIT_MULT if crit else 1.0)), crit, push, weapon)
			hit_any = true
	if hit_any:
		shake(4.0 if _combo < 3 else 7.0)
		_hit_stop()


## A few frames of slow motion on impact make hits feel heavy.
func _hit_stop() -> void:
	Engine.time_scale = 0.05
	await get_tree().create_timer(0.045, true, false, true).timeout
	Engine.time_scale = 1.0


func _on_swing_finished() -> void:
	_swing.visible = false
	_body.visible = true
	_combo_timer = COMBO_WINDOW
	if _queued_attack:
		_queued_attack = false
		_attack()


func _dash() -> void:
	if dash_charge < 1.0:
		return
	if is_attacking():  # dash cancels the swing (and the rest of the combo)
		_swing.stop()
		_swing.visible = false
		_body.visible = true
		_queued_attack = false
		_combo = 0
	var input := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	_dash_dir = input.normalized() if input != Vector2.ZERO else DIRECTIONS[facing]
	facing = _direction_name(_dash_dir)
	_dash_left = DASH_TIME
	dash_charge = 0.0
	_afterimage_timer = 0.0
	set_collision_mask_value(3, false)  # dash through enemies
	# Camera feel: quick zoom-out punch that eases back, and a lean into the dash.
	_lean = _dash_dir * DASH_LEAN
	shake(2.5)
	var punch := create_tween()
	punch.tween_property(camera, "zoom", Vector2.ONE * DASH_ZOOM, 0.06).set_ease(Tween.EASE_OUT)
	punch.tween_property(camera, "zoom", Vector2.ONE, 0.35).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	Tutorial.notify("dash")


## A fading blue copy of John's current frame, left behind while dashing.
func _spawn_afterimage() -> void:
	var ghost := Sprite2D.new()
	ghost.texture = _body.sprite_frames.get_frame_texture(_body.animation, _body.frame)
	ghost.flip_h = _body.flip_h
	ghost.scale = _body.scale
	ghost.offset = _body.offset
	ghost.global_position = global_position
	ghost.modulate = Color(0.55, 0.75, 1.0, 0.55)
	get_parent().add_child(ghost)
	var fade := ghost.create_tween()
	fade.tween_property(ghost, "modulate:a", 0.0, 0.25)
	fade.tween_callback(ghost.queue_free)


func _on_inventory_changed() -> void:
	var weapon := Game.weapon()
	_swing.sprite_frames = weapon.attack_frames if weapon else null


# --- Presentation -----------------------------------------------------------------

func _animate(input: Vector2) -> void:
	if is_attacking():
		return
	var state := "idle"
	if is_dashing():
		state = "dash"
	elif input != Vector2.ZERO:
		state = "walk"
	_body.flip_h = facing == "left"
	_body.play("%s_%s" % [state, "right" if facing == "left" else facing])
	_dust.emitting = state != "idle"


## Picks the closest interactable in reach and tells the HUD about it.
func _update_focus() -> void:
	var best: Node = null
	var best_distance := INF
	if can_act():
		for area in _interactor.get_overlapping_areas():
			var target: Node = area if area.has_method("interact") else area.get_parent()
			if not target.has_method("interact"):
				continue
			if target.has_method("can_interact") and not target.can_interact():
				continue
			var distance := global_position.distance_squared_to(area.global_position)
			if distance < best_distance:
				best = target
				best_distance = distance
	if best == _focus:
		return
	if is_instance_valid(_focus):
		if _focus.has_method("set_highlight"):
			_focus.set_highlight(false)
		if Game.dialogue_source == _focus:
			Game.close_dialogue()
	_focus = best
	if _focus and _focus.has_method("set_highlight"):
		_focus.set_highlight(true)
	Game.focus_changed.emit(_focus.display_name if _focus else "")


static func _direction_name(v: Vector2) -> String:
	if absf(v.x) >= absf(v.y):
		return "right" if v.x > 0.0 else "left"
	return "down" if v.y > 0.0 else "up"
