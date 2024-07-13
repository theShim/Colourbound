import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import os
import math
import numpy as np

from scripts.particles.sparks import Spark

from scripts.utils.CORE_FUNCS import vec, gen_rand_colour
from scripts.config.SETTINGS import Z_LAYERS

    ##############################################################################################

class Paint_Spark(Spark):
    def __init__(self, game, groups, pos):
        col = gen_rand_colour(True)
        outline = [max(0, col[i]-80) for i in range(3)]
        super().__init__(game, groups, pos, 1, math.radians(random.uniform(0, 360)), random.uniform(1, 3), col, outline=outline)