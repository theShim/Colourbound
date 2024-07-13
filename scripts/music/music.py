import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

    ##############################################################################################

#normal pygame sound object just with a name attribute
class Sound(pygame.mixer.Sound):
    def __init__(self, filename):
        super().__init__(filename)
        self.name = filename.split("/")[-1]

#stores all the music
SOUNDS = {
    "title_screen" : Sound("music/title_screen.wav"),
    "into_space" : Sound("music/into_space.wav"),
    "warp_speed" : Sound("music/warp_speed.wav"),
    "rumble" : Sound("music/rumble.mp3"),
    "typing" : Sound("music/typing.wav"),
    "falling_in_space" : Sound("music/falling_out_of_sky.wav"),
    "paint_splat_1" : Sound("music/paint_splat_1.wav"),
    "paint_splat_2" : Sound("music/paint_splat_2.mp3"),
    "paint_splat_3" : Sound("music/paint_splat_3.mp3"),
}