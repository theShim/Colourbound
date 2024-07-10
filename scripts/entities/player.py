import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math

from scripts.projectiles.paint_blob import Paint_Blob
from scripts.particles.player_floor_trail import Trail

from scripts.utils.CORE_FUNCS import vec, lerp, Timer
from scripts.utils.sprite_animator import SpriteAnimator
from scripts.config.SETTINGS import WIDTH, HEIGHT, Z_LAYERS, FRIC, GRAV, CONTROLS, DEBUG, FPS

    ##############################################################################################

class Player(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}
        path = "assets/entities/player"
        for anim in os.listdir(path):
            imgs = []
            for move_name in os.listdir(f"{path}/{anim}"):
                img = pygame.image.load(f"{path}/{anim}/{move_name}").convert_alpha()
                img = pygame.transform.scale(img, pygame.math.Vector2(img.get_size())*2)
                img.set_colorkey((0, 0, 0))
                mask = pygame.mask.from_surface(img)
                pygame.draw.polygon(img, (0, 0, 1), mask.outline(), 2)
                imgs.append(img)
            animator = SpriteAnimator(imgs, animation_speed=0.2)
            cls.SPRITES[anim.lower()] = animator

    def __init__(self, game, groups: list[pygame.sprite.Group]):
        super().__init__(groups)

        self.game = game
        if self.game != None:
            self.screen = self.game.screen
        else:
            self.screen = pygame.display.get_surface()

        self.sprites = Player.SPRITES
        self.status = "idle_down"
        self.z = Z_LAYERS["player"]
        
        self.rect = self.image.get_rect(topleft=(100, 100))
        self.facing = "down"

        self.vel = vec()
        self.acc = vec(0, 0)
        self.run_speed = 60

        self.jump_vel = 50
        self.jump_height = 0
        self.max_jump_height = (self.jump_vel ** 2) / (2 * GRAV)
        self.jump_time = 0
        self.jumping = False

        self.shot_held = False
        self.pointer_first = True
        
    @property
    def image(self) -> pygame.Surface:
        spr = self.current_sprite.get_sprite()
        return spr

    @property
    def current_sprite(self) -> SpriteAnimator:
        return self.sprites.get(self.status, self.sprites["idle_down"])
            
        ###################################################################################### 

    def move(self, keys):
        self.acc = vec(0, 0)
        
        self.directional_movement(keys)
        self.jump(keys)
        self.apply_forces()


    def directional_movement(self, keys):
        if keys[CONTROLS["left"]]:
            self.acc.x = -1 * self.run_speed
        elif keys[CONTROLS["right"]]:
            self.acc.x = 1 * self.run_speed

        if keys[CONTROLS["up"]]:
            self.acc.y = -1 * self.run_speed
        elif keys[CONTROLS["down"]]:
            self.acc.y = 1 * self.run_speed

        self.acc.clamp_magnitude_ip(self.run_speed)
        self.change_direction()

    def jump(self, keys):
        if keys[CONTROLS["jump"]] and not self.jumping:
            self.jumping = True
            self.jump_time = 0

        if self.jumping:
            self.jump_time += self.game.dt * 10
            self.jump_height = (self.jump_vel * self.jump_time) - (0.5 * GRAV * (self.jump_time ** 2))
            if self.jump_height <= 0:
                self.jump_height = 0
                self.jumping = 0


    def apply_forces(self):
        self.vel.x += self.acc.x * self.game.dt
        self.vel.y += self.acc.y * self.game.dt

        self.vel *= FRIC
        if -0.5 < self.vel.x < 0.5: #bounds to prevent sliding bug
            self.vel.x = 0
        if -0.5 < self.vel.y < 0.5:
            self.vel.y = 0

        self.rect.topleft += self.vel

        if not self.jump_height and self.vel.magnitude():
            for i in range(3):
                Trail(
                    self.game, [self.game.all_sprites, self.game.particles], self.rect.midbottom - self.vel * (i/3)
                )
            
        #####################################################################################

    def shoot(self):
        mousePos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()

        if mouse[0]:
            if self.shot_held == False:
                self.shot_held = True
                Paint_Blob(
                    self.game,
                    [self.game.all_sprites, self.game.projectiles],
                    self.rect.center + vec(0, 15 - self.jump_height),
                    mousePos + self.game.offset,
                    self.facing
                )
        else:
            self.shot_held = False
            
        ###################################################################################### 

    def change_direction(self):
        mousePos = vec(pygame.mouse.get_pos())
        dx = mousePos[0] - (self.rect.centerx - self.game.offset.x)
        dy = mousePos[1] - (self.rect.centery - self.game.offset.y)
        angle = math.degrees(math.atan2(dy, dx))
        
        if -112.5 < angle <= -67.5:
            self.facing = "up"
        elif -67.5 < angle <= -22.5:
            self.facing = "up_right"
        elif -22.5 < angle <= 22.5:
            self.facing = "right"
        elif 22.5 < angle <= 67.5:
            self.facing = "down_right"
        elif 67.5 < angle <= 112.5:
            self.facing = "down"
        elif 112.5 < angle <= 157.5:
            self.facing = "down_left"
        elif (157.5 < angle <= 180) or (-180 < angle < -157.5):
            self.facing = "left"
        elif -157.5 < angle <= -112.5:
            self.facing = "up_left"

        if self.facing in ["up", "up_right", "up_left"]:
            self.pointer_first = True
        else:
            self.pointer_first = False

        if self.acc.magnitude_squared() == 0:
            self.change_status(f"idle_{self.facing}")
        else:
            self.change_status(f"move_{self.facing}")

        
    def change_status(self, status):
        if status != self.status:
            self.current_sprite.reset_frame()
            self.status = status

    def animate(self):
        self.current_sprite.next(self.game.dt)
            
        ###################################################################################### 

    def update(self):
        keys = pygame.key.get_pressed()
        self.move(keys)
        self.shoot()

        self.animate()
        self.draw()

    def draw(self):
        jump_scale = max(0.25, 1 -(self.jump_height / self.max_jump_height))
        y = 10 * jump_scale
        shadow = pygame.Surface((y*4, y), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0), [0, 0, y*4, y])
        shadow.set_alpha(128)


        mousePos = vec(pygame.mouse.get_pos())
        dx = mousePos[0] - (self.rect.centerx - self.game.offset.x)
        dy = mousePos[1] - (self.rect.centery - self.game.offset.y)
        angle = math.atan2(dy, dx)
        
        #the lil arrow indicator. annoyed there isnt a better way to do differentiate if its infront of behind
        if self.pointer_first:
            pos = -self.game.offset + vec(self.rect.midbottom) + vec(0, -20) + vec(math.cos(angle), math.sin(angle)) * (self.image.get_width() / 1.5)
            points = [
                pos + vec(math.cos(math.radians(a) + angle), math.sin(math.radians(a) + angle)) * (8 - 2) - vec(0, self.jump_height)
                for a in range(0, 360, 120)
            ]
            shadow_points = [
                pos + vec(math.cos(math.radians(a) + angle), math.sin(math.radians(a) + angle)) * (10 - 2) - vec(0, self.jump_height)
                for a in range(0, 360, 120)
            ]
            pygame.draw.polygon(self.screen, (0, 0, 0), shadow_points)
            pygame.draw.polygon(self.screen, (100, 100, 100), points)

        #the shadow and player itself
        self.screen.blit(shadow, shadow.get_rect(center=(self.rect.midbottom - self.game.offset)))
        self.screen.blit(self.image, self.image.get_rect(midbottom=self.rect.midbottom - self.game.offset - vec(0, self.jump_height)))
        
        if not self.pointer_first:
            pos = -self.game.offset + vec(self.rect.midbottom) + vec(0, -20) + vec(math.cos(angle), math.sin(angle)) * (self.image.get_width() / 1.5)
            points = [
                pos + vec(math.cos(math.radians(a) + angle), math.sin(math.radians(a) + angle)) * (8 - 2) - vec(0, self.jump_height)
                for a in range(0, 360, 120)
            ]
            shadow_points = [
                pos + vec(math.cos(math.radians(a) + angle), math.sin(math.radians(a) + angle)) * (10 - 2) - vec(0, self.jump_height)
                for a in range(0, 360, 120)
            ]
            pygame.draw.polygon(self.screen, (0, 0, 0), shadow_points)
            pygame.draw.polygon(self.screen, (100, 100, 100), points)