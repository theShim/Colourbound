import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import random
import sys
import math
import time
import numpy as np

    ##############################################################################################

#initialising pygame stuff
pygame.init()  #general pygame
pygame.font.init() #font stuff
pygame.mixer.pre_init(44100, 16, 2, 4096) #music stuff
pygame.mixer.init()
pygame.event.set_blocked(None) #setting allowed events to reduce lag
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
pygame.display.set_caption("")

#initalising pygame window
flags = pygame.DOUBLEBUF #| pygame.FULLSCREEN
SIZE = WIDTH, HEIGHT = (720, 720)
screen = pygame.display.set_mode(SIZE, flags)
clock = pygame.time.Clock()

#renaming common functions
vec = pygame.math.Vector2

#useful functions
def gen_colour():
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

def euclidean_distance(point1, point2):
    return vec(point1).distance_to(vec(point2))

def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    angle = math.radians(angle)

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return vec(qx, qy)

    ##############################################################################################

def grayscale(img):
    return pygame.transform.grayscale(img)

grass_block = pygame.transform.scale((img := pygame.image.load("1.png").convert_alpha()), vec(img.get_size()) * 8)
bg = grass_block.copy()
grey = grayscale(grass_block)

    ##############################################################################################

last_time = time.time()

running = True
while running:

    dt = time.time() - last_time
    last_time = time.time()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    mousePos = pygame.mouse.get_pos()
    r = 100
    circle = pygame.Surface((r, r), pygame.SRCALPHA)
    pygame.draw.circle(circle, (255, 255, 255, 255), (r/2, r/2), r/2)
    grey.blit(circle, circle.get_rect(center=vec(mousePos) - vec(100, 100)), special_flags=pygame.BLEND_RGBA_SUB)

    arr = pygame.surfarray.array3d(grey)
    clear = np.all(arr == [0, 0, 0], axis=-1)
    # num = np.sum(clear)
    is_all_black = np.all(arr == [0, 0, 0])

    screen.fill((30, 30, 30))
    screen.blit(bg, (100, 100))
    screen.blit(grey, (100, 100))


    #fps
    font = pygame.font.SysFont('monospace', 30)
    fps = font.render(f'FPS: {int(clock.get_fps())}\n{int(100 * np.sum(clear) / (grey.get_width() * grey.get_height()))}%\n{is_all_black}', True, (215, 215, 215))
    screen.blit(fps, (0, 0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()