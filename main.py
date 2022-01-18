import distutils.version
import json
import os
import platform
import shutil

import config


# MARK: Helper functions
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
        import sys
        import termios
        import tty

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
os_platform = platform.system()  # Linux, Darwin or Windows

# 2. Obtain ".minecraft" folder path.
minecraft_folder_path = config.minecraft_folder_path
indexes_folder_path = ""
objects_folder_path = ""

# 2-1. Find default ".minecraft" folder path.
if not minecraft_folder_path:
    if os_platform == "Windows":
        appdata_path = os.getenv("APPDATA")
        minecraft_folder_path = os.path.join(appdata_path, ".minecraft")
    else:
        home_directory_path = os.path.expanduser("~")
        if os_platform == "Darwin":
            minecraft_folder_path = os.path.join(
                home_directory_path, "Library/Application Support/minecraft"
            )  # No dot on macOS.
        elif os_platform == "Linux":
            minecraft_folder_path = os.path.join(home_directory_path, ".minecraft")

# 2-2. Check that the default ".minecraft" folder and its "assets/indexes" & "assets/objects" sub-folders exist.
if os.path.isdir(minecraft_folder_path):
    print(f"Minecraft folder: {minecraft_folder_path}")

    indexes_folder_path = os.path.join(minecraft_folder_path, "assets/indexes")
    objects_folder_path = os.path.join(minecraft_folder_path, "assets/objects")

    if os.path.isdir(indexes_folder_path):
        print(f"Indexes folder: {indexes_folder_path}")
    else:
        print("Indexes folder not found!")
        print("Please run Minecraft at least once before running this script!")
        exit(1)

    if os.path.isdir(objects_folder_path):
        print(f"Objects folder: {objects_folder_path}")
    else:
        print("Objects folder not found!")
        print("Please run Minecraft at least once before running this script!")
        exit(1)

else:
    print('Minecraft game folder not found, please enter its path manually in "config.py".')
    exit(1)

# 3. Obtain export folder path.
export_folder_path = config.export_folder_path
if not export_folder_path:
    export_folder_path = os.path.dirname(os.path.abspath(__file__))

# 4. Parse "assets/indexes/1.x.json" file
assets_index_version = config.assets_index_version
if not assets_index_version:
    # 4-1. Attempt to find the LATEST Minecraft asset version.
    all_versions = []

    all_filenames_in_indexes_folder = os.listdir(indexes_folder_path)
    for filename in all_filenames_in_indexes_folder:
        if filename.endswith(".json"):
            all_versions.append(filename[0:-5])

    if not all_versions:
        print("No asset index found!")
        print("Please run Minecraft at least once before running this script!")
        exit(1)
    else:
        assets_index_version = all_versions[0]
        for current_version in all_versions:
            if distutils.version.LooseVersion(assets_index_version) < distutils.version.LooseVersion(current_version):
                assets_index_version = current_version
        print(f"Latest assets index: {assets_index_version}")

# 4-2. Make sure that the index file exists.
assets_index_file_path = os.path.join(indexes_folder_path, assets_index_version + ".json")
if not os.path.isfile(assets_index_file_path):
    print(f"Cannot open asset index file: {assets_index_file_path}")
    print('Please enter its path manually in "config.py".')
    exit(1)

# 5. Open assets index json file.
with open(assets_index_file_path) as f:
    assets_index = json.load(f)
    assets_index = assets_index["objects"]  # Don't forget this top-layered "object" key.


# MARK: Main program
# 1. Get user input.
print("\n1. Extract music only.")
print("2. Extract music & sound effects.")
print("0. Exit")
print("Press a key to select an option above.")

while True:
    # Wait for a legal user input.
    user_input = getch()
    if user_input == "0":
        exit(0)
    elif (user_input == "1") or (user_input == "2"):
        break
    else:
        continue

# 2. Filter items to export.
if user_input == "1":
    crude_assets_information = {k: v for k, v in assets_index.items() if k.startswith("minecraft/sounds/music/")}
elif user_input == "2":
    crude_assets_information = {k: v for k, v in assets_index.items() if k.startswith("minecraft/sounds/")}

# 3. Calculate hashed paths and export paths.
processed_assets_information = []
for k, v in crude_assets_information.items():
    asset_export_path = os.path.join(export_folder_path, k)

    asset_hashed_name = v["hash"]
    asset_hashed_folder = asset_hashed_name[0:2]
    asset_hashed_path = os.path.join(objects_folder_path, asset_hashed_folder, asset_hashed_name)

    processed_assets_information.append({"exportPath": asset_export_path, "hashedPath": asset_hashed_path})

# 4. Copy files
successful_copies = []
# An IOError happened on this file. This might be caused by insufficient permission.
failed_copies = []
# A file or directory exists at the export path.
omitted_copies = []

for file_info in processed_assets_information:
    export_path = file_info["exportPath"]
    hashed_path = file_info["hashedPath"]

    # 4-1. If a directory (not file) exists at `exportPath`, abort.
    if os.path.isdir(export_path):
        omitted_copies.append(file_info)
        continue

    # 4-2. Copy files.
    if (not os.path.isfile(export_path)) or config.should_overwrite_existing_files:
        try:
            # 4-3. Create the export directory if it does not exist.
            if not os.path.isdir(os.path.dirname(export_path)):
                os.makedirs(os.path.dirname(export_path))

            shutil.copyfile(hashed_path, export_path)
            successful_copies.append(file_info)
        except:
            failed_copies.append(file_info)
    else:
        omitted_copies.append(file_info)

# 5. Show summary.
print("\nCopy summary:")
print(f"Successful copies: {len(successful_copies)}")
print(f"Failed copies: {len(failed_copies)}")
print(f"Omitted copies: {len(omitted_copies)}")

if failed_copies:
    print("Errors occurred when copying files:")
    for i, failed_copy in enumerate(failed_copies):
        print(f"{i + 1}. Source: {failed_copy['hashedPath']}, Destination: {failed_copy['exportPath']}")
