import mouse
import keyboard
import time

mouseDelay = 0.1

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
    
def saveImage(savePath, first = False):
    if first:
        moveMouse(620, 55, mouseDelay)
        click()
        keyboard.write(savePath)
        moveMouse(780, 506, mouseDelay)
        click()
    else:
        moveMouse(780, 506, mouseDelay)
        click()

def openSaveMenu():
    click("right")
    time.sleep(0.1)
    pressKey("v")
    time.sleep(0.25)

def main():
    imgsPerRow = 8
    imgsPerColumn = 6
    savePath = "C:/Programs/visual_studio_code/Python/gelbooruScapper/saves"

    for y in range(0, imgsPerColumn):
        if y == 3:
            mouse.wheel(-200)
            time.sleep(0.4)

        for i in range(0, imgsPerRow):

            if y == 5 and i == 2:
                break # last picture normally

            moveMouse(330 + i * 200, 350 + (y % 3) * 200, mouseDelay) # hover on the pic

            openSaveMenu()

            saveImage(savePath)
main()