import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import os

from scripts.utils.CORE_FUNCS import vec, gen_rand_colour
from scripts.config.SETTINGS import Z_LAYERS

    ##############################################################################################

class Paint_Splatter(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, vel=None, size=1):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.z = Z_LAYERS["foreground particle"]

        self.pos = pos
        self.vel = vel or vec(random.uniform(-1, 1), random.uniform(-1, 1)) * random.uniform(0, 1.8)
        self.colour = gen_rand_colour(vibrant=True)
        self.radius = size * random.uniform(2, 4)
        self.decay = random.uniform(0.1, 0.3)

        self.alpha_qt = random.randint(2, 4)
        self.alpha_glow = random.uniform(1.5, 3)
        self.max_size = size * 2 * self.radius * self.alpha_glow * self.alpha_qt ** 2

    def update(self):
        self.radius -= self.decay
        if self.radius <= 0:
            return self.kill()
        
        self.pos += self.vel
        
        self.draw()

    def draw(self):
        surf = pygame.Surface((self.max_size, self.max_size), pygame.SRCALPHA)
        for i in range(self.alpha_qt, -1, -1):
            alpha = 255 - i * (255 // self.alpha_qt - 5)
            if alpha < 0: alpha = 0

            radius = 0.1 * self.radius * self.alpha_glow * i**2
            pygame.draw.circle(surf, (self.colour.r, self.colour.g, self.colour.b, alpha), list(map(lambda x: x/2, surf.get_size())), radius)

        self.screen.blit(surf, surf.get_rect(center=self.pos - self.game.offset))

    ##############################################################################################

class Paint_Splat(pygame.sprite.Sprite):

    SPLAT_COOLDOWN = 5
    
    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = []
        path = "assets/splatters"
        for splat in os.listdir(path):
            spr = pygame.image.load(f"{path}/{splat}").convert_alpha()
            spr = pygame.transform.scale(spr, vec(spr.get_size())*0.25)

            for i in range(4):
                s = pygame.transform.scale(spr, vec(spr.get_size())*(1 + (i/10)))
                s = pygame.transform.scale(s, [s.get_width(), s.get_height()*0.6])
                # s.set_colorkey((0, 0, 0))

                cls.SPRITES.append(s)
                cls.SPRITES.append(pygame.transform.flip(s, True, False))
                cls.SPRITES.append(pygame.transform.flip(s, False, True))
                cls.SPRITES.append(pygame.transform.flip(s, True, True))

    def __init__(self, game, groups, pos, scale=1):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.z = Z_LAYERS["background particle"]

        self.image: pygame.Surface = random.choice(self.SPRITES).copy()
        if scale >= 1:
            self.image = pygame.transform.scale(self.image, vec(self.image.get_size()) * scale)
        self.image.set_colorkey((0, 0, 0))

        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        self.game.state_loader.tilemap.changed = True

        self.kill()
            
        splat = f"paint_splat_{random.randint(1,3)}"
        if not self.game.music_player.is_playing("sfx"):
            self.game.music_player.play(splat, "sfx")
            self.game.music_player.set_vol(random.uniform(0.1, 0.5), "sfx")
        elif not self.game.music_player.is_playing("splat"):
            self.game.music_player.play(splat, "splat")
            self.game.music_player.set_vol(random.uniform(0.1, 0.5), "splat")