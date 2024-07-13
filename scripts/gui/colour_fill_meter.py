import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

from scripts.utils.CORE_FUNCS import vec, apply_rainbow
from scripts.config.SETTINGS import WIDTH, Z_LAYERS

    ##############################################################################################

class Colour_Meter(pygame.sprite.Sprite):
    def __init__(self, game, groups):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.z = Z_LAYERS["gui"]

        self.background = pygame.image.load("assets/gui/colour_meter_background.png").convert_alpha()
        self.background = pygame.transform.scale(self.background, vec(self.background.get_size()) * 2.75)
        self.background.set_colorkey((0, 0, 0))
        self.fill = pygame.image.load("assets/gui/colour_meter_fill.png").convert_alpha()
        self.fill = pygame.transform.scale(self.fill, vec(self.fill.get_size()) * 2.75)
        self.fill.set_colorkey((0, 0, 0))
        
        self.rect = self.background.get_rect(center=(WIDTH/2, 10 + self.background.get_height() / 2))

        self.percent = 50
        self.animation_period = 700
        self.elapsed_time = 0

    def update(self):
        self.elapsed_time += self.game.dt * 1000
        self.draw()

    def draw(self):
        self.screen.blit(self.background, self.rect)
        
        fill = apply_rainbow(
            self.fill,
            offset=(self.animation_period - self.elapsed_time) / self.animation_period,
            bands=1.2
        )
        fill = fill.subsurface([0, 0, fill.get_width() * (self.percent / 100), fill.get_height()])
        self.screen.blit(fill, self.rect)