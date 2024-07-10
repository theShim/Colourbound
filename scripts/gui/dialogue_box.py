import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import colorsys
import math

from scripts.gui.custom_fonts import Custom_Font
from scripts.utils.CORE_FUNCS import vec, Timer
from scripts.utils.sprite_animator import SpriteAnimator
from scripts.config.SETTINGS import FPS, DEBUG

    ##############################################################################################

"""
38 CHARACTERS PER LINE
3 LINES HEIGHT WISE
THEREFORE TOTAL TEXT LENGTH <= 114
"""

    ##############################################################################################

class Dialogue_Box(pygame.sprite.Sprite):
    def __init__(self, game, pos: tuple | vec, person_name: str, texts: list[str], speed:float = 0.4, start_up_delay=0):
        super().__init__()
        self.game = game
        self.screen = self.game.screen

        self.pos = pos
        self.name_pos = pos + vec(150, 18)
        self.writing_pos = pos + vec(150, 35)
        self.font = Custom_Font.Fluffy
        self.texts = texts
        self.text_counter = 0
        self.text = self.texts[self.text_counter]

        self.t = 0
        self.prev = self.t
        self.og_speed = speed if not DEBUG else 2
        self.speed = self.og_speed
        self.finished = False

        # self.typing_sounds_flag = typing_sounds_flag
        # self.clack = False      #typing sound

        self.name = person_name if person_name.lower() != "ship_grey" else "Ship"
        self.background = pygame.image.load(f"assets/gui/dialogue_{person_name.lower()}.png").convert_alpha()
        self.background = pygame.transform.scale(self.background, vec(self.background.get_size()) * 4.5)
        self.background.set_colorkey((0, 0, 0))
        self.shadow = pygame.image.load("assets/gui/dialogue_shadow.png").convert_alpha()
        self.shadow = pygame.transform.scale(self.shadow, vec(self.background.get_size()))
        self.shadow.set_colorkey((0, 0, 0))

        self.start_up_delay = start_up_delay
        self.delay_timer = Timer(start_up_delay, 1)
        self.other_delay_timer = Timer(FPS/4, 1)

        self.end_delay  = start_up_delay
        self.end_flag = False

        self.press_spacebar = Press_Spacebar(game)
        self.waiting = False
            
        ###################################################################################### 

    def reset(self):
        self.t = 0
        self.finished = False

    def end(self):
        self.t = len(self.text)
        self.finished = True
    
    def finish(self):
        self.t = len(self.text)
        self.finished = True

    def change_speed(self, speed):
        self.speed = speed

    def next_text(self):
        self.waiting = True
        if pygame.key.get_just_pressed()[pygame.K_SPACE] or self.end_flag:
            self.text_counter += 1
            if self.text_counter < len(self.texts):
                self.text = self.texts[self.text_counter]
                self.reset()
            else:
                if self.end_flag == False:
                    self.end_flag = True
                    self.delay_timer.reset()
                else:
                    self.finished = True
            
        ###################################################################################### 

    def update(self):
        self.waiting = False

        self.delay_timer.update()
        if self.other_delay_timer.finished and not self.delay_timer.finished:
            return
        
        elif not self.delay_timer.finished:
            return
        else:
            self.other_delay_timer.update()
            if not self.other_delay_timer.finished:
                return
        
        # put into another method
        # self.clack = False
        # if abs(self.t - self.prev) >= 1:
        #     self.prev = self.t
        #     self.clack = True

        if self.t < len(self.text):
            self.t += self.speed
        else:
            self.next_text()
            return

        if self.text[min(len(self.text)-1, int(self.t))] == "\t":
            self.change_speed(0.05)
        elif self.text[min(len(self.text)-1, int(self.t))] == ".":
            self.change_speed(0.075)
        elif self.text[min(len(self.text)-1, int(self.t))] == ",":
            self.change_speed(0.1)
        else:
            self.change_speed(self.og_speed)

    def render(self, col):
        if self.end_flag:
            return
        
        if self.other_delay_timer.finished and not self.delay_timer.finished:
            sf = 1 - self.delay_timer.t / self.end_delay
            background = self.background.copy()
            self.font.render(background, self.name, (20, 20, 20), vec(150, 18) + vec(1, 1))
            self.font.render(background, self.name, (255, 255, 255), vec(150, 18))
            background = pygame.transform.scale(background, vec(self.background.get_size()) * sf)
            shadow = pygame.transform.scale(self.shadow, vec(self.background.get_size()) * sf)

            scaled_rect = background.get_rect(center=self.background.get_rect(topleft=self.pos).center)
            self.screen.blit(shadow, scaled_rect.topleft + vec(2, 2))
            self.screen.blit(background, scaled_rect.topleft)


        elif self.delay_timer.finished and self.other_delay_timer.finished:
            background = self.background.copy()
            if self.waiting:
                self.press_spacebar.update(background)

            text = f"{self.text[:int(self.t)]}"
            self.screen.blit(self.shadow, self.pos + vec(2, 2))
            self.screen.blit(background, self.pos)
            self.font.render(self.screen, self.name, (20, 20, 20), self.name_pos + vec(1, 1))
            self.font.render(self.screen, self.name, (255, 255, 255), self.name_pos)
            self.font.render(self.screen, text, col, self.writing_pos)

        else:
            sf = self.delay_timer.t / self.start_up_delay
            background = self.background.copy()
            self.font.render(background, self.name, (20, 20, 20), vec(150, 18) + vec(1, 1))
            self.font.render(background, self.name, (255, 255, 255), vec(150, 18))
            background = pygame.transform.scale(background, vec(self.background.get_size()) * sf)
            shadow = pygame.transform.scale(self.shadow, vec(self.background.get_size()) * sf)

            scaled_rect = background.get_rect(center=self.background.get_rect(topleft=self.pos).center)
            self.screen.blit(shadow, scaled_rect.topleft + vec(2, 2))
            self.screen.blit(background, scaled_rect.topleft)



class Press_Spacebar(pygame.sprite.Sprite):

    @classmethod
    def cache_sprites(cls):
        imgs = [
            pygame.image.load("assets/gui/dialogue_press_start_0.png").convert_alpha(),
            pygame.image.load("assets/gui/dialogue_press_start_1.png").convert_alpha(),
        ]
        for i in range(2):
            imgs[i] = pygame.transform.scale(imgs[i], vec(imgs[i].get_size()))
            imgs[i].set_colorkey((0, 0, 0))
        cls.animator = SpriteAnimator(imgs, animation_speed=0.05)

    def __init__(self, game):
        super().__init__()
        self.game = game

    def animate(self):
        self.animator.next(self.game.dt)
        
    def update(self, surf):
        self.animate()
        self.draw(surf)

    def draw(self, surf):
        surf.blit((spr := self.animator.get_sprite()), vec(surf.get_size()) - vec(spr.get_size()) - vec(20, 14))