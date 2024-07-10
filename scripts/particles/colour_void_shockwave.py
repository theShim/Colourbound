import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import math
import random

from scripts.utils.CORE_FUNCS import vec, lerp, Timer
from scripts.utils.sprite_animator import SpriteAnimator
from scripts.config.SETTINGS import WIDTH, HEIGHT, Z_LAYERS, FPS

    ##############################################################################################

class Shockwave_Particle(pygame.sprite.Sprite):
    
    @classmethod
    def cache_sprites(cls):
        cls.COLOUR_PALETTE = pygame.image.load("assets/palettes/dark_colour_palette.png").convert_alpha()
        
    def __init__(self, game, groups, angle):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.rotation = random.uniform(0, 180)
        self.rot_mod = random.uniform(0.1, 5)
        self.angle = angle
        self.scale = random.uniform(8, 15)
        self.pos = vec(WIDTH*1.5, HEIGHT/2)

        self.colour = self.COLOUR_PALETTE.get_at((random.randint(0, self.COLOUR_PALETTE.get_width()-1), random.randint(0, self.COLOUR_PALETTE.get_height()-1)))

    def update(self, radius):
        self.rotation += self.rot_mod
        self.pos = vec(WIDTH*1.5, HEIGHT/2) + vec(math.cos(self.angle), math.sin(self.angle)) * radius

        if self.pos.x < WIDTH and not pygame.Rect(0, 0, WIDTH, HEIGHT).collidepoint(self.pos):
            return self.kill()

        self.draw()

    def draw(self):
        points = [
            self.pos + vec(math.cos(math.radians(self.rotation + offset)), math.sin(math.radians(self.rotation + offset))) * self.scale
            for offset in range(0, 360, 90)
        ]
        pygame.draw.polygon(self.screen, self.colour, points)