# one_click_pbr/panel.py

import bpy
from .operator import MATERIAL_OT_one_click_pbr

class SHADER_PT_one_click_pbr_panel(bpy.types.Panel):
    bl_label = "One-Click PBR"
    bl_idname = "SHADER_PT_one_click_pbr"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "One-Click PBR"
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.ocp_settings
        
        main_box = layout.box()
        col = main_box.column(align=True)

        op1 = col.operator(MATERIAL_OT_one_click_pbr.bl_idname, text="Create Material", icon='MATERIAL')
        op1.mark_as_asset = False; op1.overwrite_material = False
        
        op2 = col.operator(MATERIAL_OT_one_click_pbr.bl_idname, text="Create & Mark as Asset", icon='ASSET_MANAGER')
        op2.mark_as_asset = True; op2.overwrite_material = False

        op3 = col.operator(MATERIAL_OT_one_click_pbr.bl_idname, text="Overwrite Current", icon='FILE_REFRESH')
        op3.mark_as_asset = False; op3.overwrite_material = True

        # --- Packed Texture Workflow Settings ---
        pack_box = layout.box()
        pack_box.label(text="Packed Texture Workflow")
        pack_box.prop(settings, "packed_workflow", text="")

        # --- Collapsible Selective Mode Menu ---
        selective_box = layout.box()
        row = selective_box.row()
        
        icon = "TRIA_DOWN" if settings.show_selective_mode else "TRIA_RIGHT"
        row.prop(settings, "show_selective_mode", icon=icon, text="Selective Mode", emboss=False)
        
        if settings.show_selective_mode:
            grid = selective_box.grid_flow(row_major=True, columns=2, align=True)
            grid.prop(settings, "use_diffuse")
            grid.prop(settings, "use_metallic")
            grid.prop(settings, "use_roughness")
            grid.prop(settings, "use_normal_map")
            grid.prop(settings, "use_bump_map")
            grid.prop(settings, "use_displacement")
            grid.prop(settings, "use_ao")
            grid.prop(settings, "use_cavity")
            grid.prop(settings, "use_alpha")
            grid.prop(settings, "use_specular")
            grid.prop(settings, "use_sss")
            grid.prop(settings, "use_transmission")
            grid.prop(settings, "use_coat")