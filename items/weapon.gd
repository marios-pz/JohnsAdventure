class_name Weapon
extends Resource
## A sword John can equip. One .tres per weapon in res://items/.

@export var id := ""
@export var display_name := ""
@export var damage := 5
@export_range(0.0, 1.0) var crit_chance := 0.1
## Speed (px/s) enemies are pushed back with on hit.
@export var knockback := 350.0
## Bleed: `bleed_damage` every `bleed_interval` seconds for `bleed_duration` seconds. 0 = none.
@export var bleed_damage := 0
@export var bleed_duration := 0.0
@export var bleed_interval := 0.1
@export var sound := "sword"
@export var icon: Texture2D
## Swing animations: attack1_/attack2_ + right/up/down (left = mirrored right).
@export var attack_frames: SpriteFrames
