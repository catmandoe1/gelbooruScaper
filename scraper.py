import mouse
import keyboard
import time
import mss
import mss.tools
import numpy as np
import sys
import math

SCREEN = 1 # 1 OR 2 (assuming 1920x1080 HD)

if SCREEN == 1:
    offset = 0
else:
    offset = SCREEN * 1920

mouseDelay = 0.1
imageLocation = {
    "top": 343,
    "left": 262 + offset,
    "width": 1,
    "height": 3
}

pageContentLocation = {
    "top": 272,
    "left": 240 + offset,
    "width": 1661,
    "height": 753
}

def killSwitch():
    raise Exception("Stopped!")
      
def click(type = "left"):
    print("clicked")
    if type == "left":
        mouse.click(type)
    elif type == "right":
        mouse.click(type)
    else:
        raise ValueError(f"{type} is not a valid click")

def moveMouse(x, y, time = 0):
    mouse.move(x, y, True, time)

def pressKey(key):
    try:
        keyboard.send(key)
    except:
        raise ValueError(f"{key} is not a valid key")
    
def saveImage(savePath, nSaved, name, first = False):
    if first:
        moveMouse(620 + offset, 55, mouseDelay) # path bar
        click()
        keyboard.write(savePath)
        pressKey("enter")

        moveMouse(360 + offset, 440, mouseDelay) # file name bar
        click()
        keyboard.write(f"{name} - {nSaved}")

        moveMouse(780 + offset, 506, mouseDelay) # save button
        click()
    else:
        keyboard.write(f"{name} - {nSaved}")
        moveMouse(780 + offset, 506, mouseDelay) # save button
        click()

def openSaveMenu():
    click("right")
    time.sleep(0.1)
    pressKey("v")
    time.sleep(0.25)

def goIntoPic():
    click()
    moveMouse(262 + offset, 343, mouseDelay)

    while True:
        ss = mss.mss()
        area = np.array(ss.grab(imageLocation))
        print(area.sum())
        print(area)
        if area.sum() != 1044:
            break

def checkIfPic(y, i):
    location = {
    "top": 350 + (y % 3) * 200,
    "left": (330 + i * 200) + offset,
    "width": 1,
    "height": 3
    }
    
    timeout = 0
    while True:
        if timeout == 500:
            raise TimeoutError("timed out or reached end")
        ss = mss.mss()
        area = np.array(ss.grab(location))
        if area.sum() != 1044:
            break
        
        timeout = timeout + 1
        time.sleep(0.01)

def addMinusVideoTag():
    print("adding \"-video\" tag...")
    moveMouse(210 + offset, 240, mouseDelay) # tag bar
    click()
    pressKey("end")
    pressKey("space")
    keyboard.write("-video")
    pressKey("enter")
    print("complete")
    time.sleep(3)
    print("starting...")

def getNumFromUser(message):
    while True:
        try:
            x = int(input(message))
            return x
        except:
            print("invalid number")

def nextPage(page):
    moveMouse(800 + offset, 65, mouseDelay) # url bar
    click()
    pressKey("end")
    keyboard.write(f"&pid={page * 42}")
    pressKey("enter")
    time.sleep(2)
    

def main():
    imgsPerRow = 8#8
    imgsPerColumn = 6#6
    savePath = "C:/Programs/visual_studio_code/Python/gelbooruScaper/saves"
    preSnipSum = -1

    print("MAKE SURE URL DOESNT HAVE &pid=[x] IN IT")
    print("press \"alt+q\" to stop")

    keyboard.add_hotkey("alt+q", killSwitch)

    saved = 0
    currentName = input("enter name: ")
    amount = getNumFromUser("enter amount of images to scrape (-1 = infinite): ")

    if amount >= 0:
        pages = math.ceil(amount / (imgsPerRow * imgsPerColumn))
    else:
        pages = sys.maxsize * 2 + 1 # big number !!!

    addMinusVideoTag()
    mouse.wheel(800)

    if pages == 0:
        raise Exception("cant scrape 0 pages")

    for page in range(0, pages):
        for y in range(0, imgsPerColumn):
            if y == 3:
                mouse.wheel(-200)
                time.sleep(0.4)

            for i in range(0, imgsPerRow):

                if y == 5 and i == 2:
                    break # last picture normally

                # seeing if page has changed
                while True:
                    ss = mss.mss()
                    ss = np.array(ss.grab(pageContentLocation))

                    if ss.sum() != preSnipSum:
                        break

                moveMouse((330 + i * 200) + offset, 350 + (y % 3) * 200, mouseDelay) # hover on the pic
                print(str((330 + i * 200) + offset), str( 350 + (y % 3) * 200))
                
                checkIfPic(y, i)

                goIntoPic()

                openSaveMenu()

                if y == 0 and i == 0:
                    saveImage(savePath, saved, currentName, True)
                saveImage(savePath, saved, currentName)
                saved = saved + 1
                pressKey("alt+left_arrow")
                
                # used for checking if page as changed
                ss = mss.mss()
                ss = np.array(ss.grab(pageContentLocation))
                preSnipSum = ss.sum()


                time.sleep(1.25)
        nextPage(page + 1)
main()