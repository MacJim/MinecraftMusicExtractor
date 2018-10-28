import platform
import os
import sys
import distutils.version


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
print("Please run Minecraft at least once before running this script.")


# MARK: Preparations.
# 1. Get system platform.
systemPlatform = platform.system()    # Linux, Darwin or Windows

# 2. Try to obtain ".minecraft" folder path automatically.
minecraftFolderPath = ""
indexesFolderPath = ""
objectsFolderPath = ""

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
shouldEnterMinecraftFolderManually = False
while True:
    if (os.path.isdir(minecraftFolderPath)):
        indexesFolderPath = os.path.join(minecraftFolderPath, "assets/indexes")
        objectsFolderPath = os.path.join(minecraftFolderPath, "assets/objects")

        if ((not os.path.isdir(indexesFolderPath)) or (not os.path.isdir(objectsFolderPath))):
            shouldEnterMinecraftFolderManually = True
    else:
        shouldEnterMinecraftFolderManually = True

    if (shouldEnterMinecraftFolderManually):
        minecraftFolderPath = input("Unable to find your minecraft folder, please enter its path manually: ")
    else:
        print("Minecraft folder found:", minecraftFolderPath)
        break

# TODO: 3. Parse "assets/indexes/1.x.json" file
allVersions = []
distutils.version.LooseVersion


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