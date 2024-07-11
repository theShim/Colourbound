import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.config.SETTINGS import WIDTH, HEIGHT
from scripts.utils.sprite_animator import SpriteAnimator

    ##############################################################################################

class Starry_Background:

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.screen = self.game.screen

        self.bg = pygame.Surface((WIDTH, HEIGHT))
        for i in range(100):
            x = random.uniform(0, WIDTH)
            y = random.uniform(0, HEIGHT)
            r = random.uniform(1, 4)
            c = random.uniform(100, 255)
            pygame.draw.circle(self.bg, (c, c, c), (x, y), r)

        self.stars = pygame.sprite.Group()
        for i in range(5): Background_Star(self.game, self.stars, (random.uniform(10, WIDTH-10), random.uniform(10, (self.game.offset_boundary_buffer.y - 10))))
        for i in range(5): Background_Star(self.game, self.stars, (random.uniform(10, WIDTH-10), random.uniform(HEIGHT-(self.game.offset_boundary_buffer.y - 10), HEIGHT-10)))
        for i in range(5): Background_Star(self.game, self.stars, (random.uniform(10, (self.game.offset_boundary_buffer.y - 10)), random.uniform(10, HEIGHT-10)))
        for i in range(5): Background_Star(self.game, self.stars, (random.uniform(WIDTH-(self.game.offset_boundary_buffer.y - 10), WIDTH-10), random.uniform(10, HEIGHT-10)))

    def update(self):
        self.draw()

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.stars.update()


class Background_Star(pygame.sprite.Sprite):
    
    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = []
        for c in range(100, 255, 15):
            imgs = []
            for i in range(4):
                img = pygame.image.load(f"assets/backgrounds/stars/{i}.png").convert_alpha()
                # img.set_colorkey((0, 0, 0))
                mask = pygame.mask.from_surface(img)
                img = mask.to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(c, c, c, 255))
                imgs.append(img)
            cls.SPRITES.append(SpriteAnimator(imgs, True, 0.1))

    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = pos
        self.animator: SpriteAnimator = random.choice(self.SPRITES)
        self.animator.frame_index = random.randint(0, len(self.animator.sprites)-1)

        self.t = random.uniform(0, 3)
        self.angle_mod = random.uniform(0.1, 2)

    def animate(self):
        self.animator.next(self.game.dt / 10)

    def update(self):
        self.t += math.radians(self.angle_mod)

        self.animate()
        self.draw()

    def draw(self):
        spr = self.animator.get_sprite()
        self.screen.blit(spr, spr.get_rect(center=self.pos + pygame.math.Vector2(0, 4 * math.sin(self.t))))