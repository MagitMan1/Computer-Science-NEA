# Grass handling script
import random
import WorldGeneration.WorldGenerator as worldGenerator
import pygame

# Basic setup
color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
RegenList = []
random.seed(worldGenerator.seed)
backgroundColor =(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
producerRegrowthTime = 2
REGROWEVENT = pygame.USEREVENT + 1
lastKilledCluster = None
clusters = {}

def generateRandomPixels(surface, num_clusters):
    global clusters
    width, height = surface.get_size()
    size = 7

    for clusterId in range(num_clusters):
        startX = random.randint(0, width - size)
        startY = random.randint(0, height - size)

        while checkColorAtPosition(startX, startY) == worldGenerator.water:
            startX = random.randint(0, width - size)
            startY = random.randint(0, width - size)

        clusters[clusterId] = []

        for dy in range(size):
            for dx in range(size):
                x = startX + dx
                y = startY + dy
                surface.set_at((x, y), color)

                clusters[clusterId].append((x, y))
    return clusters

def checkColorAtPosition(x, y):
    colorAtPosition = worldGenerator.worldSurface.get_at((x, y))
    return colorAtPosition

def KillGrass(surface, clusters, clusterId):
    global lastKilledCluster
    if clusterId in clusters:
        for (x, y) in clusters[clusterId]:
            surface.set_at((x, y), backgroundColor)
        pygame.display.update()
        pygame.time.set_timer(REGROWEVENT, producerRegrowthTime * 1000, True)
        lastKilledCluster = clusterId
        return clusterId