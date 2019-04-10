"Note: You must initialize pygame before using this module."
import math
import random
import getpass
import urllib
from urllib.request import urlopen as uReq
import re
import os
import sys
import subprocess

def InstallPackages(packages, doRestart=True):
    "Installs all packages in a list."
    restart = False

    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

    for p in packages:
        if not p.lower() in [name.lower() for name in installed_packages]:
            try:
                os.system(f"pip install {p}")
            except ModuleNotFoundError as e:
                print(e)
            else:
                restart = True

    if restart and doRestart:
        print("Package(s) installed, restarting...")

        os.execl(sys.executable, sys.executable, * sys.argv)

InstallPackages(["bs4", "pillow"])

from bs4 import BeautifulSoup as soup
from PIL import Image, ImageDraw

def Contains(iterable, find):
    "Checks if an element exists in an iterable, returns a dict."
    iteration = 0
    for i in iterable:
        if i == find:
            result = True
            index = iteration
            return {"result":result, "index":index}
        iteration += 1
    
    index = -1

    result = False
    return {"result":result, "index":index}

def IterSum(iterable, operation="+"):
    "Adds up all elements of an iterable and returns the result. Note: all elements in said iterable must be numbers i.e no letters, symbols etc. There are also more than just the sum of all the elements, here are a list of the available operators (+, -, *, /, abs) Note: abs returns the original iterable."

    if operation == "+":
        answer = 0
        for i in iterable:
            answer += float(i)
        return answer

    elif operation == "-":
        answer = 0
        for i in iterable:
            answer -= i
        return answer

    elif operation == "*":
        answer = 1
        for i in iterable:
            answer *= i
        return answer

    elif operation == "/":
        answer = 1
        for i in iterable:
            answer /= i
        return answer

    elif operation == "abs":
        for i, item in enumerate(iterable):
            iterable[i] = abs(item)
        return iterable

def PixelScan(image, returntype=dict):
    "If returntype is dict: Returns a list of dictionaries consisting of colors and coords where the coords are the keys and the colors are the values. \n \n If returntype is list: Returns a list consisting of colors for each pixel of the image."
    
    pygame.init()

    if returntype == dict:
        scan_x = 0
        scan_y = 0
        pixelList = {}
        imageWidth, imageHight = image.get_rect().size
        while True:
            if scan_x >= imageWidth:
                scan_x = 0
                scan_y += 1

            if scan_y >= imageHight:
                return pixelList

            scanned_pixel = image.get_at((scan_x, scan_y))

            scanned_pixel = tuple(scanned_pixel)

            pixelList[(scan_x, scan_y)] = scanned_pixel

            scan_x += 1

    if returntype == list:
        scan_x = 0
        scan_y = 0
        pixelList = []
        imageWidth, imageHight = image.get_rect().size
        while True:
            if scan_x >= imageWidth:
                scan_x = 0
                scan_y += 1

            if scan_y >= imageHight:
                return pixelList

            scanned_pixel = image.get_at((scan_x, scan_y))

            pixelList.append(scanned_pixel)

            scan_x += 1

def TryDir(directory, create=False):
    "Retruns a boolean whether a directory exists or not. Can specify whether or not to create said directory if not already present."
    try:
        os.stat(directory)
    except FileNotFoundError:
        if create:
            os.mkdir(directory)
        return False
    else:
        return True

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

def Mag(x): 
    "Returns the magnitude of any iterable."
    return math.sqrt(sum(i**2 for i in x))

