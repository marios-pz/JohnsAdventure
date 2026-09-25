class_name FloatingText
extends Label
## Damage numbers and reward text that rise and fade out in world space.


static func spawn(parent: Node, at: Vector2, text: String, color: Color, duration := 0.8) -> void:
	var label := FloatingText.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", 18)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", Color.BLACK)
	label.add_theme_constant_override("outline_size", 8)
	label.z_index = 50
	label.size = Vector2(320, 0)
	label.position = at - Vector2(160, 20) + Vector2(randf_range(-12, 12), 0)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(label)
	var tween := label.create_tween()
	tween.tween_property(label, "position:y", label.position.y - 60.0, duration) \
			.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_property(label, "modulate:a", 0.0, duration * 0.5).set_delay(duration * 0.5)
	tween.tween_callback(label.queue_free)
