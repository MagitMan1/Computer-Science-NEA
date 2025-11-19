# Main UI handling script
import pygame
import pygame.time
import WorldGeneration.WorldGenerator as WorldGenerator

font = pygame.font.SysFont("Times", 30)
smallFont = pygame.font.SysFont("Times", 27)

# Loading text
loadingText = font.render(f"Generating world...", True, (255, 255, 255))

# Seed info
seedInfo = font.render(f"Seed: {WorldGenerator.seed}", True, (255, 255, 255))

# Creature colours
def listCreatureColours(currentCreatureName, currentCreatureColor):
    creatureInfo = font.render(currentCreatureName, True, currentCreatureColor)
    return creatureInfo

# Selected Creature Info
def drawCreatureInfoBox(surface, x, y, width, height, color):
    rect = pygame.draw.rect(surface, color, (x, y, width, height))
    return rect

def infoTitleText():
    title = smallFont.render("Selected Creature Info: ", True, (0, 0, 0))
    return title

def displayProperty(creatureProperty):
    property = smallFont.render(creatureProperty, True, (0, 0, 0))
    return property