"""
    Written with and for Windows 11, Python 3.10.7
    Used for calibrating download size estimate in scraper
"""

import os
import json

if input("calibrate average size? [y/n]: ").lower() != "y":
    os._exit(0)

if not os.path.exists("settings.json"):
    print("settings.json not found")
    input("Press enter to close: ")
    os._exit(0)


data = json.load(open("settings.json", "r"))

if data["save_path"] == "default":
    path = os.getcwd() + r"\saves"
else:
    path = data["save_path"]

folders = os.listdir(path)
allFiles = []
byteToMBRatio = (1 / 1024) / 1024

for i in range(0, len(folders)):
    files = os.listdir(path + "\\" + folders[i])

    noLogs = []

    for file in files:
        if file.find(".log") == -1: # filters log files
            noLogs.append(f"{path}\\{folders[i]}\\{file}")

    allFiles.append(noLogs)

print(len(allFiles), "folders")

totalByteSize = 0
totalAmt = 0

for folder in allFiles:
    for file in folder:
        totalByteSize += os.path.getsize(file)
        totalAmt += 1

averSize = round((totalByteSize / totalAmt) * byteToMBRatio, 2)

data["average_file_size_mb"] = averSize

json.dump(data, open("settings.json", "w"), indent=4)

print("total megabytes:", round(totalByteSize * byteToMBRatio, 2), "MB")
print("average size:", averSize, "MB")
print("amount of files:", totalAmt)