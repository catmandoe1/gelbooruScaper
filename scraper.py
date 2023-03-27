import mouse
import keyboard
import time
import mss
import mss.tools
import numpy as np
import sys
import cv2
import pyperclip as clipboard
import os

SCREEN = 2 # 1 OR 2 (assuming 1920x1080 HD)
global yOffset
global saved

yOffset = 0
saved = 0

if SCREEN == 1:
    offset = 0
else:
    offset = (SCREEN - 1) * 1920

MOUSEDELAY = 0.1
MAX_IMAGE_WIDTH = 175
MAX_IMAGE_HEIGHT = 175
IMAGES_PER_ROW = 8
IMAGES_PER_COLUMN = 6
IMAGES_PER_PAGE = 42 # by default on 1920 x 1080
INVALID_PATH_CHARACTERS = ["\\", "/", ":", "*", "?", "<", ">", "|"]
#SAVEPATH = "C:/Programs/visual_studio_code/Python/gelbooruScaper/saves"
SAVEPATH = os.getcwd() + r"\saves"

imageLocation = {
    "top": 341,
    "left": 260 + offset,
    "width": 1640,
    "height": 691
}

pageContentLocation = {
    "top": 272,
    "left": 240 + offset,
    "width": 1661,
    "height": 753
}

def killSwitch():
    sys.exit("Stopped by user or Finished")

def clear():
    os.system("cls")
      
def click(type = "left"):
    #print("clicked")
    if type == "left":
        mouse.click(type)
    elif type == "right":
        mouse.click(type)
    elif type == "middle":
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
    
def isValidName(name):
    if(not(name and name.strip())):
        raise ValueError("Name can't be empty")

    for char in name:
        if char in INVALID_PATH_CHARACTERS:
            raise ValueError("Invalid name")
    
    return True
    
def checkIfnotCreateDir(path, name):
    newName = name.replace(" ", "-")
    newName = newName.replace("_", "-")

    

    fullPath = path + "\\" + newName

    if not os.path.exists(fullPath):
        os.mkdir(fullPath)
    
    return fullPath

    
def saveImage(savePath, nSaved, name, first = False):
    if first:
        moveMouse(620 + offset, 55, MOUSEDELAY) # path bar
        click()
        keyboard.write(savePath)
        pressKey("enter")

        moveMouse(360 + offset, 440, MOUSEDELAY) # file name bar
        click()
        keyboard.write(f"{name} - {nSaved}")

        moveMouse(780 + offset, 506, MOUSEDELAY) # save button
        click()
    else:
        keyboard.write(f"{name} - {nSaved}")
        moveMouse(780 + offset, 506, MOUSEDELAY) # save button
        click()

def openSaveMenu():
    click("right")
    time.sleep(0.1)
    pressKey("v")
    time.sleep(0.25)

def goIntoPic():
    ss = mss.mss()
    pre = np.array(ss.grab(imageLocation))
    preSum = pre.sum()

    click()
    moveMouse(262 + offset, 343, MOUSEDELAY) # ready to save
    time.sleep(0.4)

    while True:
        ss = mss.mss()
        area = np.array(ss.grab(imageLocation))
        sum = area.sum()
        if sum != 394367520 and sum != preSum: # the number is equal to the sum of defualt background, when the image loads it changes
            print("image loaded")
            break
    
def waitTillImageLoaded():
    ss = mss.mss()
    pre = np.array(ss.grab(imageLocation))
    preSum = pre.sum()

    moveMouse(262 + offset, 343, MOUSEDELAY) # ready to save

    while True:
        ss = mss.mss()
        area = np.array(ss.grab(imageLocation))
        sum = area.sum()
        if sum != 394367520: #and sum != preSum: # the number is equal to the sum of defualt background, when the image loads it changes
            print("image loaded")
            break


