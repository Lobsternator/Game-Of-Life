import os
import sys

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(basedir, "Data\\Scripts\\"))

from ustu import *
import pygame
from pygame import *
from pygame import gfxdraw
import time as pytime
import random
import getpass
import urllib
from urllib.request import urlopen as uReq
import re
import subprocess
from operator import attrgetter as attrget
import json
import win32api
from bs4 import BeautifulSoup as soup
from PIL import Image, ImageDraw
import math
import pyautogui
from itertools import product
import noise
import numpy as np
import threading
import queue

# Initialize

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.init()
pygame.font.init()

display_x = 1280
display_y = 720

gameDisplay = pygame.display.set_mode((display_x, display_y)) 

surface = pygame.Surface(gameDisplay.get_size())

# Colors

black = (0, 0, 0, 225) 
white = (255, 255, 255, 255)

# Time

clock = pygame.time.Clock()

t = pygame.time.get_ticks() 

last_t = t

# Misc

q = queue.Queue()

keys = {}

debug = False

keyList = [K_w, K_a, K_s, K_d, K_r, K_SPACE, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_ESCAPE]

entityArr = np.array([])

mouseDown = False

running = True

gameSpeed = float(getattr(win32api.EnumDisplaySettings(win32api.EnumDisplayDevices().DeviceName, -1), 'DisplayFrequency'))

font = pygame.font.SysFont("Arial", 30)

# Define Classes

class AlignmentError(error):
    pass

class Font():
    "Font()"
    def __init__(self, fontName, size, color):
        self.fontName = "Times"
        self.size = size
        self.sizeLast = None
        self.sizeListLast = [self.sizeLast]
        self.antialias = True
        self.color = (255, 255, 255, 255)
        self.imgList = [None]
        self.dimList = [[0, 0]]
        self.pos = [0, 0]
        self.alignment = "center"
        self.lineList = ["cock"]
        self.lineListLast = [""]
        self.caretDuration = 0
        self.maxCaretDuration = 0.75
        self.font = pygame.font.SysFont(self.fontName, self.size)

        for i, line in enumerate(self.lineList):

            if len(self.imgList) < len(self.lineList):
                self.imgList.append(None)

            self.imgList[i] = self.font.render(line, self.antialias, self.color)

            width, height = self.imgList[i].get_rect().size

            if len(self.dimList) < len(self.lineList):
                self.dimList.append(None)

            self.dimList[i] = [width, height]

            if len(self.lineListLast) < len(self.lineList):
                self.lineListLast.append(None)

            self.lineListLast[i] = self.lineList[i]

            if len(self.sizeListLast) < len(self.lineList):
                self.sizeListLast.append(None)

            self.sizeListLast[i] = self.size

    def Render(self, pos=(0, 0), drawText=True, drawCaret=True):
        for i, img in enumerate(self.imgList):
            try:
                if self.lineList[i] != self.lineListLast[i]:
                    self.imgList[i] = self.font.render(self.lineList[i], self.antialias, self.color)

            except IndexError:
                self.imgList[i] = self.font.render(self.lineList[i], self.antialias, self.color)

                self.lineListLast.append(self.lineList[-1])

            if self.sizeListLast[i] != self.size:
                self.font = pygame.font.SysFont(self.fontName, self.size)
                self.imgList[i] = self.font.render(self.lineList[i], self.antialias, self.color)

            width, height = img.get_rect().size

            self.dimList[i] = [width, height]

            if self.alignment != "center" and self.alignment != "left":
                raise AlignmentError("Invalid Alignment")

            if self.alignment == "center":
                self.pos = [(pos[0]) - self.dimList[i][0] / 2, (pos[1] - self.dimList[i][1] / 2) + self.dimList[i][1] * (len(self.lineList[0:i]))]
            elif self.alignment == "left":
                self.pos = (pos[0], pos[1] - self.dimList[i][1] / 2 + self.dimList[i][1] * (len(self.lineList[0:i])))

            if drawText:
                gameDisplay.blit(img, self.pos)

            self.lineListLast[i] = self.lineList[i]

            self.sizeListLast[i] = self.size

        if drawCaret:
            if self.caretDuration >= self.maxCaretDuration / 2:
                pygame.draw.line(gameDisplay, self.color, (self.pos[0] + width, self.pos[1] + height), (self.pos[0] + width, self.pos[1]))

    def Wrap(self, maxWidth):
        if self.dimList[-1][0] > maxWidth:
            self.lineList.append("")

            self.lineList[-2] = list(self.lineList[-2])
            
            tempNum = self.lineList[-2].pop(-1)

            self.lineList[-2] = "".join(self.lineList[-2])

            self.lineList[-1] += tempNum
            self.dimList.append([])
            self.sizeListLast.append(self.size)
            self.imgList.append(self.font.render(self.lineList[-1], self.antialias, self.color))
            width, height = self.imgList[-1].get_rect().size
            self.dimList[-1] = [width, height]

    def AddLine(self):
        self.lineList.append("")
        self.dimList.append([])
        self.sizeListLast.append(self.size)
        self.imgList.append(self.font.render(self.lineList[-1], self.antialias, self.color))
        width, height = self.imgList[-1].get_rect().size
        self.dimList[-1] = [width, height]

    def Update(self):
        self.font = pygame.font.SysFont(self.fontName, self.size)
        if self.caretDuration > self.maxCaretDuration:
            self.caretDuration = 0

        self.caretDuration += 0.01

