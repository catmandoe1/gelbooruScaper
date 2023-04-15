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
import json
import requests
import shutil

"""
    Written for and with Windows 11, Firefox, Python 3.10.7


    yoffset used to avoid those annoying unclosable banners.
    the standard notice of 02/04/2023 (UK date) offset would be 36 (pixels)
    this is overriden by settings.json, edit that instead

"""
yOffset = 0
saved = 0
logText = []
timeElapsed = 0

if not os.path.exists(os.getcwd() + r"\settings.json"):
    # defaults dont touch
    DATA = {
        "screen": 1,
        "shutdown_on_completion": False,
        "y_offset": 0,
        "clear_console": True,
        "save_path": "default",
        "mouse_delay": 0.1,
        "avoid_artist_credits": True,
        "max_image_width": 175,
        "max_image_height": 175,
        "images_per_row": 8,
        "images_per_column": 6,
        "images_per_page": 42,
        "invalid_path_characters": ["\\", "/", ":", "*", "?", "<", ">", "|"]
    }

    json.dump(DATA, open("settings.json", "w"), indent=4)
    
else:
    DATA = json.load(open("settings.json", "r"))

SCREEN = DATA["screen"] # 1 OR 2 (assuming 1920x1080)
MOUSEDELAY = DATA["mouse_delay"] # zero for no mouse animations or delay
MAX_IMAGE_WIDTH = DATA["max_image_width"]
MAX_IMAGE_HEIGHT = DATA["max_image_height"]
IMAGES_PER_ROW = DATA["images_per_row"]
IMAGES_PER_COLUMN = DATA["images_per_column"]
IMAGES_PER_PAGE = DATA["images_per_page"] # by default on 1920 x 1080
INVALID_PATH_CHARACTERS = DATA["invalid_path_characters"]
SHUTDOWN_ON_COMPLETION = DATA["shutdown_on_completion"]
CLEAR_CONSOLE = DATA["clear_console"]
AVOID_ARTIST_CREDITS = DATA["avoid_artist_credits"]
if DATA["save_path"] == "default":
    SAVEPATH = os.getcwd() + r"\saves"
else:
    SAVEPATH = DATA["save_path"]
yOffset = DATA["y_offset"]
if AVOID_ARTIST_CREDITS:
    yCreditOffset = 108
else:
    yCreditOffset = 0

if SCREEN == 1:
    offset = 0
else:
    offset = (SCREEN - 1) * 1920

imageLocation = {
    "top": 341 + yOffset,
    "left": 260 + offset - yCreditOffset,
    "width": 1640,
    "height": 691 - yOffset - yCreditOffset
}

# the number is equal to the sum of defualt background, when the image loads it changes
# sum is height of image * width of image * the sum of a pixel (default background rgba = 31, 31, 31, 255)
SUM_OF_IMAGE_BACKGROUND = (imageLocation["height"] * imageLocation["width"]) * (31 + 31 + 31 + 255)

def shutdown():
    os.system("shutdown /s /t 1")

def killSwitch():
    if SHUTDOWN_ON_COMPLETION:
        shutdown()
    sys.exit("Stopped by user or Finished")

def logOut(*text):
    global logText
    ctime = getTimeFormatted()
    newText = ""

    for i in range(0, len(text)):
        if i == 0:
            newText = str(text[i])
        else:
            newText = newText + " " + str(text[i])

    newText = f"[{ctime}]: {newText}"

    print(newText)
    logText.append(newText)

def getTimeFormatted():
    return time.strftime("%H:%M:%S")

def getHrMnScFromSeconds(secs):
    # translated and adapted from java
    hours = 0
    mins = 0
    hour = "Hours"
    min = "Minutes"
    sec = "Seconds"
    # time = ""
    # flag = False
    while secs > 59:
        secs = secs - 60
        mins += 1
    while mins > 59:
        mins = mins - 60
        hours += 1
    if hours == 1:
        hour = "Hour"
    if mins == 1:
        min = "Minute"
    if secs == 1:
        sec = "Second"
    
    return f"{hours} {hour} {mins} {min} {secs} {sec}"

    

def clear():
    if CLEAR_CONSOLE:
        os.system("cls")
      
def click(type = "left"):
    if type == "left":
        mouse.click(type)
    elif type == "right":
        mouse.click(type)
    elif type == "middle":
        mouse.click(type)
    else:
        raise ValueError(f"{type} is not a valid click")

def moveMouse(x, y, time = 0, relative=False):
    mouse.move(x, y, not relative, time)

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
    
