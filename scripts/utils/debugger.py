import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import os

from scripts.utils.CORE_FUNCS import vec, gen_rand_colour
from scripts.config.SETTINGS import Z_LAYERS

    ##############################################################################################

class Debugger:
    def __init__(self):
        self.screen = pygame.display.get_surface()

        self.text = ""
        self.font = pygame.font.SysFont('Verdana', 10)

    def add_text(self, text):
        self.text += text + "\n"

    def update(self):
        self.render()
        self.text = ""
    
    def render(self):
        label = self.font.render(self.text, False, (255, 255, 255))
        self.screen.blit(label, (0, 0))