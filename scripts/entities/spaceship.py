import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import math

from scripts.utils.CORE_FUNCS import vec, lerp, Timer
from scripts.utils.sprite_animator import SpriteAnimator
from scripts.config.SETTINGS import WIDTH, HEIGHT, Z_LAYERS, FPS

    ##############################################################################################

class Spaceship(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}
        path = "assets/entities/spaceship"
        for anim in os.listdir(path):
            imgs = []
            for move_name in os.listdir(f"{path}/{anim}"):
                img = pygame.image.load(f"{path}/{anim}/{move_name}").convert_alpha()
                img = pygame.transform.scale(img, pygame.math.Vector2(img.get_size()) * 1.5)
                img.set_colorkey((0, 0, 0))
                imgs.append(img)
            animator = SpriteAnimator(imgs, animation_speed=0.2)
            cls.SPRITES[anim.lower()] = animator

    def __init__(self, game, groups: list[pygame.sprite.Group]):
        super().__init__(groups)

        self.game = game
        self.screen = self.game.screen

        self.sprites = Spaceship.SPRITES
        self.status = "idle"
        self.z = Z_LAYERS["player"]
        self.rect = self.image.get_rect(topleft=(WIDTH/2, HEIGHT/2))

        self.angle = 0
        self.mouse_control = True
        self.stage = 0 #0 = normal, 1 = go to bottom of stage, 2 = go to center and scale
        self.pause = Timer(FPS * 5, 1)
        
    @property
    def image(self) -> pygame.Surface:
        spr = self.current_sprite.get_sprite()
        return spr

    @property
    def current_sprite(self) -> SpriteAnimator:
        return self.sprites.get(self.status, self.sprites["idle"])
            
        ###################################################################################### 

    def move(self):
        mousePos = vec(pygame.mouse.get_pos())
        self.rect.center = vec(self.rect.center).lerp(mousePos, 0.1)

        if mousePos.distance_to(vec(self.rect.center)) > self.rect.width/2:
            self.change_status("flying")
        else:
            self.change_status("idle")

        if mousePos.distance_to(vec(self.rect.center)) > self.rect.width/4:
            dy = self.rect.centery - mousePos.y
            dx = self.rect.centerx - mousePos.x
            self.angle = math.atan2(dx, dy)
            
        ###################################################################################### 
        
    def change_status(self, status):
        if status != self.status:
            self.current_sprite.reset_frame()
            self.status = status

    def animate(self):
        self.current_sprite.next(self.game.dt)
            
        ###################################################################################### 

    def update(self):
        if self.mouse_control:
            self.move()
        else:
            self.angle /= 1.25
            self.change_status("flying")

            if self.stage == 1:
                self.rect.center = vec(self.rect.center).lerp(vec(WIDTH/2, HEIGHT - self.image.get_height()/2 - 10), 0.1)
                if vec(self.rect.center).distance_to(vec(WIDTH/2, HEIGHT - self.image.get_height()/2 - 10)) < self.rect.width/2:
                    self.rect.center = vec(WIDTH/2, HEIGHT - self.image.get_height()/2 - 10)
                    self.stage = 2

            elif self.stage == 2:
                self.pause.update()
                if self.pause.finished:
                    self.rect.center = vec(self.rect.center).lerp(vec(WIDTH/2, HEIGHT/2), 0.001)

        self.animate()
        self.draw()

    def draw(self):
        image = self.image.copy()
        image = pygame.transform.rotate(image, math.degrees(self.angle))

        if self.stage == 2:
            sf = vec(self.rect.center).distance_to(vec(WIDTH/2, HEIGHT/2)) / (HEIGHT/2.5)
            image = pygame.transform.scale(image, vec(image.get_size())*sf)

        rotated_rect = image.get_rect(center=self.rect.center)
        self.screen.blit(image, rotated_rect.topleft - self.game.offset)

    ##############################################################################################

