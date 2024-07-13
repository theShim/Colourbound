import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import math

from data.dialogues.cutscenes import cutscene_dialogues

from scripts.entities.spaceship import Spaceship_Side, Spaceship_Fidget_Spinner
from scripts.gui.dialogue_box import Dialogue_Box
from scripts.gui.custom_fonts import Custom_Font
from scripts.particles.star import Star_3D, Falling_Down_Star
from scripts.particles.colour_void_shockwave import Shockwave_Particle
from scripts.world_loading.state_machine import Cutscene

from scripts.config.SETTINGS import WIDTH, HEIGHT, FPS
from scripts.utils.CORE_FUNCS import vec, Timer

    ##############################################################################################

class Cutscene_1(Cutscene):
    def __init__(self, game):
        super().__init__(game, "cutscene_1")
        self.window = pygame.Surface((WIDTH, HEIGHT))
        self.bg = pygame.Surface((WIDTH, HEIGHT))
        self.bg.set_alpha(60)

        self.stars = pygame.sprite.Group()
        for i in range(400):
            Star_3D(game, [self.stars], screen=self.window)

        self.spaceship = Spaceship_Side(game, [])

        self.black = pygame.Surface((WIDTH, HEIGHT))
        self.black.fill((0, 0, 0))
        self.black_alpha = 255
        self.black.set_alpha(self.black_alpha)

        self.colourvoid_pos = vec(WIDTH*1.5,HEIGHT/2)
        self.colourvoid_radius = 0
        self.colourvoid_particles = pygame.sprite.Group()
        for angle in range(135, 225):
            s = Shockwave_Particle(
                self.game, [self.colourvoid_particles], math.radians(angle)
            )
            s.screen = self.window
            s = Shockwave_Particle(
                self.game, [self.colourvoid_particles], math.radians(angle+.5)
            )
            s.screen = self.window

        self.dialogues = [
            Dialogue_Box(
                self.game, 
                (81, 30), 
                "You", 
                [
                    cutscene_dialogues[1], 
                    cutscene_dialogues[2]
                ], 
                start_up_delay=FPS * 0.1
            ),
            Dialogue_Box(
                self.game,
                (81, 30),
                "Ship",
                [
                    cutscene_dialogues[3]
                ],
                start_up_delay=FPS * 0.1
            ),
            Dialogue_Box(
                self.game,
                (81, 30),
                "You",
                [
                    cutscene_dialogues[4]
                ],
                start_up_delay=FPS * 0.1
            ),
            Dialogue_Box(
                self.game,
                (81, 30),
                "You",
                [
                    cutscene_dialogues[5]
                ],
                start_up_delay=FPS * 0.1
            ),
            Dialogue_Box(
                self.game,
                (81, 30),
                "Ship_Grey",
                [
                    cutscene_dialogues[6]
                ],
                start_up_delay=FPS * 0.1
            ),
        ]
        self.dialogue_counter = 0

        self.stage_5_pause = Timer(FPS*1.5, 1)
        self.stage_7_pause = Timer(FPS*2, 1)
        self.stage_10_pause = Timer(FPS*1.5, 1)

        self.game.offset = vec()
        self.stage = 0

        self.bg_music = "into_space"

    def update(self):

        self.window.blit(self.bg, (0, 0))
        self.stars.update()
        self.screen.blit(self.window, (0, 0))
        self.spaceship.update()

        if self.stage == 0:
            self.game.music_player.stop(channel="bg")
            self.game.music_player.set_vol(vol=1, channel="bg")
            self.game.music_player.play(self.bg_music, "bg", loop=True, fade_in=1000)

            if self.black_alpha > 0:
                self.black_alpha -= 5
                self.black.set_alpha(self.black_alpha)
                self.screen.blit(self.black, (0, 0))
            else:
                self.stage = 1

        elif self.stage == 1:
            self.spaceship.rect.topleft = vec(self.spaceship.rect.topleft).lerp(self.spaceship.final_pos, 0.1)
            if self.spaceship.rect.x - self.spaceship.final_pos[0] >= -10:
                self.stage = 2

        elif self.stage == 2:
            self.dialogues[self.dialogue_counter].update()
            self.dialogues[self.dialogue_counter].render((113, 114, 227))
            
            if self.dialogues[self.dialogue_counter].finished:
                self.stage = 3 
                self.dialogue_counter += 1

        elif self.stage == 3:
            self.dialogues[self.dialogue_counter].update()
            self.dialogues[self.dialogue_counter].render((113, 114, 227))
            
            if self.dialogues[self.dialogue_counter].finished:
                self.stage = 4
                self.dialogue_counter += 1
                self.game.music_player.stop("bg", fadeout_ms=0)

        elif self.stage == 4:
            self.colourvoid_radius += 5

            for star in self.stars.sprites():
                star: Star_3D
                if not star.grey:
                    if star.project().distance_to(self.colourvoid_pos) <= self.colourvoid_radius:
                        star.grey_switch()

            if vec(self.spaceship.rect.center).distance_to(self.colourvoid_pos) <= self.colourvoid_radius:
                self.spaceship.grey_switch()

            self.colourvoid_particles.update(self.colourvoid_radius)
            self.game.music_player.play("rumble", "sfx")
            self.game.effect_manager.effects["screen shake"].start(int(FPS*0.25), intensity=2)

            if self.colourvoid_radius >= 1100:
                self.game.offset = self.game.offset.lerp(vec(0,0), 0.2)
                if self.game.offset.distance_to(vec(0, 0)) < 0.5:
                    self.game.offset = vec()
                    self.stage = 5

        elif self.stage == 5:
            self.game.music_player.stop("sfx")
            self.stage_5_pause.update()
            if self.stage_5_pause.finished:
                self.stage = 6

        elif self.stage == 6:
            self.dialogues[self.dialogue_counter].update()
            self.dialogues[self.dialogue_counter].render((113, 114, 227))
            
            if self.dialogues[self.dialogue_counter].finished:
                self.stage = 7

        elif self.stage == 7:
            self.stage_7_pause.update()
            if self.stage_7_pause.finished:
                self.stage = 8
                self.dialogue_counter += 1

        elif self.stage == 8:
            self.dialogues[self.dialogue_counter].update()
            self.dialogues[self.dialogue_counter].render((113, 114, 227))
            
            if self.dialogues[self.dialogue_counter].finished:
                self.stage = 9
                self.dialogue_counter += 1

        elif self.stage == 9:
            self.dialogues[self.dialogue_counter].update()
            self.dialogues[self.dialogue_counter].render((113, 114, 227))
            
            if self.dialogues[self.dialogue_counter].finished:
                self.spaceship.change_status("no_power")
                self.stage = 10

        elif self.stage == 10:
            self.stage_10_pause.update()
            if self.stage_10_pause.finished:
                self.spaceship.fall()

                if self.spaceship.rect.y > HEIGHT * 1.25:
                    self.stage = 11

        elif self.stage == 11:
            if self.black_alpha < 255:
                self.black_alpha += 20
                self.black.set_alpha(self.black_alpha)
                self.screen.blit(self.black, (0, 0))
            else:
                self.stars.empty()
                self.game.state_loader.add_state(self.game.state_loader.states["cutscene_2"])




