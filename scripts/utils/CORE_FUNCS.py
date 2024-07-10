import pygame
import math
import random
import json
import numpy as np

    ##############################################################################################

#   RENAMING COMMON FUNCTIONS
vec = pygame.math.Vector2
vec3 = pygame.math.Vector3

    ##############################################################################################

#   GENERAL STUFF
def gen_rand_colour(vibrant=False) -> tuple[float] | pygame.Color:
    if vibrant:
        return pygame.Color.from_hsva([random.randint(0, 255), 100, 80, 100])
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

def euclidean_distance(point1: list[float], point2: list[float]) -> float:
    return (((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2) ** 0.5)

def rotate(origin: list, point: list, angle: float) -> list[float]:
    ox, oy = origin
    px, py = point
    angle = math.radians(angle)

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return [qx, qy]

def lerp(a: float, b: float, lerp_factor: float) -> float:
    return (lerp_factor * a) + ((1 - lerp_factor) * b)

def normalize(val, amt, target):
    if val > target + amt:
        val -= amt
    elif val < target - amt:
        val += amt
    else:
        val = target
    return val

#bezier stuff
def ptOnCurve(b, t):
    q = b.copy()
    for k in range(1, len(b)):
        for i in range(len(b) - k):
            q[i] = (1-t) * q[i][0] + t * q[i+1][0], (1-t) * q[i][1] + t * q[i+1][1]
    return round(q[0][0]), round(q[0][1])

def bezierfy(points, samples): #no idea how this works just does, i think it's just recursive lerping though
    pts = [ptOnCurve(points, i/samples) for i in range(samples+1)]
    return pts


def crop(spritesheet, x, y, width, height, scale=1) -> pygame.Surface:
    #base surface to blit onto
    cropped = pygame.Surface((width, height), pygame.SRCALPHA)
    #scale if needed and blit onto the base surface
    cropped.blit(spritesheet, (0, 0), (x, y, width, height))
    return cropped

def apply_rainbow(surface: pygame.Surface, offset=0., strength=0.666, bands=2., colour_offset=(0, 0, 0)) -> pygame.Surface:
    """Adds a rainbow effect to an image.

        Note that this returns a new surface and does not modify the original.

        Args:
            surface: The original image.
            offset: A value from 0 to 1 that applies a color shift to the rainbow. Changing this parameter
                    over time will create an animated looping effect. Values outside the interval [0, 1) will
                    act as though they're modulo 1.
            strength: A value from 0 to 1 that determines how strongly the rainbow's color should appear.
            bands: A value greater than 0 that determines how many color bands should be rendered (in other words,
                    how "thin" the rainbow should appear).
    """
    x = np.linspace(0, 1, surface.get_width())
    y = np.linspace(0, 1, surface.get_height())
    gradient = np.outer(x, y) * bands

    red_mult = np.sin(math.pi * 2 * (gradient + offset)) * 0.5 + 0.5
    green_mult = np.sin(math.pi * 2 * (gradient + offset + 0.25)) * 0.5 + 0.5
    blue_mult = np.sin(math.pi * 2 * (gradient + offset + 0.5)) * 0.5 + 0.5

    res = surface.copy()

    red_pixels = pygame.surfarray.pixels_red(res)
    red_pixels[:] = (red_pixels * (1 - strength) + red_pixels * red_mult * strength).astype(dtype='uint16')

    green_pixels = pygame.surfarray.pixels_green(res)
    green_pixels[:] = (green_pixels * (1 - strength) + green_pixels * green_mult * strength).astype(dtype='uint16')

    blue_pixels = pygame.surfarray.pixels_blue(res)
    blue_pixels[:] = (blue_pixels * (1 - strength) + blue_pixels * blue_mult * strength).astype(dtype='uint16')

    return res

    ##############################################################################################

#   FILE STUFF
def read_file(path):
    file = open(path)
    data = file.readlines()
    file.close()
    return data

def write_file(path, data):
    file = open(path)
    file.write(data + '\n')
    file.close()


def read_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def write_json(path, dict):
    with open(path, 'w') as json_file:
        json.dump(dict, json_file)

    ##############################################################################################
    
class QuitWindow(BaseException):
    def __init__(self):
        super().__init__()

    ##############################################################################################
        
class Timer:
    def __init__(self, duration: float, speed: float):
        self.t = 0
        self.end = duration
        self.speed = speed
        self.finished = False

        self.run = True

    #turn on/off
    def switch(self, flag:bool=None):
        if flag != None: 
            self.run = flag
        else: 
            self.run = not self.run

    def reset(self):
        self.t = 0
        self.finished = False

    def change_speed(self, speed: float|int):
        self.speed = speed

    def update(self):
        if self.run:
            if self.t < self.end:
                self.t += self.speed
            else:
                self.finished = True

    ##############################################################################################

#counting total number of lines written in the directory
import os                
def countLinesIn(directory):
    total_lines = 0
    uncommented_total = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    uncommented_total += len(list(filter(lambda l:l[0] != "#", filter(lambda l: len(l), map(lambda l: l.strip(), lines)))))
    print(f"Total Lines: {total_lines} | Uncommented: {uncommented_total}")