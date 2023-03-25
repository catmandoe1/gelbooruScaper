import mouse
import keyboard
import time
import mss
import mss.tools
import numpy as np
import sys
import math
import cv2
import pyperclip as clipboard

SCREEN = 1 # 1 OR 2 (assuming 1920x1080 HD)

if SCREEN == 1:
    offset = 0
else:
    offset = SCREEN * 1920

MOUSEDELAY = 0.1
MAX_IMAGE_WIDTH = 175
MAX_IMAGE_HEIGHT = 175
IMAGES_PER_ROW = 8
IMAGES_PER_COLUMN = 6
SAVEPATH = "C:/Programs/visual_studio_code/Python/gelbooruScaper/saves"

# imageLocation = {
#     "top": 343,
#     "left": 262 + offset,
#     "width": 1,
#     "height": 3
# }

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
    #moveMouse(10, 10) #moves cursur out of the way - nvm

    while True:
        ss = mss.mss()
        area = np.array(ss.grab(imageLocation))
        sum = area.sum()
        #cv2.imshow("imggg", area)
        #cv2.waitKey()
        if sum != 394367520 and sum != preSum: # the number is equal to the sum of defualt background, when the image loads it changes
            print("image loaded")
            break
    
    

def checkIfPic(y, i):
    location = {
    "top": 384 + (y % 3) * 206,
    "left": (337 + i * 195) + offset,
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

def getNumFromUser(message):
    while True:
        try:
            x = int(input(message))
            return x
        except:
            print("invalid number")

def nextPage(page):
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
    

def main():

    preSnip = cv2.cvtColor(cv2.imread("C:/Programs/visual_studio_code/Python/gelbooruScaper/blank.jpg"), cv2.COLOR_BGR2GRAY)
    

    print("MAKE SURE URL DOESNT HAVE &pid=[x] IN IT")
    print("press \"alt+q\" to stop")
    print("choosen screen =", SCREEN)

    keyboard.add_hotkey("alt+q", killSwitch)

    saved = 0
    currentName = input("enter name: ")
    amount = getNumFromUser("enter amount of images to scrape (-1 = infinite): ")

    if amount >= 0:
        pages = math.ceil(amount / (IMAGES_PER_ROW * IMAGES_PER_COLUMN))
    else:
        pages = sys.maxsize * 2 + 1 # big number !!!

    moveMouse(1920 / 2, 1080 / 2, MOUSEDELAY)
    mouse.wheel(800)
    addMinusVideoTag()
    

    if pages == 0:
        raise Exception("cant scrape 0 pages")

    for page in range(0, pages):
        for y in range(0, IMAGES_PER_COLUMN):
            if y == 3:
                time.sleep(1)
                mouse.wheel(-200)
                time.sleep(1)

            for i in range(0, IMAGES_PER_ROW):

                if y == 5 and i == 2:
                    break # last picture normally

                if saved >= amount:
                    killSwitch()

                # seeing if page has changed/loaded
                while True:
                    ss = mss.mss()
                    ss = np.array(ss.grab(pageContentLocation))
                    
                    ss = cv2.cvtColor(ss, cv2.COLOR_BGR2GRAY)
                    #cv2.imshow("ss", ss)
                    #cv2.imshow("pre", preSnip)
                    cv2.waitKey()

                    result = cv2.matchTemplate(ss, preSnip, cv2.TM_CCORR_NORMED)
                    _, max, _, _ = cv2.minMaxLoc(result)
                    print("max:", max)

                    if max < 0.90:
                        cv2.imwrite(f"C:/Programs/visual_studio_code/Python/gelbooruScaper/debug_out/loadedSnip-{y}{i}.jpg", ss)
                        print("page loaded")
                        break

                moveMouse((337 + i * 195) + offset, 384 + (y % 3) * 206, MOUSEDELAY) # hover on the pic
                print(f"current location x:{(337 + i * 195) + offset} y:{384 + (y % 3) * 206}")
                
                checkIfPic(y, i)

                goIntoPic()

                openSaveMenu()

                if y == 0 and i == 0:
                    saveImage(SAVEPATH, saved, currentName, True)
                saveImage(SAVEPATH, saved, currentName)
                saved = saved + 1
                
                time.sleep(0.5) # allows for the save window to close in time
                # used for checking if page as changed
                ss = mss.mss()
                ss = np.array(ss.grab(pageContentLocation))
                preSnip = cv2.cvtColor(ss, cv2.COLOR_BGR2GRAY)
                cv2.imwrite(f"C:/Programs/visual_studio_code/Python/gelbooruScaper/debug_out/preSnip-{y}{i}.jpg", ss)
                pressKey("alt+left_arrow")

                
        nextPage(page + 1) # TODO FIX
main()

# moveMouse(800 + offset, 65, MOUSEDELAY) # url bar
# click()
# pressKey("ctrl+c")
# time.sleep(0.1)

# print(clipboard.paste())
#clipboard.copy("hello!")
#print(clipboard.paste())

# img = np.array(cv2.imread("C:/Programs/visual_studio_code/Python/gelbooruScaper/debug_out/preSnip-30.jpg"))
# img2 = np.array(cv2.imread("C:/Programs/visual_studio_code/Python/gelbooruScaper/debug_out/loadedSnip-30.jpg"))

# print(img.sum(), img2.sum())

# if img.sum() == img2.sum():
#     print("img = img2")
# else:
#     print("img != img2")

# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

# result = cv2.matchTemplate(img, img2, cv2.TM_CCORR_NORMED)
# cv2.imshow("igmgg", result)
# cv2.waitKey()

# min, max, minLoc, maxLoc = cv2.minMaxLoc(result)

# print(min, max, minLoc, maxLoc)