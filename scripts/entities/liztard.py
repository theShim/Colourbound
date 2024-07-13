import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import math
import os

from scripts.particles.entity_death_spark import Death_Spark
from scripts.particles.paint_splatter import Paint_Splat

from scripts.utils.CORE_FUNCS import vec, lerp
from scripts.utils.sprite_animator import SpriteAnimator
from scripts.config.SETTINGS import Z_LAYERS, WIDTH

    ##############################################################################################

class Liztard(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls): #stores each animation's sprites in its own animator class
        cls.SPRITES = {}
        cls.GREY_SPRITES = {}
        cls.COLOURS = [
            (148, 30, 89),
            (145, 15, 76),
            (115, 20, 66),
            (89, 23, 56),
            (26, 21, 46),
            (33, 26, 61),
            (45, 36, 79)
        ]
        path = "assets/entities/liz(re)tard"
        for anim in os.listdir(path):
            imgs = []
            grey_imgs = []
            for move_name in os.listdir(f"{path}/{anim}"):
                img = pygame.image.load(f"{path}/{anim}/{move_name}").convert_alpha()
                img = pygame.transform.scale(img, pygame.math.Vector2(img.get_size())*2)
                img.set_colorkey((0, 0, 0))
                mask = pygame.mask.from_surface(img)
                pygame.draw.polygon(img, (0, 0, 1), mask.outline(), 2)
                imgs.append(img)
                grey_imgs.append(pygame.transform.grayscale(img))

            animator = SpriteAnimator(imgs, animation_speed=0.05)
            cls.SPRITES[anim.lower()] = animator
            grey_animator = SpriteAnimator(grey_imgs, animation_speed=0.05)
            cls.GREY_SPRITES[anim.lower()] = grey_animator

    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.z = Z_LAYERS["enemy"]
        self.entities = groups[-1]

        self.sprites = self.SPRITES.copy()
        self.grey_sprites = self.GREY_SPRITES.copy()
        self.status = "idle"
        self.direction = "left"
        self.rect = self.image.get_rect(topleft=pos)

        self.run_speed = 2
        self.true_colored = 0
        self.colored = 0
        self.explode = False
        
    #current image
    @property
    def image(self) -> pygame.Surface:
        spr = self.current_sprite.get_sprite()
        if self.direction == "right":
            return pygame.transform.flip(spr, True, False)
        return spr

    @property
    def grey_image(self) -> pygame.Surface:
        spr: pygame.Surface = self.grey_current_sprite.get_sprite().copy()
        if self.colored:
            pygame.draw.rect(spr, [0, 0, 0, 0], [0, 0, (spr.get_width() * self.colored/spr.get_width()), spr.get_height()])
        if self.direction == "right":
            return pygame.transform.flip(spr, True, False)
        return spr
    
    #current sprite animator
    @property
    def current_sprite(self) -> SpriteAnimator:
        return self.sprites.get(self.status, self.sprites["idle"])

    @property
    def grey_current_sprite(self) -> SpriteAnimator:
        return self.grey_sprites.get(self.status, self.sprites["idle"])
            
        ###################################################################################### 

    def move(self):
        player_pos = vec(self.game.player.rect.center)
        delta = (vec(self.rect.center) - player_pos)
        if delta.magnitude() < WIDTH/1.5:
            if delta.magnitude():
                delta = delta.normalize()

            vel = delta * self.run_speed
            self.rect.center -= vel

            if vel.x < 0:
                self.direction = "right"
            else:
                self.direction = "left"

    def collisions(self):
        for entity in self.entities:
            if entity != self:
                if isinstance(entity, Liztard):
                    if self.rect.colliderect(entity.rect):
                        dy = self.rect.centery - entity.rect.centery
                        dx = self.rect.centerx - entity.rect.centerx
                        angle = math.atan2(dy, dx)

                        vel = vec(math.cos(angle), math.sin(angle)) * 2
                        self.rect.center += vel
                        entity.rect.center -= vel

        for proj in self.game.projectiles:
            if proj.dh < 10:
                if self.rect.collidepoint(proj.pos):
                    proj.kill()

                    self.true_colored += random.randint(14, 25)
                    if self.true_colored >= 100:
                        self.true_colored = 100
                        self.explode = True

        if self.true_colored != self.colored:
            self.colored = lerp(self.true_colored, self.colored, 0.1)
            if abs(self.true_colored - self.colored) < 0.1:
                self.colored = self.true_colored

        map_: pygame.Surface = self.game.state_loader.current_state.tilemap.map
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.right > map_.get_width():
            self.rect.right = map_.get_width()
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.bottom > map_.get_height():
            self.rect.bottom = map_.get_height()
        
        ###################################################################################### 

    #changing the animation
    def change_status(self, status):
        if status != self.status:
            self.current_sprite.reset_frame()
            self.status = status

    #updating the current animation sprite
    def animate(self):
        self.current_sprite.next(self.game.dt)
        self.grey_current_sprite.next(self.game.dt)
            
        ###################################################################################### 

    def update(self):
        self.move()
        self.collisions()

        if self.explode:
            splat = Paint_Splat(self.game, [self.game.all_sprites, self.game.particles], self.rect.center, scale=1.5)

            img = splat.image.copy()
            img.set_colorkey((255, 255, 255))
            self.game.state_loader.tilemap.grey_map.blit(img, splat.rect, special_flags=pygame.BLEND_RGBA_SUB)

            for i in range(random.randint(10, 20)):
                Death_Spark(self.game, [self.game.all_sprites, self.game.particles], self.rect.center, 1.2, math.radians(random.randint(0, 360)), colour=random.choice(self.COLOURS), grav=True)
            self.kill()

            map_size = self.game.state_loader.tilemap.map.get_size()
            Liztard(self.game, [self.game.all_sprites, self.game.entities], (random.uniform(50, map_size[0]-50), random.uniform(50, map_size[1]-50)))

        self.animate()
        self.draw()

    def draw(self):
        self.screen.blit(self.image, self.image.get_rect(midbottom=self.rect.midbottom - self.game.offset))
        self.screen.blit(self.grey_image, self.grey_image.get_rect(midbottom=self.rect.midbottom - self.game.offset))