class Spring():
    "Spring()"

    springList = []
    
    def __init__(self, equiLength, pos, stiffness, dampening1, dampening2, elasticity, waveFalloff, WaveStr):
        self.equiLength = equiLength
        self.lengthOffset = 0
        self.lenghtDiff = self.equiLength - self.lengthOffset
        self.stretchForce = 0
        self.depressionAmount = 0
        self.pos = pos
        self.endPos = [self.pos[0], self.pos[1] + self.equiLength]
        self.stiffness = stiffness
        self.dampening1 = dampening1
        self.dampening2 = dampening2
        self.elasticity = elasticity
        self.waveFalloff = waveFalloff
        self.WaveStr = WaveStr
        Spring.springList.append(self)

    def Debug(self):
        pygame.draw.line(gameDisplay, (255, 50, 50), self.pos, (self.pos[0], self.pos[1] - self.equiLength))
        pygame.draw.line(gameDisplay, (255, 255, 255), self.pos, (self.pos[0], self.pos[1] - self.equiLength + self.lengthOffset))

    def AddForce(self, force, waveProp=False):
        self.stretchForce += force

        if waveProp:
            s_springList = sorted(Spring.springList, key=lambda spring: Mag((spring.pos[0] - self.pos[0], spring.pos[1] - self.pos[1])))

            for i, spring in enumerate(s_springList):
                try:
                    spring.stretchForce += force / (((Mag((spring.pos[0] - self.pos[0], spring.pos[1] - self.pos[1])) ** self.waveFalloff)) * self.WaveStr)
                except ZeroDivisionError:
                    pass

    def Update(self):
        self.stretchForce *= self.dampening1

        self.lenghtDiff = self.equiLength - (self.equiLength + self.lengthOffset)

        self.depressionAmount += self.lenghtDiff * self.elasticity

        self.depressionAmount *= self.dampening2

        self.lengthOffset += self.depressionAmount

        self.lengthOffset *= self.stiffness

        self.stretchForce *= self.stiffness

        self.lengthOffset += self.stretchForce

        if self.lenghtDiff < 0.05 and self.lenghtDiff > -0.05 and self.stretchForce < 0.05 and self.stretchForce > -0.05 and self.lengthOffset < 0.05 and self.lengthOffset > -0.05:
            self.stretchForce = 0
            self.lenghtDiff = 0
            self.lengthOffset = 0
            self.depressionAmount = 0

        self.endPos = [self.pos[0], self.pos[1] + self.equiLength + self.lenghtDiff + self.lengthOffset]

    def __repr__(self):
        return f"{self.pos}"

class Bar():
    "Bar()"
    def __init__(self, maxLength, pos, width, dampening, color=(255, 255, 255)):
        self.maxLength = maxLength
        self.width = width
        self.lengthOffset = 0
        self.dampening = dampening
        self.lenghtDiff = self.maxLength - self.lengthOffset
        self.raiseAmount = 0
        self.pos = pos
        self.color = color
        self.endPos = [self.pos[0], self.pos[1] + self.maxLength]

    def Raise(self, Amount):
        self.raiseAmount += Amount

    def Update(self):
        self.lengthOffset += self.raiseAmount

        self.raiseAmount *= self.dampening

        self.lenghtDiff = self.maxLength - (self.maxLength + self.lengthOffset)

        if self.lenghtDiff < 0.05 and self.lenghtDiff > -0.05 and self.raiseAmount < 0.05 and self.raiseAmount > -0.05 and self.lengthOffset < 0.05 and self.lengthOffset > -0.05:
            self.raiseAmount = 0
            self.lenghtDiff = 0
            self.lengthOffset = 0

        if self.maxLength + self.lenghtDiff < 0:
            self.lenghtDiff = -self.maxLength
            self.lengthOffset = self.maxLength
            self.reachedBot = True
        else:
            self.reachedBot = False

        if self.lenghtDiff > 0:
            self.lenghtDiff = 0
            self.lengthOffset = 0
            self.reachedTop = True
        else:
            self.reachedTop = False

        self.endPos = [self.pos[0], self.pos[1] + self.maxLength + self.lenghtDiff + self.lengthOffset]

    def Reset(self):
        self.lengthOffset = self.maxLength
        self.lenghtDiff = -self.maxLength
        self.raiseAmount = 0

    def Draw(self):
        pygame.draw.line(gameDisplay, self.color, self.pos, (self.pos[0], self.pos[1] - self.maxLength + self.lengthOffset), self.width)

