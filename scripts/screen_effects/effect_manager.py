import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math

from scripts.utils.CORE_FUNCS import vec, lerp, Timer
from scripts.config.SETTINGS import WIDTH, HEIGHT, Z_LAYERS, FPS

from scripts.screen_effects.screen_shake import Screen_Shake

    ##############################################################################################

class Effect_Manager:
    def __init__(self, game):
        self.game = game

        self.effects = {
            "screen shake" : Screen_Shake(self),
        }

        # self.effects["crt overlay"].on = True

    def update(self):
        for key in self.effects:
            effect = self.effects[key]
            if effect.on:
                effect.update()
                return