class Spaceship_Side(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}
        path = "assets/entities/spaceship_side"
        for anim in os.listdir(path):
            imgs = []
            for move_name in os.listdir(f"{path}/{anim}"):
                img = pygame.image.load(f"{path}/{anim}/{move_name}").convert_alpha()
                img = pygame.transform.scale(img, pygame.math.Vector2(img.get_size()) * 3)
                img.set_colorkey((0, 0, 0))
                imgs.append(img)
            animator = SpriteAnimator(imgs, animation_speed=0.2)
            cls.SPRITES[anim.lower()] = animator

    def __init__(self, game, groups: list[pygame.sprite.Group]):
        super().__init__(groups)

        self.game = game
        self.screen = self.game.screen

        self.sprites = Spaceship_Side.SPRITES
        self.status = "flying"
        self.z = Z_LAYERS["player"]
        self.rect = self.image.get_rect(topleft=(-self.image.get_width() * 2, HEIGHT/2 - self.image.get_height()/2))
        self.final_pos = (30, HEIGHT/2 - self.image.get_height()/2)

        self.angle = 0
        self.pause = Timer(FPS * 5, 1)
        self.grey = False

        self.fall_timer = 77
        
    @property
    def image(self) -> pygame.Surface:
        spr = self.current_sprite.get_sprite()
        return spr

    @property
    def current_sprite(self) -> SpriteAnimator:
        return self.sprites.get(self.status, self.sprites["flying"])
            
        ######################################################################################

    def grey_switch(self):
        self.grey = True
            
        ###################################################################################### 
        
    def change_status(self, status):
        if status != self.status:
            self.current_sprite.reset_frame()
            self.status = status

    def animate(self):
        self.current_sprite.next(self.game.dt)
            
        ###################################################################################### 

    def fall(self):
        self.fall_timer += 1
        y = (1/200) * ((self.fall_timer - 78) ** 2) + 200
        self.rect.center = (self.fall_timer, y)

        gradient = (self.fall_timer - 78) / 100
        self.angle = -math.degrees(math.atan(gradient))
            
        ###################################################################################### 

    def update(self):
        self.animate()
        self.draw()

    def draw(self):
        image = self.image.copy()
        if self.grey: pygame.transform.grayscale(image, image)
        if self.status == "no_power": image = pygame.transform.rotate(image, self.angle)
        
        self.screen.blit(image, self.rect.topleft - self.game.offset)


class Spaceship_Fidget_Spinner(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        cls.SPRITES = {}
        path = "assets/entities/spaceship_fidget_spinner"
        for anim in os.listdir(path):
            imgs = []
            for move_name in os.listdir(f"{path}/{anim}"):
                img = pygame.image.load(f"{path}/{anim}/{move_name}").convert_alpha()
                img = pygame.transform.scale(img, pygame.math.Vector2(img.get_size()) * 2.5)
                img.set_colorkey((0, 0, 0))
                pygame.transform.grayscale(img, img)
                imgs.append(img)
            animator = SpriteAnimator(imgs, animation_speed=0.2)
            cls.SPRITES[anim.lower()] = animator

    def __init__(self, game, groups: list[pygame.sprite.Group]):
        super().__init__(groups)

        self.game = game
        self.screen = self.game.screen

        self.sprites = Spaceship_Fidget_Spinner.SPRITES
        self.status = "idle"
        self.z = Z_LAYERS["player"]
        self.rect = self.image.get_rect(center=(208, -58))

        self.angle = math.atan2(1.75, 1)
        self.speed = 2.4
        self.rot = 0
        self.rot_speed = 12

    @property
    def image(self) -> pygame.Surface:
        spr = self.current_sprite.get_sprite()
        return spr

    @property
    def current_sprite(self) -> SpriteAnimator:
        return self.sprites.get(self.status, self.sprites["idle"])
            
        ###################################################################################### 
        
    def change_status(self, status):
        if status != self.status:
            self.current_sprite.reset_frame()
            self.status = status

    def animate(self):
        self.current_sprite.next(self.game.dt)
            
        ###################################################################################### 

    def move(self):
        radians = self.angle
        self.rect.topleft += vec(math.cos(radians), math.sin(radians)) * self.speed

        self.rot += self.rot_speed
            
        ###################################################################################### 

    def update(self):
        self.move()
        self.animate()
        self.draw()

    def draw(self):
        image = self.image.copy()
        image = pygame.transform.rotate(image, self.rot)
        rotated_rect = image.get_rect(center=self.rect.center)
        
        self.screen.blit(image, rotated_rect.topleft - self.game.offset)