class Timer():
    def __init__(self, timestep, stop=0):
        self.time = 0
        self.timestep = timestep
        self.stop = stop
        self.done = False

    def TimeKeep(self):
        if not self.done:
            self.time += self.timestep

            if self.stop:
                if self.time > self.stop:
                    self.done = True
 
class Tadpole():
    def __init__(self, pos, radius):
        global entityArr

        self.x = pos[0]
        self.y = pos[1]
        self.target = None
        self.rect = None
        self.moving = False
        self.viewingDistance = 500
        self.viewingRect = None
        self.birthEnergy = 1500
        self.energyLevel = self.birthEnergy
        self.maxEnergyLevel = 10000
        self.energyDrainRate = 0
        self.eatingFood = False
        self.T_angle = 0
        self.radius = radius
        self.findFoodChance = 0.05
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

        entityArr = np.append(np.array([entityArr]), self)

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
        entityArr.remove(self)

    def TrySplit(self):
        global entityArr

        if self.energyLevel == self.maxEnergyLevel:
            self.energyLevel = self.birthEnergy
            entityArr = np.append(entityArr, Tadpole([self.x + random.randint(-self.radius, self.radius), self.y + random.randint(-self.radius, self.radius)], 12))

    def Move(self):
        if self.target != None:
            self.moving = True
            self.diff = (self.target[0] - self.x, self.target[1] - self.y)
            self.hypoToTarget = Mag(self.diff)
            
            if self.hypoToTarget < self.radius:
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
                    self.T_angle = math.degrees(math.acos(self.diff[0] / self.hypoToTarget))

                    if self.diff[1] > 0:
                        self.T_angle = 360 - self.T_angle
                        
                except ZeroDivisionError:
                    self.T_angle = 0

            self.x += math.cos(math.radians(-self.T_angle)) * 2
            self.y += math.sin(math.radians(-self.T_angle)) * 2

        else:
            self.moving = False

            globals()[f"t{self}"] = threading.Thread(target=self.SearchFood, daemon=True)

            globals()[f"t{self}"].start()

            RandFunc(0.05, lambda: self.SetTarget([self.x + self.noiseValue_x * 200, self.y + self.noiseValue_y * 200]))

    def SearchFood(self):
        if not self.moving:
            tempArr = np.array([])
            for e in entityArr:
                if type(e) == Food:
                    if e.rect != None and self.viewingRect != None:
                        if self.viewingRect.colliderect(e.rect):
                            tempArr = np.append(tempArr, e)

            if tempArr.size > 0:
                self.nearestFoodArr = sorted(tempArr, key=lambda e: Mag((self.x - e.x, self.y - e.y)))
                
                self.Wander()

    def CollisionCheck(self):
        global entityArr

        for i, e in enumerate(entityArr):
            if type(e) == Food:
                if e.rect != None and self.rect != None:
                    if self.rect.colliderect(e.rect):
                        self.EatFood(e.nourishment)
                        entityArr = np.delete(entityArr, i)
                        self.SetTarget(None)

            e.x = Constrain(e.x, -Map.size[0] + e.radius, Map.size[0] - e.radius)
            e.y = Constrain(e.y, -Map.size[1] + e.radius, Map.size[1] - e.radius)

    def Wander(self):
        if RandFunc(self.findFoodChance, lambda: self.SetTarget([self.nearestFoodArr[0].x, self.nearestFoodArr[0].y])):
            self.eatingFood = True

    def Update(self, dt):
        self.Move()
        self.CollisionCheck()
        self.TrySplit()

        self.rect = Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

        self.viewingRect = Rect(self.x - self.viewingDistance, self.y - self.viewingDistance, self.viewingDistance * 2, self.viewingDistance * 2)

        if self.energyLevel > self.maxEnergyLevel:
            self.energyLevel = self.maxEnergyLevel

        self.energyLevel -= self.energyDrainRate

        if self.energyLevel <= 0:
            self.Decease()

    def Draw(self):
        if (self.x > Camera.x - self.radius and self.x < Camera.x + display_x) and (self.y > Camera.y - self.radius and self.y < Camera.y + display_y):
            self.color = (255 - Constrain(self.energyLevel, 0, self.maxEnergyLevel, 0, 255), Constrain(self.energyLevel, 0, self.maxEnergyLevel, 0, 255) / 15 + 150, Constrain(self.energyLevel, 0, self.maxEnergyLevel, 0, 255) / 25 + 89)

            pygame.draw.circle(gameDisplay, self.color, (round(self.x) - Camera.x, round(self.y) - Camera.y), self.radius)

            if debug:
                if self.target != None:
                    pygame.draw.circle(gameDisplay, (255, 255, 255), (round(self.target[0]), round(self.target[1])), 4)

                    pygame.draw.rect(gameDisplay, (255 ,255 ,255), (self.rect.x - Camera.x, self.rect.y - Camera.y, self.rect.width, self.rect.height), 1)

