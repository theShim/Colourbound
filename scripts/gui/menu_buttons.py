import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.utils.CORE_FUNCS import vec, apply_rainbow, gen_rand_colour
from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class Button(pygame.sprite.Sprite):
    def __init__(self, game, groups, name, pos, end_pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.start_pos = vec(pos)
        self.end_pos = vec(end_pos)
        self.pos = self.start_pos.copy()

        self.direction = False
        self.spring_vel = vec(0, 0)
        self.stiffness = 0.1
        self.damping = 0.3

        path = "assets/gui"
        self.base_surf = pygame.image.load(f"{path}/{name}_0.png").convert_alpha()
        self.base_surf.set_colorkey((0, 0, 0))
        self.base_surf = pygame.transform.scale(self.base_surf, vec(self.base_surf.get_size()) * 1.25)
        self.clicked_surf = pygame.image.load(f"{path}/{name}_1.png").convert_alpha()
        self.clicked_surf.set_colorkey((0, 0, 0))
        self.clicked_surf = pygame.transform.scale(self.clicked_surf, vec(self.clicked_surf.get_size()) * 1.25)

        self.rect = self.base_surf.get_rect(topleft=self.pos)

        self.clicked = False
        self.hovered = False

    def mouse(self):
        mousePos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()

        self.hovered = False
        if self.rect.collidepoint(mousePos):
            self.hovered = True

        if mouse[0]:
            if self.rect.collidepoint(mousePos):
                if self.held == False:
                    self.held = True
                    self.clicked = not self.clicked
        else:
            self.held = False

        self.rect = self.base_surf.get_rect(topleft=self.pos)

    def spring_move_to_dest(self):
        if self.direction:
            self.spring_vel = self.spring_vel.lerp((self.end_pos - self.pos) * self.stiffness, (self.damping))
            self.pos += self.spring_vel
        else:
            self.spring_vel = self.spring_vel.lerp((self.start_pos - self.pos) * self.stiffness, (self.damping))
            self.pos += self.spring_vel

    def draw(self):
        if self.clicked or self.hovered:
            self.screen.blit(self.clicked_surf, self.rect)
        else:
            self.screen.blit(self.base_surf, self.rect)

            ##############################################################################

class Settings_Button(Button):
    def __init__(self, game, groups):
        super().__init__(game, groups, "settings", (WIDTH - 55, HEIGHT + 30), (WIDTH - 55, HEIGHT - 45))
        self.direction = True

    def update(self):
        self.spring_move_to_dest()
        self.mouse()

        self.draw()

class Sound_Button(Button):
    def __init__(self, game, groups):
        super().__init__(game, groups, "sound", (WIDTH - 100, HEIGHT + 30), (WIDTH - 100, HEIGHT - 45))
        self.slider = Sound_Slider(game)

    def update(self):
        self.spring_move_to_dest()
        if not self.slider.held:
            self.mouse()

        if self.clicked:
            self.slider.direction = True
        else:
            self.slider.direction = False
        self.slider.update()

        self.draw()


class Music_Button(Button):
    def __init__(self, game, groups):
        super().__init__(game, groups, "music",(WIDTH - 145, HEIGHT + 30), (WIDTH - 145, HEIGHT - 45))
        self.slider = Music_Slider(game)

    def update(self):
        self.spring_move_to_dest()
        if not self.slider.held:
            self.mouse()

        if self.clicked:
            self.slider.direction = True
        else:
            self.slider.direction = False
        self.slider.update()

        self.draw()

    ##############################################################################################

class Slider(pygame.sprite.Sprite):
    def __init__(self, game, start_pos, final_pos):
        self.game = game
        self.screen = self.game.screen

        self.start_pos = vec(start_pos)
        self.final_pos = vec(final_pos)
        self.pos = self.start_pos.copy()

        self.direction = False
        self.spring_vel = vec(0, 0)
        self.stiffness = 0.2
        self.damping = 0.2

        self.frame = pygame.image.load("assets/gui/slider.png").convert_alpha()
        self.frame = pygame.transform.scale(self.frame, vec(self.frame.get_size()) * 1.25)
        self.frame.set_colorkey((0, 0, 0))

        self.knob = pygame.image.load("assets/gui/knob.png").convert_alpha()
        self.knob = pygame.transform.scale(self.knob, vec(self.knob.get_size()) * 1.25)
        self.knob.set_colorkey((0, 0, 0))

        self.knob_min = vec(5, self.frame.get_height() - self.knob.get_height() - 10)
        self.knob_max = vec(5, 5)
        self.knob_pos = self.knob_max.copy()
        self.held = False

        self.channel = None
        self.last_vol = 1.0
        
        self.slider_fill = pygame.Surface((self.frame.get_width() - 10, self.frame.get_height() - 10), pygame.SRCALPHA)
        self.slider_fill.fill((120, 120, 120))
        self.animation_period = 700
        self.elapsed_time = random.randint(0, 700)

    def spring_move_to_dest(self):
        if self.direction:
            self.spring_vel = self.spring_vel.lerp((self.final_pos - self.pos) * self.stiffness, (self.damping))
            self.pos += self.spring_vel
        else:
            self.spring_vel = self.spring_vel.lerp((self.start_pos - self.pos) * self.stiffness, (self.damping))
            self.pos += self.spring_vel

    def knob_move(self):
        knob_rect = self.knob.get_rect(topleft=self.knob_pos + vec(self.pos.x, (self.pos.y - self.frame.height)))
        
        if pygame.mouse.get_pressed()[0]:
            if self.held == False:
                if knob_rect.collidepoint(pygame.mouse.get_pos()):
                    self.held = True
        else:
            self.held = False

        if self.held:
            self.knob_pos.y = pygame.mouse.get_pos()[1] - self.pos.y + self.frame.height

    def clamp_pos(self):
        if self.knob_pos.y > self.knob_min.y:
            self.knob_pos.y = self.knob_min.y
        if self.knob_pos.y < self.knob_max.y:
            self.knob_pos.y = self.knob_max.y

    def change_vol(self, mixer):
        dist = abs(self.knob_min.y - self.knob_pos.y)
        vol = dist / abs(self.knob_max.y - self.knob_min.y)
        if vol != self.last_vol:
            self.last_vol = vol
            mixer.set_vol(vol, self.channel)

    def update(self):
        self.spring_move_to_dest()

        if self.spring_vel.magnitude() < 1:
            self.knob_move()
        self.clamp_pos()
        self.change_vol(self.game.music_player)

        self.elapsed_time += self.game.dt * 1000

        self.draw()

    def draw(self):
        fill = self.slider_fill.copy()
        fill = apply_rainbow(
            fill,
            offset=(self.animation_period - self.elapsed_time) / self.animation_period,
            bands=1.5
        )
        fill = fill.subsurface([0, self.knob_pos.y, fill.get_width(), fill.get_height() - self.knob_pos.y])
        self.screen.blit(fill, self.frame.get_rect(bottomleft=self.pos + vec(5, self.knob_pos.y)))

        frame = self.frame.copy()
        frame.blit(self.knob, self.knob_pos)
        self.screen.blit(frame, frame.get_rect(bottomleft=self.pos))

class Sound_Slider(Slider):
    def __init__(self, game):
        super().__init__(game, (WIDTH-100, HEIGHT + 150), (WIDTH - 100, HEIGHT - 50))
        self.direction = True
        self.channel = "all"

class Music_Slider(Slider):
    def __init__(self, game):
        super().__init__(game, (WIDTH-145, HEIGHT + 150), (WIDTH - 145, HEIGHT - 50))
        self.direction = True
        self.channel = "bg"