def getSaveImagePath(path, name):
    newName = name.replace(" ", "-")
    newName = newName.replace("_", "-")

    fullPath = path + "\\" + newName

    if not os.path.exists(fullPath):
        os.mkdir(fullPath)

    return fullPath


def saveImage(url, savePath, name, nSaved):
    request = requests.get(url, stream = True)

    if request.status_code == 200:
        logOut("downloading...")
        extension = url.split(".")
        extension = extension[len(extension) - 1]
        shutil.copyfileobj(request.raw, open(f"{savePath}\\{name} - {nSaved}.{extension}", "wb"))
        logOut(f"downloaded {savePath} from {url}")
    else:
        logOut(f"{url} is an invalid url/image/video")

def getContentURL():
    #moving possible translation
    mouse.drag(0, 0, 100, 0, False, MOUSEDELAY)
    moveMouse(-100, 0, MOUSEDELAY, True)
    time.sleep(0.5)
    click() # stops possible video
    click("right")
    time.sleep(0.1)
    pressKey("o") # gets image/video url
    time.sleep(0.1)
    return clipboard.paste()

def goIntoPic():
    ss = mss.mss()
    pre = np.array(ss.grab(imageLocation))
    preSum = pre.sum()

    click()
    moveMouse(266 + offset, 347 + yOffset, MOUSEDELAY)
    time.sleep(0.4)

    while True:
        ss = mss.mss()
        area = np.array(ss.grab(imageLocation))
        sum = area.sum()
        #sum = 394367520 by default

        if sum != SUM_OF_IMAGE_BACKGROUND and sum != preSum: 
            logOut("image loaded")
            break
    
def waitTillImageLoaded():
    ss = mss.mss()
    pre = np.array(ss.grab(imageLocation))
    preSum = pre.sum()

    moveMouse(266 + offset, 347 + yOffset + yCreditOffset, MOUSEDELAY) # ready to save

    while True:
        ss = mss.mss()
        area = np.array(ss.grab(imageLocation))
        sum = area.sum()
        if sum != SUM_OF_IMAGE_BACKGROUND: #and sum != preSum: # the number is equal to the sum of defualt background, when the image loads it changes
            logOut("image loaded")
            break

def getAmtPagesFromUser(*message):
    while True:
        try:
            for text in message:
                logOut(text)
            x = input()

            if x[:1] == "p":
                pages = int(x[1:]) * IMAGES_PER_PAGE
                return pages

            x = int(x)
            return x
        except:
            logOut("invalid input")

def getNumFromUser(*message):
    while True:
        try:
            for text in message:
                logOut(text)
            x = input()

            x = int(x)
            return x
        except:
            logOut("invalid number")
    
def pictureX(rowStage):
    return (337 + rowStage * 195) + offset

def pictureY(columnStage):
    return (384 + (columnStage % 3) * 206) + yOffset

def progress(nSaved, maxSaved):
    s = "PROGRESS"
    e = ""
    exit = "\"alt + q\" to exit at anytime"
    logOut(f"{s:=^100}")
    fraction = f"{nSaved} / {maxSaved}"
    precent = f"{round((nSaved / maxSaved) * 100)}%"
    savepath = f"Save path: {SAVEPATH}"
    shutDown = "SHUTDOWN ON COMPLETION IS ENABLED"
    logOut(f"{fraction: ^100}")
    logOut(f"{precent: ^100}")
    logOut(f"{savepath: ^100}")
    if SHUTDOWN_ON_COMPLETION:
        logOut(f"{shutDown: ^100}")
    logOut(f"{exit: ^100}")
    logOut(f"{e:=^100}")


def waitTillImageSwitched(previousImage):
    repeats = 0
    while True:
        ss = mss.mss()
        ss = np.array(ss.grab(imageLocation))
        ss = cv2.cvtColor(ss, cv2.COLOR_BGR2GRAY)
        
        result = cv2.matchTemplate(ss, previousImage, cv2.TM_CCOEFF_NORMED)
        _, maxV, _, _ = cv2.minMaxLoc(result)
        if repeats % 10 == 0:
            logOut(maxV)

        if maxV < 0.99:
            logOut("loaded next image")
            return
        
        repeats = repeats + 1

        if repeats == 100:
            logOut("detected no change in page")
            if checkPageAndCompare():
                return

