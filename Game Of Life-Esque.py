import os, win32api, random, noise, math, time, pyautogui
import pygame as pg
import numpy as np

# Initialize

os.environ['SDL_VIDEO_CENTERED'] = '1'

pg.display.init()
pg.font.init()

display_x = pyautogui.size()[0]
display_y = pyautogui.size()[1]

gameDisplay = pg.display.set_mode((display_x, display_y), pg.NOFRAME) 

surface = pg.Surface(gameDisplay.get_size())

# Colors

black = (0, 0, 0, 225) 
white = (255, 255, 255, 255)

# Time

clock = pg.time.Clock()

t = pg.time.get_ticks() 

last_t = t

# Misc

displayInfo = False

infoText1 = None

mouseRect = pg.Rect(pg.mouse.get_pos()[0] + 2.5, pg.mouse.get_pos()[1] + 2.5, 5, 5)

keys = {}

zoom = 1

debug = False

entityArr = np.array([])

entityArr_byType = {"food":np.array([], dtype="object"), "tad":np.array([], dtype="object")}

mouseDown = False

running = True

gameSpeed = 60

font1 = pg.font.SysFont("Arial", 32)

font2 = pg.font.SysFont("Arial", 22)

# Utility Funcs

def Constrain(val, val_min, val_max, cons_min=None, cons_max=None):
    "Constrains a value between a minimum and maximum, if two more arguments are given it constrains the value between a minimum and maximum range of values with a different impulse. "
    if cons_min != None and cons_max == None:
        raise TypeError("Constrain() missing 1 required positional argument: 'cons_max'")

    if cons_min != None and cons_max != None:
        if val >= val_max:
            return cons_max

        if val <= val_min:
            return cons_min
    elif cons_min == None and cons_max == None:
        if val >= val_max:
            return val_max

        if val <= val_min:
            return val_min

    if cons_min != None and cons_max != None:
        val = val - val_min

        valDiff = val_max - val_min

        consDiff = cons_max - cons_min

        valPer = val / valDiff

        result = consDiff * valPer

        result = cons_min + result

        return result

    else:
        if val > val_max:
            val = val_max

        if val < val_min:
            val = val_min

        return val

def RandFunc(chance, func):
    "Calls a function at a given chance. Returns a bool stating whether the function has been passed or not"
    if random.uniform(1, 2) - 1 > 1 - chance:
        func()

        return True

    return False

def Mag(x): 
    "Returns the magnitude of any iterable."
    return math.sqrt(sum(i**2 for i in x))

# Define Functions

def Controls():
    global keys
    global running
    global mouseDown
    global mouseRect
    global selectedTad
    global displayInfo

    for event in pg.event.get():
        
        if event.type == pg.QUIT:
            pg.quit()
            running = False

        if not running:
            break

        # Controls

        if event.type == pg.KEYDOWN:
            keys[event.key] = True

            if keys.get(pg.K_ESCAPE):
                pg.quit()
                running = False
                break

        if event.type == pg.KEYUP:
            keys[event.key] = False

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouseDown = True
                
                mouseRect = pg.Rect(pg.mouse.get_pos()[0] - 5 + Camera.x, pg.mouse.get_pos()[1] - 5 + Camera.y, 10, 10)

                for tad in entityArr_byType["tad"]:
                    if tad.rect != None:
                        if mouseRect.colliderect(tad.rect):
                            selectedTad = tad

                            displayInfo = True

                            break
                else:
                    displayInfo = False

                if keys.get(pg.K_RSHIFT) or keys.get(pg.K_LSHIFT):
                    Tadpole([pg.mouse.get_pos()[0] + Camera.x, pg.mouse.get_pos()[1] + Camera.y], 12)

            if event.button == 3:
                if keys.get(pg.K_RSHIFT) or keys.get(pg.K_LSHIFT):
                    entityArr, Food([pg.mouse.get_pos()[0] + Camera.x, pg.mouse.get_pos()[1] + Camera.y], random.randint(10, 1000))

        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                mouseDown = False

            if event.button == 3:
                pass

        if event.type == pg.MOUSEMOTION:
            pass

    # Control Actions

    if keys.get(pg.K_RSHIFT) or keys.get(pg.K_LSHIFT):
        if keys.get(pg.K_w):
            Camera.y -= Camera.speed * 3

        if keys.get(pg.K_a):
            Camera.x -= Camera.speed * 3

        if keys.get(pg.K_s):
            Camera.y += Camera.speed * 3

        if keys.get(pg.K_d):
            Camera.x += Camera.speed * 3

    else:
        if keys.get(pg.K_w):
            Camera.y -= Camera.speed

        if keys.get(pg.K_a):
            Camera.x -= Camera.speed

        if keys.get(pg.K_s):
            Camera.y += Camera.speed

        if keys.get(pg.K_d):
            Camera.x += Camera.speed

