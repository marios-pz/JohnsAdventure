extends Node
## Music and sound effects by name (autoload "Audio").

const MUSIC := {
	"main_theme": "res://assets/sounds/main.ogg",
	"forest_theme": "res://assets/sounds/forest_theme.ogg",
	"city_theme": "res://assets/sounds/city_theme.ogg",
	"garden_theme": "res://assets/sounds/cave_garden.ogg",
	"credits": "res://assets/sounds/credits.ogg",
}
const SFX := {
	"sword": "res://assets/sounds/sword_slice.ogg",
	"wooden_sword": "res://assets/sounds/wooden_sword.ogg",
	"hit": "res://assets/sounds/dummy_hit.ogg",
	"magic": "res://assets/sounds/magic_shooting.ogg",
	"letter": "res://assets/sounds/letter_sound.ogg",
	"select": "res://assets/sounds/Select_UI.ogg",
}

const MUSIC_VOLUME := 0.6

var current_music := ""
var _music := AudioStreamPlayer.new()
var _fade: Tween


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_music.volume_db = linear_to_db(MUSIC_VOLUME)
	add_child(_music)


## Starts `track` looping. Re-requesting the playing track does nothing.
func play_music(track: String) -> void:
	if track == current_music:
		return
	current_music = track
	if _fade:
		_fade.kill()
	_music.volume_db = linear_to_db(MUSIC_VOLUME)
	var stream: AudioStreamOggVorbis = load(MUSIC[track])
	stream.loop = true
	_music.stream = stream
	_music.play()


func stop_music() -> void:
	current_music = ""
	_music.stop()


## Fades the track out and forgets it, so the next play_music() starts fresh even
## when it asks for the same track (title screen and John's room share main_theme).
## Await it before changing scene between the menu and the game.
func fade_out_music(time := 0.6) -> void:
	current_music = ""
	if _fade:
		_fade.kill()
	_fade = create_tween()
	_fade.tween_property(_music, "volume_db", -60.0, time)
	_fade.tween_callback(_music.stop)
	await _fade.finished


func play_sfx(sound: String, volume := 0.5) -> void:
	var player := AudioStreamPlayer.new()
	player.stream = load(SFX[sound])
	player.volume_db = linear_to_db(volume)
	player.pitch_scale = randf_range(0.93, 1.07)  # small variation so repeats don't sound robotic
	add_child(player)
	player.play()
	player.finished.connect(player.queue_free)
