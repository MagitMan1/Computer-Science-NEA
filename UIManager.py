# Main UI handling script
import pygame
import pygame.time
import WorldGeneration.WorldGenerator as WorldGenerator

font = pygame.font.SysFont("Times", 30)

# Loading text
loadingText = font.render(f"Generating world...", True, (255, 255, 255))

# Seed info
seedInfo = font.render(f"Seed: {WorldGenerator.seed}", True, (255, 255, 255))

# Creature colours
def listCreatureColours(currentCreatureName, currentCreatureColor):
    creatureInfo = font.render(currentCreatureName, True, currentCreatureColor)
    return creatureInfo

# Selected Creature Info