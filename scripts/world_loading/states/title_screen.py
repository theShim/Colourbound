import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random, math

from scripts.entities.spaceship import Spaceship
from scripts.gui.titlecard import Titlecard
from scripts.gui.custom_fonts import Custom_Font
from scripts.gui.menu_buttons import Settings_Button, Sound_Button, Music_Button, Controls_Button

from scripts.particles.star import Star_3D
from scripts.world_loading.state_machine import State

from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class Title_Screen(State):
    def __init__(self, game):
        super().__init__(game, "title_screen")

        self.bg = pygame.Surface((WIDTH, HEIGHT))
        self.bg.set_alpha(60)

        self.stars = pygame.sprite.Group()
        for i in range(300):
            Star_3D(game, [self.stars])

        self.spaceship = Spaceship(self.game, [])

        self.titlecard = Titlecard(self.game)
        self.font = Custom_Font.Fluffy
        self.alpha = 0

        self.black = pygame.Surface((WIDTH, HEIGHT))
        self.black.fill((0, 0, 0))
        self.black_alpha = 455
        self.black.set_alpha(self.black_alpha)

        self.menu_buttons = pygame.sprite.Group()
        self.controls_button = Controls_Button(self.game, [self.menu_buttons])
        self.settings_button = Settings_Button(self.game, [self.menu_buttons])
        self.sound_button = Sound_Button(self.game, [self.menu_buttons])
        self.music_button = Music_Button(self.game, [self.menu_buttons])

        self.bg_music = "title_screen"
        self.start = True

    def update(self):
        self.screen.blit(self.bg, (0, 0))
        
        self.stars.update()
        self.spaceship.update()
        self.titlecard.update()

        self.menu_buttons.update()

        if self.controls_button.clicked:
            self.settings_button.clicked = False
            
        if self.settings_button.clicked:
            self.sound_button.direction = True
            self.music_button.direction = True
        else:
            self.sound_button.direction = self.sound_button.clicked = False
            self.music_button.direction = self.music_button.clicked = False

        if self.titlecard.exit_flag == False and self.controls_button.controls.direction == False:
            self.alpha += math.radians(1)
            txt = "Press SPACE to Start"
            self.font.render(self.screen, txt, (50, 50, 50), ((2 + WIDTH-self.font.calc_surf_width(txt))/2, 2 + 30 + HEIGHT/2 - self.font.space_height/2), alpha=155 * math.sin(self.alpha) + 100)
            self.font.render(self.screen, txt, (200, 200, 200), ((WIDTH-self.font.calc_surf_width(txt))/2, 30 + HEIGHT/2 - self.font.space_height/2), alpha=155 * math.sin(self.alpha) + 100)

        if self.start:
            if self.black_alpha > 0:
                self.black_alpha -= 5
                self.black.set_alpha(min(255, self.black_alpha))
                self.screen.blit(self.black, (0, 0))
                return
            else:
                self.black_alpha = 0
                self.start = False

        if self.spaceship.stage == 0:
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                self.titlecard.exit_flag = True
                self.spaceship.stage = 1
                for button in self.menu_buttons.sprites():
                    button.direction = button.clicked = False

        if self.titlecard.exit_flag:
            self.titlecard.exit()
            self.spaceship.mouse_control = False
        if self.spaceship.stage == 2:      
            if not self.game.music_player.is_playing("sfx"):
                self.game.music_player.play("warp_speed", "sfx")
                self.game.music_player.set_vol(vol=0.5, channel="sfx")

            self.game.music_player.set_vol((400 - ((180/math.pi) * Star_3D.angle)) / 400, channel="bg")

            Star_3D.update_angle()

        if (180/math.pi) * Star_3D.angle > 900:
            self.black_alpha += 5
            self.black.set_alpha(self.black_alpha)
            self.screen.blit(self.black, (0, 0))
            self.game.music_player.stop("bg")

        self.game.debugger.add_text(str(self.game.music_player.is_playing("sfx")))

        if (180/math.pi) * Star_3D.angle > 1200:
            # if not self.game.music_player.is_playing("sfx"):
                self.game.state_loader.add_state(self.game.state_loader.states["cutscene_1"])
                self.stars.empty()
                Star_3D.angle = 0