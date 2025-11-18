# World gen
import pygame
import random
from perlin_noise import PerlinNoise

pygame.init()

# User settings:
Octaves = 2
Scale = 7
worldSize = 720, 720

# Basic Setup
seed = random.randint(0, 999999)

# Randomise colours using same word seed
random.seed(seed + 1)
water = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
random.seed(seed)
base = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

worldSurface = pygame.Surface(worldSize)

def PerlinNoiseWorldGenerator(seed): # Simply generates and colours the world
    global worldSurface
    print("Generating World...")
    worldNoise = PerlinNoise(seed=seed, octaves=Octaves)

    for y in range(worldSize[1]):
        for x in range(worldSize[0]):
            nx = x / worldSize[0] * Scale
            ny = y / worldSize[1] * Scale
            worldValue = (worldNoise([nx, ny]) + 1) / 2
            if worldValue < 0.3:
                color = water
            else:
                color = base
            worldSurface.set_at((x, y), color)

    print("World generated")
    return worldSurface