def checkIfPic(y, i):
    location = {
    "top": pictureY(y),
    "left": pictureX(i),
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
    moveMouse(210 + offset, 240, MOUSEDELAY) # tag bar
    click()
    pressKey("end")
    pressKey("space")
    keyboard.write("-video")
    pressKey("enter")
    print("complete")
    time.sleep(3)
    print("starting...")

def getAmtPagesFromUser(*message):
    while True:
        try:
            for text in message:
                print(text)
            x = input()

            if x[:1] == "p":
                pages = int(x[1:]) * IMAGES_PER_PAGE
                return pages

            x = int(x)
            return x
        except:
            print("invalid input")

def nextPage(page):
    raise DeprecationWarning("not used")
    newUrl = ""
    moveMouse(800 + offset, 65, MOUSEDELAY) # url bar
    click()
    pressKey("ctrl+c")
    time.sleep(0.1)
    url = clipboard.paste() # gets url

    #url2 = r"https://gelbooru.com/index.php?page=post&s=list&tags=shiroko_%28blue_archive%29"
    #url = r"https://gelbooru.com/index.php?page=post&s=list&tags=muoto&pid=42"

    url = url.split("&")
    print(url)
    url.pop() # removes the page id
    print(url)

    for segs in url:
        if segs == "s=view":
            newUrl = newUrl + "&" + "s=list"
        else:
            newUrl = newUrl + "&" + segs

    newUrl = newUrl[1:]
    print(newUrl)
    newUrl = newUrl + f"&pid={page * 42}"

    clipboard.copy(newUrl)
    
    #keyboard.write(f"&pid={page * 42}")
    pressKey("ctrl+v")
    time.sleep(0.1)
    pressKey("enter")
    time.sleep(2)
    print("now on page", page + 1)
    
def pictureX(rowStage):
    return (337 + rowStage * 195) + offset

def pictureY(columnStage):
    return (384 + (columnStage % 3) * 206) - yOffset

def progress(nSaved, maxSaved):
    s = "PROGRESS"
    e = ""
    print(f"{s:=^100}")
    fraction = f"{nSaved} / {maxSaved}"
    precent = f"{round((nSaved / maxSaved) * 100)}%"
    savepath = f"Save path: {SAVEPATH}"
    print(f"{fraction: ^100}")
    print(f"{precent: ^100}")
    print(f"{savepath: ^100}")
    print(f"{e:=^100}")


def waitTillImageSwitched(previousImage):
    repeats = 0
    while True:
        ss = mss.mss()
        ss = np.array(ss.grab(imageLocation))
        ss = cv2.cvtColor(ss, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(ss, previousImage, cv2.TM_CCOEFF_NORMED)
        _, maxV, _, _ = cv2.minMaxLoc(result)
        if repeats % 10 == 0:
            print(maxV)

        if maxV < 0.99:
            # cv2.imshow("prev", previousImage)
            # cv2.imshow("curr", ss)
            # cv2.waitKey()
            print("loaded next image")
            return
        
        repeats = repeats + 1

        if repeats == 100:
            print("detected no change in page")
            if checkPageAndCompare():
                return

            # cv2.imshow("cur", ss)
            # cv2.imshow("prev", previousImage)
            # cv2.waitKey()
            # raise TimeoutError("Timed out or hit end")

def checkPageAndCompare():
    global saved

    savedBoard = clipboard.paste() # keeping last copied thing

    print("compairing ids to check if page has updated")
    moveMouse(800 + offset, 65, MOUSEDELAY) # url bar
    click()
    pressKey("ctrl+c")
    time.sleep(0.1)
    url = clipboard.paste() # gets url of current page

    moveMouse(1920 / 2 + offset, 1080 / 2, MOUSEDELAY)
    click()
    pressKey("right_arrow")
    time.sleep(2) # waiting for new url

    moveMouse(800 + offset, 65, MOUSEDELAY) # url bar
    click()
    pressKey("ctrl+c")
    time.sleep(0.1)
    url2 = clipboard.paste() # gets url of current page

    moveMouse(1920 / 2 + offset, 1080 / 2, MOUSEDELAY)
    click()

    clipboard.copy(savedBoard)

    
    #url = r"https://gelbooru.com/index.php?page=post&s=view&id=8042932&tags=hayasaka_%28a865675167774%29"
    #url2 = r"https://gelbooru.com/index.php?page=post&s=view&id=8042931&tags=hayasaka_%28a865675167774%29"

    print(url)
    print(url2)

    url = url.split("&")
    url2 = url2.split("&")

    id1 = ""
    id2 = ""

    for tag in url:
        if tag[:3] == "id=":
            print("id 1:", tag[3:])
            id1 = tag[3:]
            break
    for tag in url2:
        if tag[:3] == "id=":
            print("id 2:", tag[3:])
            id2 = tag[3:]
            break

    if id1 != id2:
        print("change detected, continuing")
        #saved = saved - 1
        pressKey("left_arrow")
        time.sleep(2)
        return True
    else:
        raise TimeoutError("Page timed out or reached end")
    

def main():
    global yOffset
    global saved

    #preSnip = cv2.cvtColor(cv2.imread("C:/Programs/visual_studio_code/Python/gelbooruScaper/blank-new.png"), cv2.COLOR_BGR2GRAY)
    preSnip = cv2.cvtColor(cv2.imread("C:/Programs/visual_studio_code/Python/gelbooruScaper/blank.jpg"), cv2.COLOR_BGR2GRAY)
    

    #print("MAKE SURE URL DOESNT HAVE &pid=[x] IN IT")
    print("press \"alt+q\" to stop")
    print("choosen screen =", SCREEN)

    keyboard.add_hotkey("alt+q", killSwitch)

    
    currentName = input("enter name: ")
    isValidName(currentName)
    amount = getAmtPagesFromUser("enter amount of images to scrape,", "-1 = infinite", f"use a surfix of p to count in pages (p2 = {IMAGES_PER_PAGE * 2} images)")

    if amount == -1:
        amount = sys.maxsize * 2 + 1 # big number !!!
    elif amount == 0:
        raise ValueError("cant scrape 0 images")

    moveMouse(1920 / 2 + offset, 1080 / 2, MOUSEDELAY)
    mouse.wheel(800)
    addMinusVideoTag()

    # initial image select
    moveMouse(pictureX(0), pictureY(0), MOUSEDELAY)
    goIntoPic()

    while saved < amount:
        progress(saved, amount)
        if saved != 0:
            time.sleep(1) # super simple fix
            waitTillImageSwitched(preSnip)
            waitTillImageLoaded()

        openSaveMenu()

        if saved == 0:
            saveImage(checkIfnotCreateDir(SAVEPATH, currentName), saved, currentName, True)
        else:
            saveImage(checkIfnotCreateDir(SAVEPATH, currentName), saved, currentName)

        time.sleep(0.4)
        ss = mss.mss()
        ss = np.array(ss.grab(imageLocation))
        preSnip = cv2.cvtColor(ss, cv2.COLOR_BGR2GRAY)

        if saved != amount - 1:
            pressKey("right_arrow")
        saved = saved + 1
        clear()

    print("finished")

print("save path =", SAVEPATH)
main()

# new branch!!!