import platform
import os
import sys
import distutils.version
import json

import config


# MARK: Helper functions.
def getch():
    """Get a single character from user input. The user is not required to press ENTER.
    Source (many thanks): https://stackoverflow.com/questions/510357/python-read-a-single-character-from-the-user
    """
    try:
        # Only works on Windows.
        import msvcrt
        return msvcrt.getch().decode("ASCII")

    except ModuleNotFoundError:
        # Works on UNIX.
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


# MARK: User instructions.
print("Minecraft Music Extractor by MacJim")
print("This script extracts music & sound effects from your local Minecraft game folder.")
print("For more information on your Minecraft game folder, please refer to this wiki page:")
print("https://minecraft.gamepedia.com/.minecraft")
print("Please run Minecraft at least once before running this script.\n")


# MARK: Preparations.
# 1. Get system platform.
systemPlatform = platform.system()    # Linux, Darwin or Windows

# 2. Obtain ".minecraft" folder path.
minecraftFolderPath = config.minecraftFolderPath
indexesFolderPath = ""
objectsFolderPath = ""

if ((minecraftFolderPath is None) or (minecraftFolderPath == "")):
    # 2-1. Default ".minecraft" folder path.
    if (systemPlatform == "Windows"):
        appdataPath = os.getenv("APPDATA")
        minecraftFolderPath = os.path.join(appdataPath, ".minecraft")
    else:
        homeDirectoryPath = os.path.expanduser("~")
        if (systemPlatform == "Darwin"):
            minecraftFolderPath = os.path.join(homeDirectoryPath, "Library/Application Support/minecraft")    # No dot on macOS.
        elif (systemPlatform == "Linux"):
            minecraftFolderPath = os.path.join(homeDirectoryPath, ".minecraft")

# 2-2. Makes sure that the default ".minecraft" folder and its "assets/indexes" & "assets/objects" subfolders exist.
if (os.path.isdir(minecraftFolderPath)):
    print("Minecraft folder found:", minecraftFolderPath)

    indexesFolderPath = os.path.join(minecraftFolderPath, "assets/indexes")
    objectsFolderPath = os.path.join(minecraftFolderPath, "assets/objects")

    if (os.path.isdir(indexesFolderPath)):
        print("Indexes folder found:", indexesFolderPath)
    else:
        print("Indexes folder not found!")
        print("Please run Minecraft at least once before running this script!")
        exit(1)

    if (os.path.isdir(objectsFolderPath)):
        print("Objects folder found:", objectsFolderPath)
    else:
        print("Objects folder not found!")
        print("Please run Minecraft at least once before running this script!")
        exit(1)

else:
    print("Minecraft game folder not found, please enter its path manually in \"config.py\".")
    exit(1)

# 3. Obtain export folder path.
exportFolderPath = config.exportFolderPath
if ((exportFolderPath is None) or (exportFolderPath == "")):
    exportFolderPath = os.path.dirname(os.path.abspath(__file__))

# 4. Parse "assets/indexes/1.x.json" file
assetsIndexVersion = config.assetsIndexVersion
if ((assetsIndexVersion is None) or (assetsIndexVersion == "")):
    # 4-1. Attempt to find the LATEST Minecraft asset version.
    allVersions = []

    allFilenamesInIndexesFolder = os.listdir(indexesFolderPath)
    for aFilename in allFilenamesInIndexesFolder:
        if (aFilename.endswith(".json")):
            allVersions.append(aFilename[0:-5])

    if (len(allVersions) <= 0):
        print("No asset index found!")
        print("Please run Minecraft at least once before running this script!")
        exit(1)
    else:
        assetsIndexVersion = allVersions[1]
        for currentVersion in allVersions:
            if (distutils.version.LooseVersion(assetsIndexVersion) < distutils.version.LooseVersion(currentVersion)):
                assetsIndexVersion = currentVersion
        print("Latest assets index found:", assetsIndexVersion)

# 4-2. Make sure that the index file exists.
assetsIndexFilePath = os.path.join(indexesFolderPath, assetsIndexVersion + ".json")
if (not os.path.isfile(assetsIndexFilePath)):
    print("Cannot open asset index file:", assetsIndexFilePath)
    print("Please enter its path manually in \"config.py\".")
    exit(1)

# 5. Open assets index json file.
with open(assetsIndexFilePath) as assetsIndexFileData:
    assetsIndex = json.load(assetsIndexFileData)


# MARK: Main program
print("1. Extract music only.")
print("2. Extract sound effects only.")
print("3. Extract music & sound effects.")
print("0. Exit")
print("Press a key to select an option above.")

while(True):
    # Wait for a legal user input.
    userInput = getch()
    if ((userInput == "0") or (userInput == "1") or (userInput == "2") or (userInput == "3")):
        break
    else:
        continue