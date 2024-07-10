import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

from scripts.world_loading.state_machine import State

    ##############################################################################################

class Planet_1(State):
    def __init__(self, game, prev=None):
        super().__init__(game, "planet_1", prev)
        self.tilemap.load("data/stage_data/test2.json")