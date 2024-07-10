import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import os

from scripts.utils.CORE_FUNCS import vec, gen_rand_colour
from scripts.config.SETTINGS import Z_LAYERS

    ##############################################################################################

class Trail(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.z = Z_LAYERS["background particle"]

        self.pos = vec(pos)
        self.radius = 5
        self.og_radius = self.radius
        self.alpha = 255

    def update(self):
        self.alpha -= 20
        self.radius -= 0.25
        if self.radius < 0 or self.alpha < 0:
            return self.kill()

        self.draw()

    def draw(self):
        surf = pygame.Surface((self.og_radius*2, self.og_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (100, 100, 100), (self.og_radius, self.og_radius), self.radius)
        surf.set_alpha((self.alpha))
        self.screen.blit(surf, surf.get_rect(center=(self.pos - self.game.offset)))