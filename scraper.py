#import mouse
import keyboard
import time
#import mss
#import mss.tools
import numpy as np
import sys
# import cv2
# import pyperclip as clipboard
import os
import json
import requests
import shutil
import requests_html
import threading
import math

"""
    Written with and for Windows 11, Python 3.10.7
    Main Program
    
"""
yOffset = 0
saved = 0
logText = []
timeElapsed = 0
downLoaded = 0

if not os.path.exists(os.getcwd() + r"\settings.json"):
    # defaults dont touch
    DATA = {
        "amt_download_threads": 42,
        "shutdown_on_completion": False,
        "clear_console": True,
        "mp4_or_webm": "mp4",
        "save_path": "default",
        "average_file_size_mb": 2.28, # MB - from 8243 images/videos at 18756 MB
        "images_per_row": 8,
        "images_per_column": 6,
        "images_per_page": 42,
        "invalid_path_characters": ["\\", "/", ":", "*", "?", "<", ">", "|"]
    }

    json.dump(DATA, open("settings.json", "w"), indent=4)
    
else:
    DATA = json.load(open("settings.json", "r"))

AMT_DOWNLOAD_THREADS = DATA["amt_download_threads"]
SHUTDOWN_ON_COMPLETION = DATA["shutdown_on_completion"]
CLEAR_CONSOLE = DATA["clear_console"]
MP4_OR_WEBM = DATA["mp4_or_webm"]
AVERAGE_FILE_SIZE = DATA["average_file_size_mb"]
IMAGES_PER_ROW = DATA["images_per_row"]
IMAGES_PER_COLUMN = DATA["images_per_column"]
IMAGES_PER_PAGE = DATA["images_per_page"]
INVALID_PATH_CHARACTERS = DATA["invalid_path_characters"]

if DATA["save_path"] == "default":
    SAVEPATH = os.getcwd() + r"\saves"
else:
    SAVEPATH = DATA["save_path"]


def shutdown():
    os.system("shutdown /s /t 1")

def killSwitch():
    if SHUTDOWN_ON_COMPLETION:
        shutdown()
    os._exit(0)

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
    #if (str(url).find(".jpg") != -1) or (str(url).find(".jpeg") != -1):

    # sample images are always .jpg and when converting the sample image url to the full image url,
    # theres a chance that url doesnt exist. Most commonly because that the full image is a .png
    request = requests.get(url, stream = True)
    usedURL = url

    if request.status_code != 200:
        extension = str(url).split(".")
        extension = extension[len(extension) - 1]
        noExURL = url[:-len(extension) - 1]
        usedURL = noExURL + ".png"
        
        request = requests.get(noExURL + ".png", stream = True)
        if request.status_code != 200:
            request = requests.get(noExURL + ".jpeg", stream = True)
            usedURL = noExURL + ".jpeg"
            
            if request.status_code != 200:
                logOut(f"{usedURL} is an invalid url/image/video")
                return
        
    extension = usedURL.split(".")
    extension = extension[len(extension) - 1]
    shutil.copyfileobj(request.raw, open(f"{savePath}\\{name} - {nSaved}.{extension}", "wb"))

def getContentURL(HTMLSession: requests_html.HTMLSession, url):
    r = HTMLSession.get(url)
    try:
        image = r.html.find("#image", first=True) # type: ignore
        return image.attrs["src"]
    except:
        videoTag = r.html.find("#gelcomVideoPlayer", first=True) # type: ignore
        videoSources = videoTag.find("source")
        if MP4_OR_WEBM == "mp4":
            return videoSources[0].attrs["src"]
        elif MP4_OR_WEBM == "webm":
            return videoSources[1].attrs["src"]
        else:
            raise ValueError(f"\"{MP4_OR_WEBM}\" is not either \"mp4\" or \"webm\"")

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

