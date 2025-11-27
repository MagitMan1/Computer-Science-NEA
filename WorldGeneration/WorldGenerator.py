import numpy as np
import pygame
from opensimplex import OpenSimplex
import random

# Basic Setup
seed = random.randint(0, 999999)
worldSize = 720
Scale = 10

# Initialize Pygame
pygame.init()
worldSurface = pygame.Surface((worldSize, worldSize))

# Color setup
water = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
base = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
while water == base:
    water = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def generateNoiseGrid(width, height, xCoords, yCoords, noiseGen):
    noiseValues = np.zeros((height, width))

    for y in range(height):
        ny = yCoords[y]
        for x in range(width):
            noiseValues[y, x] = noiseGen.noise2(xCoords[x], ny)

    return noiseValues

def PerlinNoiseWorldGenerator():
    global worldSurface
    print("Generating World...")

    noiseGen = OpenSimplex(seed=seed)

    width, height = worldSize, worldSize
    scaleX = Scale / width
    scaleY = Scale / height

    xCoords = np.arange(width) * scaleX
    yCoords = np.arange(height) * scaleY

    noiseValues = generateNoiseGrid(width, height, xCoords, yCoords, noiseGen)

    waterMask = noiseValues < -0.4
    rgbArray = np.zeros((height, width, 3), dtype=np.uint8)
    rgbArray[waterMask] = water
    rgbArray[~waterMask] = base

    pygame.surfarray.blit_array(worldSurface, rgbArray)
    print("World Generated")
    return worldSurface