# leaving endx, y default means the mouse will return to the place it started
def getCurrentUrl(mouseReturnToStart = False):
    previousClipBoard = clipboard.paste()
    prevCords = mouse.get_position()

    moveMouse(800 + offset, 65, MOUSEDELAY) # url bar
    click()
    pressKey("ctrl+c")
    time.sleep(0.1)
    url = clipboard.paste() # gets url of current page
    logOut("got url:", url)

    if mouseReturnToStart:
        moveMouse(prevCords[0], prevCords[1], MOUSEDELAY)

    clipboard.copy(previousClipBoard)
    return url


def checkPageAndCompare():
    global saved

    logOut("compairing ids to check if page has updated")
    url = getCurrentUrl() # gets url of current page

    moveMouse(1920 / 2 + offset, 1080 / 2, MOUSEDELAY)
    click()
    pressKey("right_arrow")
    time.sleep(2) # waiting for new url

    url2 = getCurrentUrl() # gets url of current page

    moveMouse(1920 / 2 + offset, 1080 / 2, MOUSEDELAY)
    click()

    url = url.split("&")
    url2 = url2.split("&")

    id1 = ""
    id2 = ""

    for tag in url:
        if tag[:3] == "id=":
            logOut("id 1:", tag[3:])
            id1 = tag[3:]
            break
    for tag in url2:
        if tag[:3] == "id=":
            logOut("id 2:", tag[3:])
            id2 = tag[3:]
            break

    if id1 != id2:
        logOut("change detected, continuing")
        pressKey("left_arrow")
        time.sleep(2)
        return True
    else:
        if SHUTDOWN_ON_COMPLETION:
            shutdown()
        raise TimeoutError("Page timed out or reached end")
    
def startingIn(sec):
    for i in range(sec, 0, -1):
        logOut(f"Starting in {i}")
        time.sleep(1)

# this is more continue from this picture rather than page
def goToPage(currentImageNum):
    if currentImageNum < 1:
        logOut("program already starts from here")
        return
    url = getCurrentUrl()

    url = url.split("&")
    logOut(url)
    isPid = False

    for part in url:
        logOut(part[:4])

        if part[:4] == "pid=":
            isPid = True

    if not isPid:
        pressKey("end")
        keyboard.write(f"&pid={currentImageNum}")
    else:
        newUrl = ""

        for part in url:
            if part[:4] == "pid=":
                newUrl = newUrl + f"&pid={currentImageNum}"
            else:
                newUrl = newUrl + "&" + part

        newUrl = newUrl[1:] # strips off the first & -> cant be bothered fixing it
        keyboard.write(newUrl)

    pressKey("enter")
    time.sleep(2)

def getStartingIndex(path, name):
    startingIndex = 0
    #possible extensions:
    #.gif
    #.jpg
    #.jpeg
    #.png
    #.webm
    newName = name.replace(" ", "-")
    newName = newName.replace("_", "-")

    fullPath = path + "\\" + newName

    if not os.path.exists(fullPath):
        os.mkdir(fullPath)

    files = os.listdir(fullPath)
    for file in files:
        if file[-4:] == ".gif" or file[-4:] == ".jpg" or file[-4:] == ".png":# or file[-5:] == ".jpeg" or file[-5:] == ".webm":
            fileSplit = str(file).split(name + " - ")[1] # removes the name and stuff
            fileSplit = fileSplit[:-4]
            try:
                fileSplit = int(fileSplit)
            except:
                logOut("file reading broke!")
                continue
            
            if fileSplit > startingIndex:
                startingIndex = fileSplit

    if startingIndex != 0:
        startingIndex = startingIndex + 1 # adding 1 to avoid overriding first image
    return startingIndex

def createLog(logPath, nSaved, savedLeft, name, lastURL):
    fb = open(f"{logPath}\\{name}.log", "w")
    fb.write(f"savepath: {logPath}\r")
    fb.write(f"progress: {nSaved} / {savedLeft}\r")
    fb.write(f"last image page: {lastURL}\r")
    if nSaved == savedLeft:
        fb.write("finished\r")

    for text in logText:
        fb.write(str(text) + "\r")
    fb.close()
    print("created log")