# Define Classes

class Tadpole():
    def __init__(self, pos, radius):
        global entityArr
        global entityArr_byType

        self.x = pos[0]
        self.y = pos[1]
        self.target = None
        self.rect = None
        self.moving = False
        self.speed = random.uniform(0.5, 3.5)
        self.searchCoolDownMax = 50
        self.searchCoolDown = self.searchCoolDownMax
        self.nearestFood = min(entityArr_byType["food"], key=lambda e: np.linalg.norm((self.x - e.x, self.y - e.y)))
        self.sightDistance = random.randint(300, 700)
        self.viewingRect = None
        self.splitEnergy = random.randint(1000, 2000)
        self.energyLevel = self.splitEnergy
        self.energyLevelMax = 5000
        self.energyDrainRate = random.uniform(0.5, 2)
        self.eatingFood = False
        self.T_angle = 0
        self.radius = radius
        self.findFoodChance = random.uniform(0.1, 0.7)
        self.color = (50, 150, 89)
        self.NOISE_octaves = 1
        self.NOISE_persistence = 1000000
        self.NOISE_lacunarity = 10
        self.NOISE_scale = 25
        self.NOISE_x1 = random.randint(1, 10000)
        self.NOISE_y1 = random.randint(1, 10000)
        self.NOISE_z1 = random.randint(1, 10000)
        self.NOISE_x2 = random.randint(1, 10000)
        self.NOISE_y2 = random.randint(1, 10000)
        self.NOISE_z2 = random.randint(1, 10000)

        self.noiseValue_x = 0
        self.noiseValue_y = 0

        entityArr = np.append(entityArr, self)
        entityArr_byType["tad"] = np.append(entityArr_byType["tad"], self)

    def EatFood(self, nourishment):
        self.energyLevel += nourishment

    def SetTarget(self, pos):
        if pos != None:
            pos[0] = Constrain(pos[0], -Map.size[0] + e.radius, Map.size[0] - e.radius)
            pos[1] = Constrain(pos[1], -Map.size[1] + e.radius, Map.size[1] - e.radius)
            self.target = pos
        else:
            self.target = pos
    
    def Decease(self):
        global entityArr
        global entityArr_byType

        entityArr = np.delete(entityArr, np.where(entityArr == self))
        entityArr_byType["food"] = np.delete(entityArr_byType["food"], np.where(entityArr_byType["food"] == self))

    def TrySplit(self):
        if self.energyLevel >= self.energyLevelMax:
            self.energyLevel = self.splitEnergy

            Tadpole([self.x + random.randint(-self.radius, self.radius), self.y + random.randint(-self.radius, self.radius)], 12)
            
    def Move(self):
        if self.target != None:
            self.moving = True
            self.diff = (self.target[0] - self.x, self.target[1] - self.y)
            self.distToTarget = Mag(self.diff)
            
            if self.distToTarget < self.radius:
                self.target = None
                self.eatingFood = False

                self.noiseValue_x = noise.snoise3(
                            self.NOISE_x1 / self.NOISE_scale, 
                            self.NOISE_y1 / self.NOISE_scale, 
                            self.NOISE_z1, 
                            octaves=self.NOISE_octaves, 
                            persistence=self.NOISE_persistence, 
                            lacunarity=self.NOISE_lacunarity)

                self.noiseValue_y = noise.snoise3(
                            self.NOISE_x2 / self.NOISE_scale, 
                            self.NOISE_y2 / self.NOISE_scale, 
                            self.NOISE_z2, 
                            octaves=self.NOISE_octaves, 
                            persistence=self.NOISE_persistence, 
                            lacunarity=self.NOISE_lacunarity)

                self.NOISE_z1 += 0.3

                self.NOISE_z2 += 0.3

            else:
                try:
                    self.T_angle = math.degrees(math.acos(self.diff[0] / self.distToTarget))

                    if self.diff[1] > 0:
                        self.T_angle = 360 - self.T_angle
                        
                except ZeroDivisionError:
                    self.T_angle = 0

            self.x += math.cos(math.radians(-self.T_angle)) * self.speed
            self.y += math.sin(math.radians(-self.T_angle)) * self.speed

        else:
            self.moving = False

            if self.searchCoolDown <= 0:
                self.SearchFood()

            RandFunc(0.05, lambda: self.SetTarget([self.x + self.noiseValue_x * 200, self.y + self.noiseValue_y * 200]))

    def SearchFood(self):
        self.searchCoolDown = self.searchCoolDownMax

        self.nearestFood = min(entityArr_byType["food"], key=lambda e: np.linalg.norm((self.x - e.x, self.y - e.y)))
        
        self.Wander()

    def CollisionCheck(self):
        global entityArr
        global entityArr_byType

        if self.nearestFood != None:
            if self.nearestFood.rect != None and self.rect != None:
                if self.rect.colliderect(self.nearestFood.rect):
                    self.EatFood(self.nearestFood.nourishment)
                    self.TrySplit()
                    entityArr = np.delete(entityArr, np.where(entityArr == self.nearestFood))
                    entityArr_byType["food"] = np.delete(entityArr_byType["food"], np.where(entityArr_byType["food"] == self.nearestFood))
                    self.SetTarget(None)
                    self.nearestFood = None

        self.x = Constrain(self.x, -Map.size[0] + self.radius, Map.size[0] - self.radius)
        self.y = Constrain(self.y, -Map.size[1] + self.radius, Map.size[1] - self.radius)

    def Wander(self):
        if self.nearestFood != None:
            if RandFunc(self.findFoodChance, lambda: self.SetTarget([self.nearestFood.x, self.nearestFood.y])):
                self.eatingFood = True

    def Update(self, dt):
        self.Move()

        self.rect = pg.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

        self.viewingRect = pg.Rect(self.x - self.sightDistance, self.y - self.sightDistance, self.sightDistance * 2, self.sightDistance * 2)

        self.CollisionCheck()

        if self.energyLevel > self.energyLevelMax:
            self.energyLevel = self.energyLevelMax

        self.energyLevel -= self.energyDrainRate

        self.searchCoolDown -= 1

        if self.energyLevel <= 0:
            self.Decease()

    def Draw(self):
        if (self.x > Camera.x - self.radius and self.x < Camera.x + display_x + self.radius) and (self.y > Camera.y - self.radius and self.y < Camera.y + display_y + self.radius):
            self.color = (255 - Constrain(self.energyLevel, 0, self.energyLevelMax, 0, 255), Constrain(self.energyLevel, 0, self.energyLevelMax, 0, 255) / 15 + 150, Constrain(self.energyLevel, 0, self.energyLevelMax, 0, 255) / 25 + 89)

            pg.draw.circle(surface, self.color, (round(self.x) - Camera.x, round(self.y) - Camera.y), self.radius)

            if debug:
                if self.target != None:
                    # pg.draw.circle(surface, white, (round(self.target[0]), round(self.target[1])), 4)

                    pg.draw.rect(surface, white, (self.rect.x - Camera.x, self.rect.y - Camera.y, self.rect.width, self.rect.height), 1)

