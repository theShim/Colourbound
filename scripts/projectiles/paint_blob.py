import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import math

from scripts.particles.paint_splatter import Paint_Splatter, Paint_Splat

from scripts.utils.CORE_FUNCS import vec, Timer, gen_rand_colour
from scripts.config.SETTINGS import GRAV, HEIGHT, Z_LAYERS

    ##############################################################################################

class Paint_Blob(pygame.sprite.Sprite):
    def __init__(self, game, groups, start_pos, end_pos, facing):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.z = Z_LAYERS["projectile"]

        self.pos = vec(start_pos)
        self.start_pos = self.pos.copy()
        self.end_pos = vec(end_pos)
        self.facing = facing

        self.max_height = 40
        self.vel = math.sqrt(self.max_height * 2 * GRAV)
        self.total_time = (2 * self.vel) / GRAV
        self.time = 0.1
        self.dh = 0
        self.landed = False
        
        self.colour = gen_rand_colour(vibrant=True)
        self.colour_switch = Timer(5, 1)

    def move(self):
        self.time += self.game.dt * 10
        self.dh = (self.vel * self.time) - (0.5 * GRAV * (self.time ** 2))
        
        if self.dh <= 0:
            self.dh = 0
            self.landed = True
        if self.time > self.total_time:
            self.time = self.total_time

        self.pos = self.start_pos.lerp(self.end_pos, self.time / self.total_time)

    def update(self):
        self.colour_switch.update()
        if self.colour_switch.finished:
            self.colour_switch.reset()
            self.colour = gen_rand_colour(vibrant=True)

        if self.dh:
            for i in range(2):
                Paint_Splatter(self.game, [self.game.all_sprites, self.game.particles], self.pos - vec(0, self.dh))
                
        if self.landed:
            splat = Paint_Splat(self.game, [self.game.all_sprites, self.game.particles], self.pos)

            img = splat.image.copy()
            img.set_colorkey((255, 255, 255))
            self.game.state_loader.tilemap.grey_map.blit(img, splat.rect, special_flags=pygame.BLEND_RGBA_SUB)

            splat.kill()
            self.kill()
            return

        self.game.state_loader.tilemap.changed = False

        self.move()
        self.draw()

    def draw(self):
        # pygame.draw.line(self.screen, (100, 100, 100), self.pos - self.game.offset, self.end_pos - self.game.offset, 2)
        screen_y = self.pos.y - self.game.offset.y
        radius = (((5 * screen_y) / HEIGHT) + 4)

        y = radius / 2
        shadow = pygame.Surface((y*4, y), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0), [0, 0, y*4, y])
        shadow.set_alpha(128)
        self.screen.blit(shadow, shadow.get_rect(center=(self.pos + vec(0, radius) - self.game.offset)))

        pygame.draw.circle(self.screen, self.colour, self.pos - self.game.offset - vec(0, self.dh), radius)