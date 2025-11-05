# Creature handling script
import pygame
import WorldGeneration.WorldGenerator as worldGenerator
import Life.PrimaryProducers as producers
import random
import math

# Fix edge bug
# Grass regrowth
# Make eating system work on predators, if chase lasts over CHASE TIME attribute then revert to roaming, prey stops moving on predator eating state
# Ensure eating system is perfect
# Write up
# ------------------------------------
# Make vision customisable
# Make it so you can turn on and off vision visualisation
# Speed glitching via performance
# Energy system - 0 energy = death, decreases over time, increased by food. 1x multiplier, movement energy go down faster while moving
# Reproduction
# Extensive ai generated dictionary of creature names - Not generating the name in the moment
# Seed loading

# Basic setup
creatures = {}
surface = None
usedColors = []
world = None # Set in main

# User controled variables
creatureVisionVisualisation = True

def stateMachine(creature, currentTime):
    if creature["foodSeen"] and creature["atFood"] == False:
        currentState = "Chasing"
    else:
        currentState = "Roaming"

    if creature["atFood"]:
        currentState = "Eating"
        if "eatStartTime" not in creature:
            creature["eatStartTime"] = currentTime

        elapsed = (currentTime - creature["eatStartTime"])
        if elapsed >= creature["EatTime"]:
            clusterId = creature.get("foodCluster")
            producers.KillGrass(world, producers.clusters, clusterId)

            creature["atFood"] = False
            creature["foodSeen"] = False
            del creature["eatStartTime"]
            currentState = "Roaming"
    return currentState

def colorDecider():
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    if (color != worldGenerator.water and color != worldGenerator.base and color != producers.color and color not in usedColors):
        usedColors.append(color)
        return color

def tintImage(color):
    base_sprite = pygame.image.load("LifeSprite.png").convert_alpha()
    base_sprite = pygame.transform.scale(base_sprite, (22, 22))
    tinted = base_sprite.copy()
    arr = pygame.surfarray.pixels3d(tinted)
    arr[arr.sum(axis=2) == 0] = color
    del arr
    return tinted

def spawnRace(population, name, speed, trophicLevel, EatTime):
    global creatures
    if not(trophicLevel == "p" or trophicLevel == "s" or trophicLevel == "t"):
        raise TypeError("Incorrect trophic level specified, cannot create creature")

    width, height = surface.get_size()
    color = colorDecider()

    startId = max(creatures.keys(), default=-1) + 1

    for i in range(population):
        x = random.randint(0, width)
        y = random.randint(0, height)
        body = tintImage(color)

        creatures[startId + i] = {
            "Name": name,
            "Speed": speed,
            "body": body,
            "color": color,
            "TrophicLevel": trophicLevel,
            "x": x,
            "y": y,
            "vision": None, # Assigned in main
            "lookDirectionX": random.randint(-640, 640),
            "lookDirectionY": random.randint(-360, 360),
            "turnInterval": pygame.time.get_ticks() + (random.randint(1, 4) * 1000),
            "MoveInterval": pygame.time.get_ticks() + (random.randint(1, 3) * 1000),
            "ShouldStop": random.choice([True, False]),
            "currentState": None,
            "foodSeen": False,
            "foodLocation": None,
            "atFood": False,
            "EatTime": EatTime * 1000,
            "FoodCluster": None
        }
    return creatures

def creatureVision(spawnX, spawnY, fov, length, creature):
    global foodSeen

    fov = math.radians(fov)
    numRays = 5
    s = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

    pos = (spawnX, spawnY)

    dx = creature["lookDirectionX"]
    dy = creature["lookDirectionY"]

    angle = math.atan2(dy, dx)

    points = [pos]
    halfFov = fov / 2
    for i in range(numRays + 1):
        rayAngle = angle - halfFov + (fov * i / numRays)
        points.append((pos[0] + math.cos(rayAngle) * length, pos[1] + math.sin(rayAngle) * length))

    if creatureVisionVisualisation:
        pygame.draw.polygon(s, (0, 255, 0, 100), points)

    minX = max(0, int(min(p[0] for p in points)))
    maxX = min(surface.get_width(), int(max(p[0] for p in points)))
    minY = max(0, int(min(p[1] for p in points)))
    maxY = min(surface.get_height(), int(max(p[1] for p in points)))

    if not creature["foodSeen"]:
        creature["foodSeen"] = False
        creature["foodLocation"] = None

        # Food detection for primary consumers
        if creature["TrophicLevel"] == "p":
            for y in range(minY, maxY):
                for x in range(minX, maxX):
                    if s.get_at((x, y)):
                        if surface.get_at((x, y)) == producers.color:
                            creature["foodSeen"] = True
                            worldX = creature["x"] + (x - spawnX)
                            worldY = creature["y"] + (y - spawnY)

                            clusterId = findClusterAtPosition(worldX, worldY, tolerance=11)
                            if clusterId is not None:
                                creature["foodLocation"] = random.choice(producers.clusters[clusterId])
                                creature["foodCluster"] = clusterId
                            else:
                                creature["foodLocation"] = (worldX, worldY)
                                creature["foodCluster"] = None
                            break

        # Food detection for Secondary consumers
        elif creature["TrophicLevel"] == "s":
            detectPrey(creature, preyLevels=["p"], spawnX=spawnX, spawnY=spawnY, s=s, minX=minX, maxX=maxX, minY=minY,
                       maxY=maxY, creatures=creatures)

        # Food detection for Tertiary consumers
        elif creature["TrophicLevel"] == "t":
            detectPrey(creature, preyLevels=["p", "s"], spawnX=spawnX, spawnY=spawnY, s=s, minX=minX, maxX=maxX, minY=minY,
                       maxY=maxY, creatures=creatures)

    surface.blit(s, (0, 0))