def Dictionary():
    "Creates a file on your desktop called \"Dictionary.txt\" containing a long list of words taken from the oxford dictionary. Only creates the text file if it doesn't already exist."
    dictionary = ""

    url_1 =  "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_A-B/?page=1"
    url_2 =  "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_A-B/?page=2"
    url_3 =  "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_A-B/?page=3"
    url_4 =  "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_A-B/?page=4"
    url_5 =  "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_A-B/?page=5"
    url_6 =  "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_C-D/?page=1"
    url_7 =  "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_C-D/?page=2"
    url_8 =  "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_C-D/?page=3"
    url_9 =  "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_C-D/?page=4"
    url_10 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_C-D/?page=5"
    url_11 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_C-D/?page=6"
    url_12 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_C-D/?page=7"
    url_13 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_E-G/?page=1"
    url_14 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_E-G/?page=2"
    url_15 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_E-G/?page=3"
    url_16 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_E-G/?page=4"
    url_17 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_E-G/?page=5"
    url_18 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_E-G/?page=6"
    url_19 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_H-K/?page=1"
    url_20 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_H-K/?page=2"
    url_21 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_H-K/?page=3"
    url_22 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_H-K/?page=4"
    url_23 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_L-N/?page=1"
    url_24 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_L-N/?page=2"
    url_25 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_L-N/?page=3"
    url_26 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_L-N/?page=4"
    url_27 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_O-P/?page=1"
    url_28 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_O-P/?page=2"
    url_29 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_O-P/?page=3"
    url_30 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_O-P/?page=4"
    url_31 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_O-P/?page=5"
    url_32 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_Q-R/?page=1"
    url_33 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_Q-R/?page=2"
    url_34 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_Q-R/?page=3"
    url_35 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_S/?page=1"
    url_36 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_S/?page=2"
    url_37 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_S/?page=3"
    url_38 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_S/?page=4"
    url_39 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_S/?page=5"
    url_40 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_T/?page=1"
    url_41 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_T/?page=2"
    url_42 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_T/?page=3"
    url_43 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_U-Z/?page=1"
    url_44 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_U-Z/?page=2"
    url_45 = "https://www.oxfordlearnersdictionaries.com/wordlist/english/oxford3000/Oxford3000_U-Z/?page=3"

    url_list = [url_1, url_2, url_3, url_4, url_5, url_6, url_7, url_8, url_9, url_10, url_11, url_12, url_13, url_14, url_15, url_16, url_17, url_18, url_19, url_20, url_21, url_22, url_23, url_24, url_25, url_26, url_27, url_28, url_29, url_30, url_31, url_32, url_33, url_34, url_35, url_36, url_37, url_38, url_39, url_40, url_41, url_42, url_43, url_44, url_45]

    for url in url_list:
        try:
            uClient = uReq(url)

            page_html = uClient.read()

            uClient.close()

            pageSoup = soup(page_html, "html.parser")

            words = pageSoup.find_all(class_="result-list1 wordlist-oxford3000 list-plain")

            words = words[0].text

            words = words.split("\n")

            for i in range(len(words)):
                try:
                    words.remove("")
                except:
                    continue

            words = " ".join(words)

            dictionary += words

        except urllib.error.HTTPError:
            print("HTTP ERROR!")
            break
    try:
        with open(f"C:/Users/{getpass.getuser()}/Desktop/Dictionary.txt", "w") as f:
            f.write(str(dictionary))
        return "Dictionary done!"
    except UnboundLocalError:
        pass

def BlendColors(colorList):
    "Blends two or more colors."
    for color in colorList:
        if len(color) != 3:
            raise ValueError("one or more of the colors in the list is not a valid color")

    R = 0
    G = 0
    B = 0

    for color in colorList:
        R += color[0]
        G += color[1]
        B += color[2]

    R /= len(colorList)
    G /= len(colorList)
    B /= len(colorList)

    return [R, G, B]

def BlendColorsAlpha(colorList):
    "Blends two or more colors with alpha layer."
    for color in colorList:
        if len(color) != 4:
            raise ValueError("one or more of the colors in the list is not a valid color")

    R = 0
    G = 0
    B = 0
    A = 0

    for color in colorList:
        R += color[0]
        G += color[1]
        B += color[2]
        A += color[3]

    R /= len(colorList)
    G /= len(colorList)
    B /= len(colorList)
    A /= len(colorList)

    return [R, G, B, A]

def isequation(string):
    "Checks if a string is clasified as an equation by python"
    match = re.match(r"\s*(\d+)\s*(-=?|\+=?|/=?|%=?|\*=?|\*\*=?)\s*(\d+)\s*", string)
    if match:
        return match.groups()

def RandFunc(chance, func):
    "Calls a function at a given chance. Returns a bool stating whether the function has been passed or not"
    chance = 1 - chance

    if random.uniform(1, 2) - 1 > chance:
        func()

        return True

    return False

def PathExtend(extension):
    "Returns an extended path from the executable path."
    if os.path.dirname(__file__) != "":
        for i, char in enumerate(extension):
            if char == "/":
                extension = list(extension)

                extension[i] = "\\"
                    
                extension = "".join(extension)

        if getattr(sys, 'frozen', False):
            basedir = sys._MEIPASS
        else:
            basedir = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(basedir, f"{extension}")

    else:
        for i, char in enumerate(extension):
            if char == "/":
                extension = list(extension)

                extension[i] = "\\"
                    
                extension = "".join(extension)

        if getattr(sys, 'frozen', False):
            basedir = sys._MEIPASS
        else:
            basedir = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(basedir, f"{extension}")