def progress(nSaved, maxSaved):
    if nSaved > maxSaved:
        nSaved = maxSaved
    s = "DOWNLOAD PROGRESS"
    e = ""
    exit = "\"alt + q\" to exit at anytime"
    logOut(f"{s:=^100}")
    fraction = f"{nSaved} / {maxSaved}"
    precent = f"{math.floor((nSaved / maxSaved) * 100)}%"
    savepath = f"Save path: {SAVEPATH}"
    shutDown = "SHUTDOWN ON COMPLETION IS ENABLED"
    logOut(f"{fraction: ^100}")
    logOut(f"{precent: ^100}")
    logOut(f"{savepath: ^100}")
    if SHUTDOWN_ON_COMPLETION:
        logOut(f"{shutDown: ^100}")
    logOut(f"{exit: ^100}")
    logOut(f"{e:=^100}")
    
def startingIn(sec):
    for i in range(sec, 0, -1):
        logOut(f"Starting in {i}")
        time.sleep(1)

def getStartingIndex(path, name):
    startingIndex = 0
    #possible extensions:
    #.gif
    #.jpg
    #.jpeg
    #.png
    #.webm
    # newName = name.replace(" ", "-")
    # newName = newName.replace("_", "-")

    # fullPath = path + "\\" + newName

    # if not os.path.exists(fullPath):
    #     os.mkdir(fullPath)

    files = os.listdir(path)
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

# returns the links that lead to images/videos
def filterLinks(links):
    filteredLinks = []
    for link in links:      
        if (str(link).find("s=view") != -1) and (str(link).find("page=post") != -1):
            filteredLinks.append(link)

    return filteredLinks

def getFolderContentSizeFormatted(path):
    files = os.listdir(path)
    noLogFiles = []
    byteToMBRatio = (1 / 1024) / 1024 # byte -> kilobyte -> megabyte
    MBtoGBRatio = 1024
    useGiga = False

    for file in files:
        if file.find(".log") == -1:
            noLogFiles.append(f"{path}\\{file}")

    if len(noLogFiles) > downLoaded:
        noLogFiles = noLogFiles[-downLoaded:]
    
    totalByteSize = 0
    totalAmt = 0

    for file in noLogFiles:
        totalByteSize += os.path.getsize(file)
        totalAmt += 1
    
    size = totalByteSize * byteToMBRatio # bytes to megabytes

    if size > MBtoGBRatio:
        size = size / MBtoGBRatio # megabyte to gigabyte
        useGiga = True

    text = ""
    if useGiga:
        text = f"{round(size, 2)} GB"
    else:
        text = f"{round(size, 2)} MB"
    return text

def createLog(logPath, nSaved, name, startingURL):
    logFile = f"{logPath}\\{name}.log"

    i = 1
    while os.path.exists(logFile):
        logFile = f"{logPath}\\{name}{i}.log"
        i += 1

    fb = open(logFile, "w")
    fb.write(f"savepath: {logPath}\r")
    fb.write(f"pages downloaded: {round(nSaved / 42, 2)}\r")
    fb.write(f"files downloaded: {nSaved}\r")
    fb.write(f"size of download: {getFolderContentSizeFormatted(logPath)}\r")
    fb.write(f"starting page: {startingURL}\r\r")

    for text in logText:
        fb.write(str(text) + "\r")
    fb.close()
    print("created log")

def readLog(logPath): # pretty much useless
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

def addIndexToUrl(url: str, page):
    result = url.find("&pid=")
    if result == -1:
        return f"{url}&pid={IMAGES_PER_PAGE * page}"
    else:
        id = int(url[result + 5:])
        newUrl = url[:result]
        return f"{newUrl}&pid={id + IMAGES_PER_PAGE * page}"

def compileLinks(HTMLSession: requests_html.HTMLSession, startingUrl, nPages):
    result = []
    for i in range(0, nPages):
        clear()
        logOut(f"Compiling images on pages ... [{i + 1} / {nPages}]")
        r = HTMLSession.get(addIndexToUrl(startingUrl, i))
        links = r.html.absolute_links # type: ignore
        links = filterLinks(links) # gets rid of junk links
        result.extend(links)

    logOut(f"Got {len(result)} image/video links")
    return result