def detectPrey(creature, preyLevels, spawnX, spawnY, s, minX, maxX, minY, maxY, creatures):
    for otherCreature in creatures.values():
        if otherCreature is creature:
            continue

        if otherCreature["TrophicLevel"] not in preyLevels:
            continue

        camOffsetX = spawnX - creature["x"] - creature["body"].get_width() // 2
        camOffsetY = spawnY - creature["y"] - creature["body"].get_height() // 2

        otherScreenX = camOffsetX + otherCreature["x"] + otherCreature["body"].get_width() // 2
        otherScreenY = camOffsetY + otherCreature["y"] + otherCreature["body"].get_height() // 2

        if minX <= otherScreenX <= maxX and minY <= otherScreenY <= maxY:
            try:
                if s.get_at((int(otherScreenX), int(otherScreenY))).a > 0:
                    creature["foodSeen"] = True
                    break
            except IndexError:
                print("Error")
                pass

def turnHandler(creature, currentTime):
    if creature["currentState"] == "Roaming":
        if currentTime >= creature["turnInterval"]:
            creature["lookDirectionX"] = random.randint(-640, 640)
            creature["lookDirectionY"] = random.randint(-360, 360)
            creature["turnInterval"] = currentTime + (random.randint(1, 4) * 1000)

    elif creature["currentState"] == "Chasing" and creature.get("foodLocation"):
        foodX, foodY = creature["foodLocation"]
        dx = foodX - creature["x"]
        dy = foodY - creature["y"]

        # normalize
        mag = math.sqrt(dx ** 2 + dy ** 2)
        if mag > 0:
            creature["lookDirectionX"] = dx / mag
            creature["lookDirectionY"] = dy / mag

def movementHandler(creature, currentTime, worldSurface):
    # Clamp to world boundaries (both min and max)
    creature["x"] = max(0, min(creature["x"], worldSurface.get_width() - creature["body"].get_width()))
    creature["y"] = max(0, min(creature["y"], worldSurface.get_height() - creature["body"].get_height()))

    dx = creature["lookDirectionX"]
    dy = creature["lookDirectionY"]

    if creature["currentState"] == "Roaming":
        if currentTime >= creature["MoveInterval"]:
            creature["ShouldStop"] = random.choice([True, False])
            creature["MoveInterval"] = pygame.time.get_ticks() + (random.randint(1, 3) * 1000)

        if not creature["ShouldStop"]:
            mag = math.sqrt(dx ** 2 + dy ** 2)
            if mag > 0:
                move(dx, dy, mag, creature)
    elif creature["currentState"] == "Chasing":
        mag = math.sqrt(dx ** 2 + dy ** 2)
        if mag > 0:
            move(dx, dy, mag, creature)
        tolerance = 1
        if abs(creature["x"] - creature["foodLocation"][0]) <= tolerance and abs(creature["y"] - creature["foodLocation"][1]) <= tolerance:
            creature["atFood"] = True

def move(dx, dy, mag, creature):
    normalized_dx = (dx / mag) * creature["Speed"]
    normalized_dy = (dy / mag) * creature["Speed"]

    creature["x"] += normalized_dx
    creature["y"] += normalized_dy


def findClusterAtPosition(x, y, tolerance):
    for clusterId, pixels in producers.clusters.items():
        for px, py in pixels:
            if abs(px - int(x)) <= tolerance and abs(py - int(y)) <= tolerance:
                return clusterId
    return None