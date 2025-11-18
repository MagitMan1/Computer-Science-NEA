# Creature handling script
import pygame
import WorldGeneration.WorldGenerator as worldGenerator
import Life.PrimaryProducers as producers
import random
import math

# Energy system - 0 energy = death, decreases over time, increased by food. 1x multiplier, movement energy go down faster while moving

# ------------------------------------
# Reproduction
# Speed glitching via performance - delta time?, general optimisation
# Extensive AI generated dictionary of creature names - Not generating the name in the moment
# MAJOR CODE CLEANUP
# Seed loading
# creature avoids water

# Basic setup
creatures = {}
surface = None
usedColors = []
world = None # Set in main

def stateMachine(creature, currentTime, creatures):
    if creature["currentState"] == "Frozen":
        return "Frozen"

    if creature["currentState"] == "Evading":
        return "Evading"

    if creature["foodSeen"] and creature["atFood"] == False:
        currentState = "Chasing"
    else:
        currentState = "Roaming"

    if creature["atFood"]:
        currentState = "Eating"
        creature["creatureVisionVisualisation"] = False
        if "eatStartTime" not in creature:
            creature["eatStartTime"] = currentTime

        elapsed = (currentTime - creature["eatStartTime"])
        if elapsed >= creature["EatTime"]:
            if creature["TrophicLevel"] == "p":
                clusterId = creature.get("foodCluster")
                producers.KillGrass(world, producers.clusters, clusterId)
            elif creature["TrophicLevel"] in ["s", "t"]:
                preyId = creature.get("preyId")
                if preyId is not None and preyId in creatures:
                    del creatures[preyId]
                    del creature["preyId"]

            creature["atFood"] = False
            creature["foodSeen"] = False
            del creature["eatStartTime"]
            creature["creatureVisionVisualisation"] = True
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

def spawnRace(population, name, speed, trophicLevel, EatTime, EvadeTime, FOV, viewDistance):
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
            "FoodCluster": None,
            "creatureVisionVisualisation": True,
            "predatorLocation": None,
            "evadeTime": EvadeTime * 1000 if trophicLevel in ["p", "s"] else None,
            "FOV": FOV,
            "viewDistance": viewDistance
        }
    return creatures

def creatureVision(spawnX, spawnY, creature):
    global foodSeen
    fov = creature["FOV"]
    length = creature["viewDistance"]

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

    if creature["creatureVisionVisualisation"]:
        background = worldGenerator.base
        pygame.draw.polygon(s, (255-background[0], 255-background[1], 255-background[2], 100), points)

    minX = max(0, int(min(p[0] for p in points)))
    maxX = min(surface.get_width(), int(max(p[0] for p in points)))
    minY = max(0, int(min(p[1] for p in points)))
    maxY = min(surface.get_height(), int(max(p[1] for p in points)))

    for otherCreature in creatures.values():
        if otherCreature is creature:
            continue

        isPredator = False
        if creature["TrophicLevel"] == "p" and otherCreature["TrophicLevel"] in ["s", "t"]:
            isPredator = True
        elif creature["TrophicLevel"] == "s" and otherCreature["TrophicLevel"] == "t":
            isPredator = True

        if isPredator:
            camOffsetX = spawnX - creature["x"] - creature["body"].get_width() // 2
            camOffsetY = spawnY - creature["y"] - creature["body"].get_height() // 2

            otherScreenX = camOffsetX + otherCreature["x"] + otherCreature["body"].get_width() // 2
            otherScreenY = camOffsetY + otherCreature["y"] + otherCreature["body"].get_height() // 2

            if minX <= otherScreenX <= maxX and minY <= otherScreenY <= maxY:
                try:
                    if s.get_at((int(otherScreenX), int(otherScreenY))).a > 0:
                        creature["currentState"] = "Evading"
                        creature["predatorLocation"] = (otherCreature["x"], otherCreature["y"])
                        break
                except IndexError:
                    pass

    if not creature["foodSeen"] and not creature["currentState"] == "Evading":
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
                    creature["foodLocation"] = (otherCreature["x"], otherCreature["y"])

                    for creatureId, creatureObj in creatures.items():
                        if creatureObj is otherCreature:
                            creature["preyId"] = creatureId
                            break
                    break
            except IndexError:
                print("Error")
                pass

def turnHandler(creature, currentTime):
    if not creature["currentState"] == "Frozen":
        if creature["currentState"] == "Roaming":
            if currentTime >= creature["turnInterval"]:
                creature["lookDirectionX"] = random.randint(-640, 640)
                creature["lookDirectionY"] = random.randint(-360, 360)
                creature["turnInterval"] = currentTime + (random.randint(1, 4) * 1000)

        elif creature["currentState"] == "Evading" and creature.get("predatorLocation"):
            predatorX, predatorY = creature["predatorLocation"]
            dx = creature["x"] - predatorX
            dy = creature["y"] - predatorY

            mag = math.sqrt(dx ** 2 + dy ** 2)
            if mag > 0:
                creature["lookDirectionX"] = dx / mag
                creature["lookDirectionY"] = dy / mag

        elif creature["currentState"] == "Chasing" and creature.get("foodLocation"):
            if creature.get("preyId") is not None and creature["preyId"] in creatures:
                prey = creatures[creature["preyId"]]
                creature["foodLocation"] = (prey["x"], prey["y"])

            foodX, foodY = creature["foodLocation"]
            dx = foodX - creature["x"]
            dy = foodY - creature["y"]

            mag = math.sqrt(dx ** 2 + dy ** 2)
            if mag > 0:
                creature["lookDirectionX"] = dx / mag
                creature["lookDirectionY"] = dy / mag

def movementHandler(creature, currentTime, worldSurface):
    # Clamp to world boundaries (both min and max)
    creature["x"] = max(0, min(creature["x"], worldSurface.get_width() - (creature["body"].get_width()/3)))
    creature["y"] = max(0, min(creature["y"], worldSurface.get_height() - (creature["body"].get_height()/3)))

    if not creature["currentState"] == "Frozen":
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

        elif creature["currentState"] == "Evading":
            mag = math.sqrt(dx ** 2 + dy ** 2)
            if mag > 0:
                move(dx, dy, mag, creature)

            if creature.get("predatorLocation"):
                if "evadeStartTime" not in creature:
                    creature["evadeStartTime"] = currentTime
                elapsed = (currentTime - creature["evadeStartTime"])
                if elapsed >= creature["evadeTime"]:
                    del creature["evadeStartTime"]
                    creature["predatorSeen"] = False
                    creature["predatorLocation"] = None
                    creature["currentState"] = "Roaming"

        elif creature["currentState"] == "Chasing":
            mag = math.sqrt(dx ** 2 + dy ** 2)
            if mag > 0:
                move(dx, dy, mag, creature)
            tolerance = 1
            if abs(creature["x"] - creature["foodLocation"][0]) <= tolerance and abs(creature["y"] - creature["foodLocation"][1]) <= tolerance:
                creature["atFood"] = True
                if creature.get("preyId") is not None and creature["preyId"] in creatures:
                    prey = creatures[creature["preyId"]]
                    prey["currentState"] = "Frozen"
                    prey["creatureVisionVisualisation"] = False

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