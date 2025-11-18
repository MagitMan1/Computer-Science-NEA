# Main file for Evolution Simulator

import pygame
import WorldGeneration.WorldGenerator as WorldGenerator
import Life.PrimaryProducers
import UIManager as UI
import Life.Creature as creatureBase

pygame.init()
clock = pygame.time.Clock()

# User settings:
windowedResolution = 1280, 720
backgroundColor = (70, 70, 70)
camSpeed = 2
devMode = True

# Basic Setup
running = True
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
windowName = pygame.display.set_caption("Evolution Simulator (NEA)")
fullscreen = True
camX, camY = 0, 0

# Loading text
screen.blit(UI.loadingText, ((screen.get_width() // 2)- (UI.loadingText.get_width() // 2), screen.get_height() // 2))
pygame.display.flip()

# Generate world
world = WorldGenerator.PerlinNoiseWorldGenerator(WorldGenerator.seed)

# Life setup ----------------------------------------------
creatureBase.surface = screen
# P producer
grass = Life.PrimaryProducers.generateRandomPixels(world, 65)

# Creatures
pConsumers = creatureBase.spawnRace(3, "Race1", 0.75, "p", 2, 5, 30, 115)
#sConsumers = creatureBase.spawnRace(5, "Race2", 0.75, "s", 3, 3, 50, 85)
#tConsumers = creatureBase.spawnRace(5, "Race3", 0.75, "t", 6, None, 75, 40)

creatureBase.world = world
# ---------------------------------------------------------

def centreCamera():
    global camX, camY
    if not fullscreen:
        camX = (windowedResolution[0] - world.get_width()) // 2
        camY = (windowedResolution[1] - world.get_height()) // 2
    else:
        camX = (screen.get_width() - world.get_width()) // 2
        camY = (screen.get_height() - world.get_height()) // 2
    print("Camera position reset")

# setup camera
centreCamera()

while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Fullscreen control
            if event.key == pygame.K_p:
                if not fullscreen:
                    fullscreen = not fullscreen
                    print("Entered fullscreen")
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    fullscreen = not fullscreen
                    print("Exited fullscreen")
                    screen = pygame.display.set_mode((windowedResolution), pygame.RESIZABLE)
            # Re centre camera
            if event.key == pygame.K_h:
                centreCamera()

    # Keybinds
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        camY += camSpeed
    if keys[pygame.K_s]:
        camY -= camSpeed
    if keys[pygame.K_a]:
        camX += camSpeed
    if keys[pygame.K_d]:
        camX -= camSpeed

    screen.fill(backgroundColor)

    currentTime = pygame.time.get_ticks()

    # Visible item blits
    screen.blit(world, (camX, camY))
    screen.blit(UI.seedInfo, (camX - 170, camY))

    # Creature setup and initialisation
    creatureInfoYPosition = 35
    drawnSpecies = set()
    for creature in list(creatureBase.creatures.values()):
        # Variables to setup
        creature["currentState"] = creatureBase.stateMachine(creature, currentTime, creatureBase.creatures)
        creature["vision"] = creatureBase.creatureVision(
            camX + creature["x"] + creature["body"].get_width() // 2,
            camY + creature["y"] + creature["body"].get_height() // 2,
            creature
        )
        # Functions to call
        creatureBase.turnHandler(creature, currentTime)
        creatureBase.movementHandler(creature, currentTime, world)
        # Blits
        screen.blit(creature["body"], (camX + creature["x"], camY + creature["y"]))
        # Creature info text
        if creature["Name"] not in drawnSpecies:
            screen.blit(
                UI.listCreatureColours(creature["Name"], creature["color"]),
                (camX - 80, camY + creatureInfoYPosition)
            )
            creatureInfoYPosition += 30
            drawnSpecies.add(creature["Name"])

    # Regrowing grass
    Life.PrimaryProducers.regrowGrass(currentTime)

    # Final display flip
    pygame.display.flip()

pygame.quit()