import platform
import os
import sys
import distutils.version
import json
import shutil

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
    assetsIndex = assetsIndex["objects"]    # Don't forget this top-layered "object" key.


# MARK: Main program
# 1. Get user input.
print("\n1. Extract music only.")
print("2. Extract music & sound effects.")
print("0. Exit")
print("Press a key to select an option above.")

while(True):
    # Wait for a legal user input.
    userInput = getch()
    if (userInput == "0"):
        exit(0)
    elif ((userInput == "1") or (userInput == "2")):
        break
    else:
        continue

# 2. Filter items to export.
crudeAssetsInformation = {}
if (userInput == "1"):
    for aKey, aValue in assetsIndex.items():
        if (aKey.startswith("minecraft/sounds/music/")):
            crudeAssetsInformation[aKey] = aValue
elif (userInput == "2"):
    for aKey, aValue in assetsIndex.items():
        if (aKey.startswith("minecraft/sounds/")):
            crudeAssetsInformation[aKey] = aValue

# 3. Calculate hashed path and export path.
processedAssetsInformation = []
for aKey, aValue in crudeAssetsInformation.items():
    assetExportPath = os.path.join(exportFolderPath, aKey)

    assetHashedName = aValue["hash"]
    assetHashedFolder = assetHashedName[0:2]
    assetHashedPath = os.path.join(objectsFolderPath, assetHashedFolder, assetHashedName)

    processedAssetsInformation.append({
        "exportPath": assetExportPath,
        "hashedPath": assetHashedPath
    })

# 4. Copy files
successfulCopies = []
# An IOError happened on this file. This might be caused by insufficient permission.
failedCopies = []
# A file or directory exists at the export path.
omittedCopies = []

for aFileToCopy in processedAssetsInformation:
    exportPath = aFileToCopy["exportPath"]
    hashedPath = aFileToCopy["hashedPath"]

    # 4-1. If a directory (not file) exists at `exportPath`, abort.
    if (os.path.isdir(exportPath)):
        omittedCopies.append(aFileToCopy)
        continue

    # 4-2. Copy files.
    if ((not os.path.isfile(exportPath)) or (config.shouldOverrideExistingFile)):
        try:
            # 4-3. Create the export directory if it does not exist.
            if (not os.path.isdir(os.path.dirname(exportPath))):
                os.makedirs(os.path.dirname(exportPath))

            shutil.copyfile(hashedPath, exportPath)
            successfulCopies.append(aFileToCopy)
        except:
            failedCopies.append(aFileToCopy)
    else:
        omittedCopies.append(aFileToCopy)

# 5. Show summary.
print("\nCopy summary:")
print("Successful copies:", len(successfulCopies))
print("Failed copies:", len(failedCopies))
print("Omitted copies:", len(omittedCopies))

if (len(failedCopies) > 0):
    print("Errors occurred when copying certain files.")
    print("This might be caused by insufficient file permissions.")
    print("Press any key to view them.")

    sys.stdout.flush()
    getch()

    print("Failed copies:")
    for i in range(len(failedCopies)):
        print(i)
        print("Source:", failedCopies[i]["hashedPath"])
        print("Destination:", failedCopies[i]["exportPath"])