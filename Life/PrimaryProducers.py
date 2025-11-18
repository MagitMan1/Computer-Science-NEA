# Grass handling script
import random
import WorldGeneration.WorldGenerator as worldGenerator
import pygame

# Basic setup
color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
RegenList = []
random.seed(worldGenerator.seed)
backgroundColor =(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
lastKilledCluster = None
clusters = {}

producerRegrowthTime = 10000
regrowingClusters = {}

def generateRandomPixels(surface, num_clusters):
    global clusters, clusterNumber
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
    global regrowingClusters
    if clusterId in clusters:
        killedPositions = clusters[clusterId].copy()

        for (x, y) in clusters[clusterId]:
            surface.set_at((x, y), backgroundColor)

        del clusters[clusterId]
        regrowingClusters[clusterId] = (pygame.time.get_ticks(), killedPositions)
        return clusterId

def regrowGrass(currentTime):
    global regrowingClusters
    clustersToRegrow = []

    for clusterId, (startTime, positions) in regrowingClusters.items():
        elapsed = currentTime - startTime

        if elapsed >= producerRegrowthTime:
            clustersToRegrow.append(clusterId)

    for clusterId in clustersToRegrow:
        startTime, positions = regrowingClusters[clusterId]
        surface = worldGenerator.worldSurface
        clusters[clusterId] = []

        for (x, y) in positions:
            surface.set_at((x, y), color)
            clusters[clusterId].append((x, y))

        del regrowingClusters[clusterId]