class Food():
    def __init__(self, pos, nourishment):
        global entityArr
        global entityArr_byType

        self.x = pos[0]
        self.y = pos[1]
        self.nourishment = nourishment
        self.rect = None
        self.radius = round(Constrain(self.nourishment ** 0.85, 10, 1000, 3, 9.5))

        entityArr = np.append(entityArr, self)
        entityArr_byType["food"] = np.append(entityArr_byType["food"], self)

    def Update(self, dt):
        self.radius = round(Constrain(self.nourishment ** 0.85, 10, 1000, 3, 9.5))

        self.rect = pg.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def Draw(self):
        if (self.x > Camera.x - self.radius and self.x < Camera.x + display_x) and (self.y > Camera.y - self.radius and self.y < Camera.y + display_y):
            pg.draw.circle(surface, (170, 100, 43), (round(self.x) - Camera.x, round(self.y) - Camera.y), round(Constrain(self.nourishment ** 0.85, 10, 1000, 3, 9.5)))

            if debug:
                if self.rect != None:
                    pg.draw.rect(surface, white, (self.rect.x - Camera.x, self.rect.y - Camera.y, self.rect.width, self.rect.height), 1)

    @staticmethod
    def SpawnFood():
        for i in range(1):
            Food([random.randint(-Map.size[0], Map.size[0]), random.randint(-Map.size[1], Map.size[1])], random.randint(10, 1000))

