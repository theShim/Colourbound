import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import colorsys
import math

from scripts.utils.CORE_FUNCS import vec, apply_rainbow
from scripts.config.SETTINGS import WIDTH, Z_LAYERS

    ##############################################################################################

class Player_Icon(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.z = Z_LAYERS["gui"]

        self.image = pygame.image.load("assets/gui/player_icon.png").convert_alpha()
        self.image.set_colorkey((0, 0, 0))
        self.image = pygame.transform.scale(self.image, vec(self.image.get_size()) * 2.5)
        self.rect = self.image.get_rect(topleft=pos)

        self.shadow = pygame.mask.from_surface(self.image).to_surface(setcolor=(30, 30, 30, 255), unsetcolor=(0, 0, 0, 0))

    def update(self):
        self.screen.blit(self.shadow, self.rect.topleft + vec(2, 2))
        self.screen.blit(self.image, self.rect)