# bump_version.py
import re
import os

# --- CONFIGURATION ---
ADDON_FOLDER = "one_click_pbr"
VERSION_FILE = "version.txt"
INIT_FILE = os.path.join(ADDON_FOLDER, "__init__.py")

# Read the current version from version.txt
with open(VERSION_FILE, "r") as f:
    major, minor, patch = map(int, f.read().strip().split('.'))

# Increment the patch number
patch += 1

new_version_str = f"{major}.{minor}.{patch}"
print(f"Bumping version to: {new_version_str}")

# Write the new version back to version.txt
with open(VERSION_FILE, "w") as f:
    f.write(new_version_str)

# Update the bl_info in __init__.py using regex
with open(INIT_FILE, "r") as f:
    init_content = f.read()

new_init_content = re.sub(
    r'("version": \()\d+, \d+, \d+(\),)',
    f'\\1{major}, {minor}, {patch}\\2',
    init_content
)

with open(INIT_FILE, "w") as f:
    f.write(new_init_content)

print("Addon version updated successfully.")