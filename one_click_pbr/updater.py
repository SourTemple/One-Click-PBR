# one_click_pbr/updater.py

import bpy
import urllib.request
from .. import bl_info # Import bl_info from the main __init__.py

# !!! IMPORTANT !!!
# Replace this with the RAW URL to your version file on GitHub
VERSION_URL = "https://raw.githubusercontent.com/SourTemple/One-Click-PBR/main/version.txt"
RELEASES_URL = "https://github.com/SourTemple/One-Click-PBR/releases"

class OCP_OT_check_for_updates(bpy.types.Operator):
    """Checks for a new version of the addon online"""
    bl_idname = "ocp.check_for_updates"
    bl_label = "Check for Updates"

    def execute(self, context):
        try:
            with urllib.request.urlopen(VERSION_URL, timeout=5) as response:
                online_version_str = response.read().decode('utf-8').strip()
                online_version = tuple(map(int, online_version_str.split('.')))
                
                local_version = bl_info.get('version', (0, 0, 0))

                if online_version > local_version:
                    self.report({'INFO'}, f"A new version is available: {online_version_str}")
                    # Open the releases page in the user's web browser
                    bpy.ops.wm.url_open(url=RELEASES_URL)
                else:
                    self.report({'INFO'}, "One-Click PBR is up to date.")

        except Exception as e:
            self.report({'ERROR'}, f"Could not check for updates: {e}")

        return {'FINISHED'}