class Camera():
    x = 0
    y = 0
    speed = 10
    
    @classmethod
    def Update(cls):
        cls.x = Constrain(cls.x, -Map.size[0], Map.size[0] - display_x)
        cls.y = Constrain(cls.y, -Map.size[1], Map.size[1] - display_y)

class Map():
    size = (display_x * 3, display_y * 3)

# Object Assignment

for i in range(500):
    Food([random.randint(-Map.size[0], Map.size[0]), random.randint(-Map.size[1], Map.size[1])], random.randint(10, 1000))

for i in range(5):
    Tadpole([random.randint(-Map.size[0], Map.size[0]), random.randint(-Map.size[1], Map.size[1])], 12)

# Main Loop

while running:

    t = pg.time.get_ticks()

    deltaTime = (t - last_t) / 1000.0

    Controls()

    # Exit Without An Error Message

    if not running:
        break

    # Do The Actual Game

    Camera.Update()

    if displayInfo:
        pg.draw.rect(surface, (255, 0, 0), (selectedTad.rect.x - Camera.x, selectedTad.rect.y - Camera.y, selectedTad.rect.width, selectedTad.rect.height), 1)

    for e in entityArr:
        e.Draw()
        e.Update(deltaTime)

    if displayInfo:
        infoText1 = font2.render(f"Energy: {round(selectedTad.energyLevel)}", True, white)
        infoText2 = font2.render(f"Max Energy: {round(selectedTad.energyLevelMax)}", True, white)
        infoText3 = font2.render(f"Split Energy: {round(selectedTad.splitEnergy)}", True, white)
        infoText4 = font2.render(f"Energy Drain Rate: {round(selectedTad.energyDrainRate, 3)}", True, white)
        infoText5 = font2.render(f"Find Food Chance: {round(selectedTad.findFoodChance, 3)}", True, white)
        infoText6 = font2.render(f"Sight Distance: {round(selectedTad.sightDistance)}", True, white)
        infoText7 = font2.render(f"Speed: {round(selectedTad.speed, 3)}", True, white)

        for i in range(7):
            surface.blit(globals()[f"infoText{i + 1}"], (40, display_y - 30 * i - 50))

    RandFunc(0.037, Food.SpawnFood)

    # This Always Goes Last

    fps = font1.render(str(int(clock.get_fps())), True, white)
    surface.blit(fps, (25, 25))

    gameDisplay.blit(surface, (0, 0))

    pg.display.flip()

    surface.fill(black)

    clock.tick(gameSpeed)

    last_t = t