def readLog(logPath):
    try:
        files = os.listdir(logPath)
    except:
        raise Exception("invalid path")
    data = []
    path = ""
    for file in files:
        if str(file).split(".")[len(str(file).split(".")) - 1] == "log":
            path = file
            break
    
    if path == "":
        return
    
    fb = open(logPath + "\\" + path, "r")
    lines = fb.readlines()
    fb.close()
    filterdLines = []
    for line in lines:
        filterdLines.append(line.replace("\n", ""))

    for i in range(0, 4):
        if i == 3:
            try:
                if filterdLines[i] == "finished":
                    data.append(True)
                else:
                    data.append(False)
            except:
                data.append(False)
            break
        if i != 1:
            data.append(str(filterdLines[i]).split(": ")[1])
        else:
            text = str(filterdLines[i]).split(": ")[1].split(" / ")
            data.append(text[0]) # current progress
            data.append(text[1]) # max progress

    return data # savepath, current progress, max progress, last page url, isFinished

def main():
    global yOffset
    global saved
    global timeElapsed

    preSnip = cv2.cvtColor(cv2.imread(f"{os.getcwd()}\\blank.jpg"), cv2.COLOR_BGR2GRAY)
    
    logOut("use the settings.json to edit perferences")
    logOut("press \"alt+q\" to stop")
    logOut("choosen screen =", SCREEN)

    keyboard.add_hotkey("alt+q", killSwitch)

    
    currentName = input("enter name: ")
    isValidName(currentName)
    amount = getAmtPagesFromUser("enter amount of images to scrape,", "-1 = infinite", f"use a surfix of p to count in pages (p2 = {IMAGES_PER_PAGE * 2} images)")

    if amount == -1:
        amount = sys.maxsize * 2 # big number !!!
    elif amount == 0:
        raise ValueError("cant scrape 0 images")
    
    if input("start from a previous scrape? [y/n]: ") == "y":
        data = readLog(getSaveImagePath(SAVEPATH, input("enter it's name")))
        if data[4]:
            logOut("that scrape already finished")
            raise SystemExit("that scrape already finished")
    elif input("start from a certain index? [y/n]: ") == "y":
        index = getNumFromUser("enter index:")
        goToPage(index)
    else:
        
        logOut("starting from the beginning")

    saved = getStartingIndex(SAVEPATH, currentName)
    amount = amount + saved
    startingIn(10)
    timeElapsed = time.time()

    #goToPage(pickUp)
    moveMouse(1920 / 2 + offset, 1080 / 2 + yOffset, MOUSEDELAY)
    mouse.wheel(800)

    # initial image select
    moveMouse(pictureX(0), pictureY(0), MOUSEDELAY)
    goIntoPic()

    while saved < amount:
        progress(saved, amount)
        if saved != 0:
            time.sleep(1) # super simple fix
            
            waitTillImageSwitched(preSnip)
            waitTillImageLoaded()

        url = getContentURL()
        saveImage(url, getSaveImagePath(SAVEPATH, currentName), currentName, saved)

        #time.sleep(0.4)
        ss = mss.mss()
        ss = np.array(ss.grab(imageLocation))
        preSnip = cv2.cvtColor(ss, cv2.COLOR_BGR2GRAY)

        if saved != amount - 1:
            moveMouse(239 + offset, 282 + yOffset + yCreditOffset, MOUSEDELAY) # clicks off to the side to deselect possible video
            click()
            pressKey("right_arrow") # next page
        saved = saved + 1
        clear()
        first = False
    progress(saved, amount)
    logOut("finished")
    logOut(f"time elapsed: {getHrMnScFromSeconds(round(time.time() - timeElapsed))}")
    createLog(getSaveImagePath(SAVEPATH, currentName), saved, amount, currentName, getCurrentUrl())

# createLog(getSaveImagePath(SAVEPATH, "logtest"), 3, 4, "logtest", "https://www.youtube.com")
# print(readLog(getSaveImagePath(SAVEPATH, "logtest")))

def noMouse():
    # video url https://video-cdn3.gelbooru.com/images/77/91/7791c17f55b740800e82d4d84b24ff94.mp4
    # image url https://img3.gelbooru.com//images/66/69/6669a75ad857faa53d5136b36f82210b.jpg
    req = requests.get("https://gelbooru.com/index.php?page=post&s=view&id=7701618&tags=reisalin_stout", stream=True)
    logOut(req)
    html = req.content.decode("utf-8")
    logOut(html)
    logOut(str(html).find("https://img3.gelbooru.com//images/66/69/6669a75ad857faa53d5136b36f82210b.jpg"))
    
    text = ""
    for i in range(0, 76):
        text = text + html[3291 + i]

    logOut(text)

#noMouse()
logOut("save path =", SAVEPATH)
logOut("\"alt + q\" to exit at anytime")
main()

if SHUTDOWN_ON_COMPLETION:
    shutdown()
print("Press enter to close...")
input()