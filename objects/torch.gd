extends Node2D
## Wall torch: its light flickers by jittering size and energy.

@export var radius := 220.0

var _next_flicker := 0.0

@onready var _light: PointLight2D = $Light


func _process(delta: float) -> void:
	_next_flicker -= delta
	if _next_flicker > 0.0:
		return
	_next_flicker = randf_range(0.06, 0.14)
	_light.texture_scale = randfn(radius, radius * 0.03) / 128.0  # radial.png has a 128 px radius
	_light.energy = randfn(1.0, 0.07)
