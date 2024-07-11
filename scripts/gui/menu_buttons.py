import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

from scripts.utils.CORE_FUNCS import vec
from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class Button(pygame.sprite.Sprite):
    def __init__(self, game, groups, name, pos, end_pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        path = "assets/gui"
        self.base_surf = pygame.image.load(f"{path}/{name}_0.png").convert_alpha()
        self.base_surf.set_colorkey((0, 0, 0))
        self.base_surf = pygame.transform.scale(self.base_surf, vec(self.base_surf.get_size()) * 1.25)
        self.clicked_surf = pygame.image.load(f"{path}/{name}_1.png").convert_alpha()
        self.clicked_surf.set_colorkey((0, 0, 0))
        self.clicked_surf = pygame.transform.scale(self.clicked_surf, vec(self.clicked_surf.get_size()) * 1.25)

        self.o_pos = vec(pos).copy()
        self.pos = vec(pos)
        self.end_pos = vec(end_pos)

        self.clicked = False
        self.held = False
        self.hovered = False
        self.new = False

        self.slider = None

    def mouse(self):
        mousePos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()

        self.hovered = False
        if self.rect.collidepoint(mousePos):
            self.hovered = True

            if mouse[0]:
                if self.held == False:
                    self.held = True
                    self.clicked = not self.clicked
                    self.new = True
            else:
                self.held = False

    def action(self):
        pass
            

    def update(self):
        self.rect = self.base_surf.get_rect(topleft=self.pos)
        self.mouse()
        self.action()

        self.draw()

    def draw(self):
        if self.slider:
            self.slider.update(self.game.music_player)

        if self.clicked or self.hovered:
            self.screen.blit(self.clicked_surf, self.rect)
        else:
            self.screen.blit(self.base_surf, self.rect)



class Settings_Button(Button):
    def __init__(self, game, groups):
        super().__init__(game, groups, "settings", (WIDTH - 55, HEIGHT + 30), (WIDTH - 55, HEIGHT - 45))
        self.move_flag = True
        self.spring_vel = vec(0, 0)
        self.stiffness = 0.2
        self.damping = 0.2

    def action(self):
        if self.move_flag:
            self.spring_vel = self.spring_vel.lerp((self.end_pos - self.pos) * self.stiffness, self.damping)
            self.pos += self.spring_vel
        else:
            self.spring_vel = self.spring_vel.lerp((self.o_pos - self.pos) * self.stiffness, (self.damping))
            self.pos += self.spring_vel

        if self.new:
            if self.clicked:
                for spr in self.groups()[0]:
                    if spr != self:
                        spr.move_flag = True
                        spr.spring_vel = vec()
            else:
                for spr in self.groups()[0]:
                    if spr != self:
                        spr.move_flag = False
                        spr.spring_vel = vec()
            self.new = False

class Sound_Button(Button):
    def __init__(self, game, groups):
        super().__init__(game, groups, "sound", (WIDTH - 100, HEIGHT + 30), (WIDTH - 100, HEIGHT - 45))
        self.move_flag = False
        self.spring_vel = vec(0, 0)
        self.stiffness = 0.2
        self.damping = 0.2

        self.slider = Sound_Slider(self.game, (WIDTH - 100, HEIGHT - 50))

    def action(self):
        if self.move_flag:
            self.spring_vel = self.spring_vel.lerp((self.end_pos - self.pos) * self.stiffness, self.damping)
            self.pos += self.spring_vel + vec(0, 0)
        else:
            self.spring_vel = self.spring_vel.lerp((self.o_pos - self.pos) * self.stiffness, (self.damping))
            self.pos += self.spring_vel

class Music_Button(Button):
    def __init__(self, game, groups):
        super().__init__(game, groups, "music", (WIDTH - 145, HEIGHT + 30), (WIDTH - 145, HEIGHT - 45))   
        self.move_flag = False
        self.spring_vel = vec(0, 0)
        self.stiffness = 0.2
        self.damping = 0.2

    def action(self):
        if self.move_flag:
            self.spring_vel = self.spring_vel.lerp((self.end_pos - self.pos) * self.stiffness, self.damping)
            self.pos += self.spring_vel + vec(0, 0)
        else:
            self.spring_vel = self.spring_vel.lerp((self.o_pos - self.pos) * self.stiffness, (self.damping))
            self.pos += self.spring_vel


class Sound_Slider(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        self.screen = self.game.screen

        self.pos = pos

        self.base = pygame.Surface((7, 27))
        self.base.fill((20, 16,32))

    def update(self, mixer):
        self.draw()

    def draw(self):
        self.screen.blit(self.base, self.base.get_rect(bottomleft=self.pos))



    # class Volume_Slider(pygame.sprite.Sprite):
    #     def __init__(self, parent, mixer, pos):
    #         super().__init__()
    #         self.parent = parent
    #         self.mixer = mixer
    #         self.pos = pos

    #         self.base = pygame.Surface((72, 7), pygame.SRCALPHA)
    #         self.base.fill((20, 16, 32))
    #         self.base.fill((39, 37, 60), [0, 0, 72, 2])
    #         self.base = pygame.transform.scale(self.base, vec(self.base.get_size()) * 3)
    #         pygame.draw.rect(self.base, (1, 0, 0), self.base.get_rect(), 3)

    #         self.knob = Player_Menu.Volume_Knob(self, self.mixer, 
    #                                             [self.pos[0] + 3, self.pos[1] - 6], 
    #                                             [self.pos[0] + self.base.get_width() - 33 - 3, self.pos[1] - 6])

    #     def update(self, screen):
    #         screen.blit(self.base, self.pos)

    #         pygame.draw.rect(screen, [17, 158, 214], [self.pos[0] + 3, self.pos[1] + 3, int(self.knob.pos.x - self.knob.start.x), 3])
    #         pygame.draw.rect(screen, [65, 243, 252], [self.pos[0] + 3, self.pos[1] + 6, int(self.knob.pos.x - self.knob.start.x), 12])

    #         vol = str(int(self.mixer.volumes[0] * 100))
    #         Custom_Font.Fluffy.render(screen, str(vol), (41, 39, 62), [self.pos[0] + self.base.get_width() + 11, self.pos[1] + 5])
    #         Custom_Font.Fluffy.render(screen, str(vol), (210, 210, 210), [self.pos[0] + self.base.get_width() + 10, self.pos[1] + 4])

    #         Custom_Font.Fluffy.render(screen, "Music:", (41, 39, 62), [self.pos[0] - Custom_Font.Fluffy.calc_surf_width("Music:") - 4, self.pos[1] + 5])
    #         Custom_Font.Fluffy.render(screen, "Music:", (210, 210, 210), [self.pos[0] - Custom_Font.Fluffy.calc_surf_width("Music:") - 5, self.pos[1] + 4])

    #         self.knob.update(screen)

    # class Volume_Knob(pygame.sprite.Sprite):
    #     def __init__(self, parent, mixer, start, end):
    #         super().__init__()
    #         self.parent = parent
    #         self.mixer = mixer

    #         self.start = vec(start)
    #         self.end = vec(end)
    #         self.pos = vec(end)

    #         self.base = pygame.Surface((14-3, 14-3), pygame.SRCALPHA)
    #         self.base.fill((57, 58, 74))
    #         pygame.draw.rect(self.base, (1, 0, 0), self.base.get_rect(), 1)
    #         pygame.draw.line(self.base, (20, 16, 32), [2, 2], [2, 11-3])
    #         pygame.draw.line(self.base, (20, 16, 32), [11-3, 2], [11-3, 11-3])
    #         pygame.draw.line(self.base, (30, 23, 48), [3, 2], [10-3, 2])
    #         pygame.draw.line(self.base, (30, 23, 48), [3, 11-3], [10-3, 11-3])
    #         self.base = pygame.transform.scale(self.base, vec(self.base.get_size())*3)

    #         self.held = False

    #     def clamp_pos(self):
    #         if self.pos.x < self.start.x:
    #             self.pos.x = self.start.x
    #         if self.pos.x > self.end.x:
    #             self.pos.x = self.end.x

    #     def change_volume(self):
    #         dist = abs(self.start.x - self.pos.x)
    #         vol = dist / (self.end.x - self.start.x)
    #         self.mixer.set_vol(vol, "bg")

    #     def move(self):
    #         mouse = pygame.mouse.get_pressed()
    #         mousePos = pygame.mouse.get_pos()

    #         if mouse[0]:
    #             if self.held == False:
    #                 if self.base.get_rect(topleft=self.pos).collidepoint(mousePos):
    #                     self.held = True
    #             else:
    #                 self.pos.x = mousePos[0] - self.base.get_width()/2
    #                 self.clamp_pos()
    #                 self.change_volume()
    #         else:
    #             self.held = False

    #     def update(self, screen):
    #         self.move()

    #         screen.blit(self.base, self.pos)
    #         if self.base.get_rect(topleft=self.pos).collidepoint(pygame.mouse.get_pos()) or self.held:
    #             pygame.draw.rect(screen, [65, 243, 252], [self.pos.x + 6, self.pos.y + 6, 3, 21])
    #             pygame.draw.rect(screen, [65, 243, 252], [self.pos.x + self.base.get_width() - 9, self.pos.y + 6, 3, 21])
    #             pygame.draw.rect(screen, [17, 158, 214], [self.pos.x + 6, self.pos.y + 6, 21, 3])
    #             pygame.draw.rect(screen, [17, 158, 214], [self.pos.x + 6, self.pos.y + self.base.get_height() - 9, 21, 3])