def extractImageURLsFromPages(HTMLSession: requests_html.HTMLSession, links):
    imageURLs = []
    length = len(links)
    for i in range(0, length):
        clear()
        logOut(f"Extracting image urls from links ... [{i + 1} / {length}]")
        url = getContentURL(HTMLSession, links[i])
        url = str(url).replace("sample_", "").replace("/samples", "/images") # by default the images are only samples, this gets the hd one
        imageURLs.append(url)

    return imageURLs

# 
def downloadThread(links: list, savePath: str, name: str, fileNums: list):
    global downLoaded

    if len(links) != len(fileNums):
        raise Exception("The amount of links given does equal the amount of file numbers given")
    
    for i in range(0, len(links)):
        saveImage(links[i], savePath, name, fileNums[i])
        downLoaded += 1

def getAndSaveImagesFromLinks(links, savePath, name):
    # for i in range(0, len(links)): # TODO add threading to this to make it faster
    #     saveImage(links[i], savePath, name, i)

    logOut("Spliting load over multiple threads")
    separatedLoad = np.array_split(np.array(links), AMT_DOWNLOAD_THREADS) # splits up load "equally" for every thread
    downloadThreads = []

    previousIndex = getStartingIndex(savePath, name) # incase dictory already has saves

    logOut("Initalizing download threads")
    startingIndex = 0 + previousIndex # for thread file numbers
    for i in range(0, AMT_DOWNLOAD_THREADS): # initalizing threads
        fileNums = []
        for j in range(0, len(separatedLoad[i])):
            fileNums.append(startingIndex)
            startingIndex += 1

        thread = threading.Thread(target=downloadThread, args=(separatedLoad[i], savePath, name, fileNums,))
        downloadThreads.append(thread)

    logOut("Starting download threads")
    for thread in downloadThreads:
        thread.start()

    before = 0
    clear()
    while threading.active_count() > 3:
        if downLoaded != before:
            before = downLoaded
            clear()
            progress(downLoaded, len(links))

    logOut("Finished downloading")



def main():
    global yOffset
    global saved
    global timeElapsed
    
    logOut("Use the settings.json to edit perferences")
    logOut("Press \"alt+q\" to stop")

    keyboard.add_hotkey("alt+q", killSwitch)

    
    currentName = input("Enter name: ")
    isValidName(currentName)
    startingUrl = input("Enter starting url: ")
    amount = getNumFromUser(f"Enter number of pages to scrape [1 = {IMAGES_PER_PAGE} file]:")
    clear()
    logOut("Estimated amount of files:", IMAGES_PER_PAGE * amount)
    logOut("Estimated download size:", round(IMAGES_PER_PAGE * amount * AVERAGE_FILE_SIZE, 2), "MB")
    logOut("Estimated time to scrape:", getHrMnScFromSeconds(amount * 26))

    input("Press enter to confirm: ")

    #startingIn(2)
    timeElapsed = time.time()
    logOut("starting html session")
    session = requests_html.HTMLSession()
    logOut("created")

    links = compileLinks(session, startingUrl, amount)
    links = extractImageURLsFromPages(session, links)
    getAndSaveImagesFromLinks(links, getSaveImagePath(SAVEPATH, currentName), currentName)

    logOut("finished")
    logOut(f"time elapsed: {getHrMnScFromSeconds(round(time.time() - timeElapsed))}")
    createLog(getSaveImagePath(SAVEPATH, currentName), downLoaded, currentName, startingUrl)

logOut("save path =", SAVEPATH)
logOut("\"alt + q\" to exit at anytime")
main()

if SHUTDOWN_ON_COMPLETION:
    shutdown()
print("Press enter to close...")
input()