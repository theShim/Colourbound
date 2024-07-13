import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

from scripts.utils.CORE_FUNCS import lerp
from scripts.config.SETTINGS import Z_LAYERS

    ##############################################################################################

class Paint_Shockave(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, radius):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.z = Z_LAYERS["background particle"]

        self.pos = pos

        self.radius = 1
        self.max_radius = radius

    def update(self):
        self.radius = lerp(self.max_radius, self.radius, 0.1)
        if self.radius >= self.max_radius - 0.5:
            self.game.state_loader.tilemap.changed = True
            self.kill()

        pygame.draw.circle(self.game.state_loader.tilemap.grey_map, (0, 0, 0, 0), self.pos, self.radius)