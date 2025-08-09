# one_click_pbr/__init__.py
# Main entry point for the addon.

bl_info = {
    "name": "One-Click PBR",
    "author": "You & Your AI Vibe Coder",
    "version": (7, 0),
    "blender": (3, 0, 0),
    "location": "Shader Editor > Sidebar (N Panel) > One-Click PBR",
    "description": "Intelligently finds and connects a full PBR texture set to a new material.",
    "category": "Material",
}

# This section handles reloading the addon properly during development
if "bpy" in locals():
    import importlib
    if "utils" in locals():
        importlib.reload(utils)
    if "properties" in locals():
        importlib.reload(properties)
    if "operator" in locals():
        importlib.reload(operator)
    if "panel" in locals():
        importlib.reload(panel)
    if "updater" in locals():
        importlib.reload(updater)

import bpy
from . import utils, properties, operator, panel
from . import updater

classes_to_register = (
    properties.OCP_Settings,
    operator.MATERIAL_OT_one_click_pbr,
    panel.SHADER_PT_one_click_pbr_panel,
    updater.OCP_OT_check_for_updates,
)

def register():
    for cls in classes_to_register:
        bpy.utils.register_class(cls)
    # Add the settings property group to the scene
    bpy.types.Scene.ocp_settings = bpy.props.PointerProperty(type=properties.OCP_Settings)

def unregister():
    # Delete the settings property group from the scene
    del bpy.types.Scene.ocp_settings
    for cls in reversed(classes_to_register):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
