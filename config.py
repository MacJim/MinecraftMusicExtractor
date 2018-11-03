# Minecraft Music Extractor configuration.


# 1. ".minecraft" (or "minecraft" on macOS) folder path.
# If `None` or an empty string, will use the default Minecraft path.
minecraftFolderPath = None


# 2. Music and sound effects export folder path.
# If `None` or an empty string, all music and sound effects will be saved in the same folder of "main.py".
exportFolderPath = None


# 3. Overwrite existing files when exporting.
# If `True`, this script will overwrite files at the destination folder.
# Note: This script will NOT overwrite directories regardless of this value.
shouldOverrideExistingFiles = False


# 4. Minecraft assets index version.
# If `None` or an empty string, this script will attempt to locate and extract music and sound effects from the LATEST Minecraft version on your computer.
assetsIndexVersion = None
# assetsIndexVersion = "1.12"