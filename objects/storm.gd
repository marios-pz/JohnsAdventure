extends Node
## Post-ambush weather: the light dims a little and a light rain falls.
## Gated like any quest node (metadata show_after/hide_after); when it appears
## live (the ambush boom) on_revealed() eases the darkness in and starts the rain.

@export var shade := Color(0.7, 0.66, 0.8)   ## CanvasModulate colour: slightly dark, slightly purple
@export var rain_amount := 140
@export var rain_speed := 1400.0

var _shade: CanvasModulate
var _rain: CPUParticles2D


func _ready() -> void:  # nodes made here, not at init: a storm that never enters the tree must not leak
	_shade = CanvasModulate.new()
	_rain = CPUParticles2D.new()
	_shade.color = shade
	add_child(_shade)
	var layer := CanvasLayer.new()  # screen space: the rain covers the view wherever the camera goes
	layer.layer = 1
	add_child(layer)

	var fade := Gradient.new()  # each drop is a thin streak, bright at the bottom
	fade.set_color(0, Color(0.85, 0.9, 1.0, 0.5))
	fade.set_color(1, Color(0.85, 0.9, 1.0, 0.0))
	var drop := GradientTexture2D.new()
	drop.gradient = fade
	drop.width = 2
	drop.height = 20
	drop.fill_from = Vector2(0, 1)
	drop.fill_to = Vector2.ZERO
	_rain.texture = drop
	_rain.amount = rain_amount
	_rain.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	_rain.direction = Vector2(-0.22, 1.0)
	_rain.spread = 2.0
	_rain.gravity = Vector2.ZERO
	_rain.initial_velocity_min = rain_speed
	_rain.initial_velocity_max = rain_speed * 1.15
	_rain.particle_flag_align_y = true
	layer.add_child(_rain)
	_fit_rain()
	_rain.preprocess = _rain.lifetime  # already raining when John walks in later
	get_viewport().size_changed.connect(_fit_rain)


## Called by the level when the story reveals it: darken gradually, rain starts now.
func on_revealed() -> void:
	_shade.color = Color.WHITE
	create_tween().tween_property(_shade, "color", shade, 1.5)
	_rain.preprocess = 0.0
	_rain.restart()


## Spawn line above the (possibly ultrawide or tall) screen, drops live until they leave it.
func _fit_rain() -> void:
	var view := get_viewport().get_visible_rect().size
	_rain.position = Vector2(view.x * 0.6, -30.0)
	_rain.emission_rect_extents = Vector2(view.x * 0.75, 10.0)
	_rain.lifetime = (view.y + 60.0) / rain_speed