class Food():
    def __init__(self, pos, nourishment):
        global entityArr

        self.x = pos[0]
        self.y = pos[1]
        self.nourishment = nourishment
        self.rect = None
        self.radius = round(Constrain(self.nourishment ** 0.85, 10, 1000, 3, 9.5))

        entityArr = np.append(np.array([entityArr]), self)

    def Update(self, dt):
        self.radius = round(Constrain(self.nourishment ** 0.85, 10, 1000, 3, 9.5))

        self.rect = Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def Draw(self):
        if (self.x > Camera.x - self.radius and self.x < Camera.x + display_x) and (self.y > Camera.y - self.radius and self.y < Camera.y + display_y):
            pygame.draw.circle(gameDisplay, (170, 100, 43), (round(self.x) - Camera.x, round(self.y) - Camera.y), round(Constrain(self.nourishment ** 0.85, 10, 1000, 3, 9.5)))

            if debug:
                if self.rect != None:
                    pygame.draw.rect(gameDisplay, (255 ,255 ,255), (self.rect.x - Camera.x, self.rect.y - Camera.y, self.rect.width, self.rect.height), 1)

    @staticmethod
    def SpawnFood():
        global entityArr

        for i in range(1):
            entityArr = np.append(np.array([entityArr]), Food([random.randint(-Map.size[0], Map.size[0]), random.randint(-Map.size[1], Map.size[1])], random.randint(10, 1000)))

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

for i in range(1):
    globals()[f"tad{i}"] = Tadpole([random.randint(-Map.size[0], Map.size[0]), random.randint(-Map.size[1], Map.size[1])], 12)

for i in range(500):
    globals()[f"food{i}"] = Food([random.randint(-Map.size[0], Map.size[0]), random.randint(-Map.size[1], Map.size[1])], random.randint(10, 1000))

# Main Loop

while running:

    t = pygame.time.get_ticks()

    deltaTime = (t - last_t) / 1000.0

    # Event Handeling

    for event in pygame.event.get():
        
        if event.type == QUIT:
            pygame.quit()
            running = False

        if not running:
            break

        # Controls

        if event.type == KEYDOWN:
            keys[event.key] = True

            if keys.get(K_ESCAPE):
                pygame.quit()
                running = False
                break

        if event.type == KEYUP:
            keys[event.key] = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouseDown = True
                entityArr = np.append(entityArr, Tadpole([pygame.mouse.get_pos()[0] + Camera.x, pygame.mouse.get_pos()[1] + Camera.y], 12))

            if event.button == 3:
                pass

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouseDown = False

            if event.button == 3:
                pass

        if event.type == pygame.MOUSEMOTION:
            pass

    # Control Actions

    if keys.get(303) or keys.get(304):
        if keys.get(K_w):
            Camera.y -= Camera.speed * 3

        if keys.get(K_a):
            Camera.x -= Camera.speed * 3

        if keys.get(K_s):
            Camera.y += Camera.speed * 3

        if keys.get(K_d):
            Camera.x += Camera.speed * 3

    else:
        if keys.get(K_w):
            Camera.y -= Camera.speed

        if keys.get(K_a):
            Camera.x -= Camera.speed

        if keys.get(K_s):
            Camera.y += Camera.speed

        if keys.get(K_d):
            Camera.x += Camera.speed

    # Exit Without An Error Message

    if not running:
        break

    # Do The Actual Game

    Camera.Update()

    for e in entityArr:
        e.Draw()
        e.Update(deltaTime)

    # RandFunc(0.01, Food.SpawnFood)

    # This Always Goes Last

    fps = font.render(str(int(clock.get_fps())), True, white)
    gameDisplay.blit(fps, (25, 25))

    pygame.display.flip()

    gameDisplay.fill(black)

    clock.tick(gameSpeed)

    last_t = t 