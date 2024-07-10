import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import colorsys
import math

from scripts.utils.CORE_FUNCS import vec, lerp, Timer
from scripts.utils.sprite_animator import SpriteAnimator
from scripts.config.SETTINGS import WIDTH, HEIGHT, Z_LAYERS, FRIC, GRAV, CONTROLS, DEBUG, FPS

    ##############################################################################################