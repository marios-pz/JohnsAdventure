import pygame as pg

from .utils import resource_path


class SoundManager:

    def __init__(self, sound_only: bool = False, music_only: bool = False, volume: float = 0.3) -> None:
        # in order to simplify the load and optimize things, we will load this class
        # several times but only part of it, for example, in the player class,
        # you will load sound_only = True because you don't need an access to the
        # musics and only in the sounds.

        if not pg.mixer.get_init():
            pg.mixer.pre_init()

        self.volume = volume

        self.sounds = {
            "letterSound": pg.mixer.Sound(resource_path("data/sound/letter_sound.wav")),
            "woodenSword": pg.mixer.Sound(resource_path("data/sound/sword_slice.flac")),
            "dummyHit": pg.mixer.Sound(resource_path("data/sound/dummy_hit.wav")),
            "magic_shooting": pg.mixer.Sound(resource_path("data/sound/magic_shooting.wav")),
            "PlayerHit":  pg.mixer.Sound(resource_path("data/sound/hurt.wav"))

        } if not music_only else {}

        self.musics = {
            "forest_theme": resource_path("data/sound/forest_theme.flac"),
            "Select_UI": resource_path("data/sound/Select_UI.wav"),
            "city_theme": resource_path("data/sound/city_theme.mp3"),
            "credits": resource_path("data/sound/credits.mp3"),
            "garden_theme": resource_path("data/sound/cave_garden.mp3"),
            "main_theme": resource_path("data/sound/main.flac"),

        } if not sound_only else {}
        self.playing_music = "none"

    def play_sound(self, key: str) -> bool:  # return False if the sound couldn't be player, True otherwise
        if key not in self.sounds:
            print("Error when playing sound : unable to find ", key, "in database.")
            return False
        self.sounds[key].set_volume(self.volume)
        self.sounds[key].play()
        return True

    def play_music(self, key: str, loops: int = -1) -> bool:
        # return False if the music couldn't be played, True otherwise
        # start playing a song, if a song is already playing, it stops the current song and load the
        # song asked

        pg.mixer.music.set_volume(self.volume)

        if key not in self.musics:
            return False

        if pg.mixer.music.get_busy():
            pg.mixer.music.stop()
            pg.mixer.music.unload()

        pg.mixer.music.load(self.musics[key])
        self.playing_music = key
        pg.mixer.music.play(loops=loops)
        return True
