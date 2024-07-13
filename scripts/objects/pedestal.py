import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math

from scripts.particles.paint_shockwave import Paint_Shockave
from scripts.particles.paint_splatter import Paint_Splatter

from scripts.utils.CORE_FUNCS import vec, apply_rainbow, lerp
from scripts.utils.sprite_animator import SpriteAnimator
from scripts.config.SETTINGS import Z_LAYERS

    ##############################################################################################

class Pedestal(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        path = "assets/objects/pedestal"
        imgs = []
        masks = []
        for i in range(47):
            img = pygame.image.load(f"{path}/{i}.png").convert_alpha()
            img.set_colorkey((255, 255, 255))
            imgs.append(img)

            img = img.copy()
            img.set_colorkey((255, 0, 0))
            masks.append(pygame.mask.from_surface(img).to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(180, 180, 180, 255)).convert_alpha())

        cls.ANIMATOR = SpriteAnimator(imgs, animation_speed=0.2)
        cls.MASKS = masks

    def __init__(self, game, groups, pos, radius):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.z = Z_LAYERS["pedestal"]

        self.pos = vec(pos)
        self.animator = self.ANIMATOR.copy()
        self.animator.frame_index = random.uniform(0, len(self.animator.sprites))

        self.splat_radius = radius
        self.true_fill = 0
        self.fill = 0
        self.fill_max = 5
        self.explosion_timer = 0

        self.animation_period = 700
        self.elapsed_time = random.randint(0, 700)

        self.hover = vec()
        self.max_hover = 4
        self.highest = 0
        

    @property
    def image(self) -> pygame.Surface:
        spr = self.animator.get_sprite().copy()
        spr.set_colorkey((255, 0, 0))
        return spr
    
    def paint_blob_collisions(self):
        for blob in self.game.projectiles:
            if self.image.get_rect(midbottom = self.pos).collidepoint(blob.pos):
                if self.true_fill < self.fill_max:
                    self.true_fill += 1
                blob.kill()

    def release_recollection(self):
        for i in range(random.randint(10, 16)):
            vel = vec(random.uniform(-1, 1), random.uniform(-1, 1)) * 5
            Paint_Splatter(self.game, [self.game.all_sprites, self.game.particles], self.pos.copy(), vel, size=2)
        Paint_Shockave(self.game, [self.game.all_sprites, self.game.particles], self.pos, self.splat_radius)
        self.kill()

    def animate(self):
        self.animator.next(self.game.dt)

    def update(self):
        self.paint_blob_collisions()

        if self.true_fill != self.fill:
            self.fill = lerp(self.true_fill, self.fill, 0.1)
            if abs(self.fill - self.true_fill) < 0.1:
                self.fill = self.true_fill

        if self.fill == self.fill_max:
            self.animator.animation_speed = lerp(10, self.animator.animation_speed, 0.1)
            self.explosion_timer += 1
            self.hover = vec(0, -0.3 * (-(self.explosion_timer ** 2) + (40 * self.explosion_timer)))
        else:
            self.hover = vec(0, self.max_hover * math.sin(0.1 * math.radians(self.elapsed_time)))

        if max(0, ((self.max_hover  * 1.5 + self.hover.y)) * 1.9) > 19:
            self.release_recollection()

        self.elapsed_time += self.game.dt * 1000

        self.animate()
        self.draw()

    def draw(self):
        #creating a shadow using the current height of jump
        y = min(19, max(0, ((self.max_hover  * 1.5 + self.hover.y)) * 1.9)) ** 0.9
        shadow = pygame.Surface((y*4, y*1.5), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0), [0, 0, y*4, y*1.5])
        shadow.set_alpha(128)
        self.screen.blit(shadow, shadow.get_rect(midbottom=(self.pos - self.game.offset + vec(0, 4))))

        self.screen.blit(self.image, self.image.get_rect(midbottom = self.pos - self.game.offset + self.hover))

        mask = self.MASKS[int(self.animator.frame_index)]
        overlay = mask.copy()
        overlay = apply_rainbow(
            overlay,
            offset=(self.animation_period - self.elapsed_time) / self.animation_period,
            bands=1.5
        )
        overlay = overlay.subsurface([0, overlay.get_height() * (1 - self.fill/self.fill_max), overlay.get_width(), overlay.get_height() * (self.fill / self.fill_max)])
        self.screen.blit(overlay, overlay.get_rect(midbottom = self.pos - self.game.offset + self.hover))