class Cutscene_2(Cutscene):
    def __init__(self, game):
        super().__init__(game, "cutscene_2")
        self.window = pygame.Surface((WIDTH, HEIGHT))
        self.bg = pygame.Surface((WIDTH, HEIGHT))
        self.bg.set_alpha(60)

        self.stars = pygame.sprite.Group()
        for i in range(400):
            Falling_Down_Star(self.game, [self.stars], screen=self.window)

        self.spaceship = Spaceship_Fidget_Spinner(game, [])
        self.after_effects = []

        self.black = pygame.Surface((WIDTH, HEIGHT))
        self.black.fill((0, 0, 0))
        self.black_alpha = 255
        self.black.set_alpha(self.black_alpha)

        self.game.offset = vec()
        self.stage = 0
        self.start = -10

    def update(self):
        if not self.game.music_player.is_playing("sfx"):
            self.game.music_player.set_vol(vol=0.5, channel="sfx")
            self.game.music_player.play("falling_in_space", "sfx", fade_in=2000)

        self.window.blit(self.bg, (0, 0))
        self.stars.update()
        # for effect in self.after_effects:
        #     effect[duration] -= 5
        self.screen.blit(self.window, (0, 0))
        self.spaceship.update()

        if self.stage == 0:
            if self.black_alpha > 0:
                self.black_alpha -= 10
                self.black.set_alpha(self.black_alpha)
                self.screen.blit(self.black, (0, 0))
            else:
                self.stage = 1

        if self.stage == 1:
            if self.spaceship.rect.top > HEIGHT*1.1:
                self.stage = 2

        elif self.stage == 2:
            if self.black_alpha < 505:
                self.black_alpha += 10
                self.black.set_alpha(min(255, self.black_alpha))
                self.screen.blit(self.black, (0, 0))
            else:
                self.game.state_loader.add_state(self.game.state_loader.states["planet_1"])



class Ending(Cutscene):
    def __init__(self, game, prev):
        super().__init__(game, "ending", prev)

        self.black = pygame.Surface((WIDTH, HEIGHT))
        self.black.fill((0, 0, 0))
        self.black_alpha = 0
        self.black.set_alpha(self.black_alpha)

        self.timer = 100

        self.prev = prev
        self.stage = 0

    def update(self):
        if self.black_alpha > 0 and self.stage == 0:
            self.prev.render()

        if self.stage == 0:
            if self.black_alpha < 255:
                self.black_alpha += 10
            else:
                self.black_alpha = 255
                self.stage = 1
            self.black.set_alpha(self.black_alpha)
            self.game.screen.blit(self.black, (0, 0))

        else:
            self.game.screen.fill((0, 0, 0))

        if self.stage == 1:
            self.game.music_player.stop("all", fadeout_ms=5000)
            self.timer -= 1
            if self.timer == 0:
                self.stage = 2

        elif self.stage == 2:
            text = "sorry i ran out of time bruh. press ESCAPE to quit"
            size = Custom_Font.Fluffy.calc_surf_width(text)
            Custom_Font.Fluffy.render(self.game.screen, text, (255, 255, 255), (100, 100))