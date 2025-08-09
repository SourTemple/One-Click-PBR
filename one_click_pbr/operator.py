# one_click_pbr/operator.py

import bpy
import os
from .utils import find_texture_by_keywords, resolve_conflict, get_base_name_from_file

class MATERIAL_OT_one_click_pbr(bpy.types.Operator):
    bl_idname = "material.one_click_pbr"
    bl_label = "One-Click PBR Operator"
    bl_description = "Finds textures and builds a material"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    mark_as_asset: bpy.props.BoolProperty(default=False)
    overwrite_material: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        active_obj = context.active_object
        if not active_obj: self.report({'ERROR'}, "Please select an object."); return {'CANCELLED'}
        directory = os.path.dirname(self.filepath)
        settings = context.scene.ocp_settings

        all_files_in_dir = os.listdir(directory)
        diffuse_keywords = ['basecolor', 'base color', 'diffuse', 'diff', 'color', 'col', 'albedo', 'alb']
        potential_diffuse_maps = find_texture_by_keywords(directory, all_files_in_dir, diffuse_keywords)
        unique_sets = {get_base_name_from_file(os.path.basename(d_map), diffuse_keywords) for d_map in potential_diffuse_maps}

        if len(unique_sets) > 1:
            object_name_base = active_obj.name.split('.')[0].lower()
            available_files = [f for f in all_files_in_dir if object_name_base in f.lower()]
        else:
            available_files = all_files_in_dir

        full_search_order = [('specular_color', ['specular color', 'spec color', 'specular tint'], 'use_specular'), ('sss_radius', ['scattering radius', 'scatter radius', 'scattering color', 'scatter color', 'sss color', 'sss radius', 'radius'], 'use_sss'), ('sss', ['scattering', 'scatter', 'sss'], 'use_sss'), ('normal', ['normal map', 'normal', 'opengl', 'nrm'], 'use_normal_map'), ('displacement', ['disp', 'displacement', 'height', 'depth'], 'use_displacement'), ('bump', ['bump', 'bump map', 'bmp'], 'use_bump_map'), ('gloss', ['gloss', 'glossy', 'glossiness'], 'use_roughness'), ('metallic', ['metallic', 'metal', 'metalness'], 'use_metallic'), ('specular', ['specular', 'spec'], 'use_specular'), ('roughness', ['roughness', 'rough'], 'use_roughness'), ('ao', ['ao', 'ambient', 'occlusion', 'ambient occlusion'], 'use_ao'), ('cavity', ['cavity'], 'use_cavity'), ('alpha', ['alpha', 'opacity', 'mask'], 'use_alpha'), ('transmission', ['transmission', 'trans'], 'use_transmission'), ('coat', ['coat'], 'use_coat'), ('diffuse', ['basecolor', 'base color', 'diffuse', 'diff', 'color', 'col', 'albedo', 'alb'], 'use_diffuse')]
        search_order = [(map_type, keywords) for map_type, keywords, setting in full_search_order if not settings.show_selective_mode or getattr(settings, setting)]
        
        claimed_files, final_paths = set(), {}
        packed_channels_found = set()
        packed_texture_path = None

        # --- Packed Texture Priority Investigation ---
        if settings.packed_workflow in ['UNREAL', 'POLYHAVEN']:
            packed_keywords = ['orm', 'mra'] if settings.packed_workflow == 'UNREAL' else ['arm']
            packed_maps = find_texture_by_keywords(directory, available_files, packed_keywords)
            if packed_maps:
                packed_texture_path = packed_maps[0]
                final_paths['packed_orm'] = packed_texture_path # Use a generic key
                claimed_files.add(os.path.basename(packed_texture_path))
                packed_channels_found.update(['ao', 'roughness', 'metallic'])
                self.report({'INFO'}, f"Prioritizing Packed Texture: {os.path.basename(packed_texture_path)}")

        # --- Main Investigation Loop ---
        for map_type, keywords in search_order:
            if map_type in packed_channels_found: continue # Skip if already found in a packed map
            unclaimed_filenames = [f for f in available_files if f not in claimed_files]
            found_maps = find_texture_by_keywords(directory, unclaimed_filenames, keywords)
            if found_maps:
                best_file = resolve_conflict(found_maps, map_type) if map_type in ['normal', 'displacement'] else found_maps[0]
                if best_file:
                    final_paths[map_type] = best_file
                    claimed_files.add(os.path.basename(best_file))
        
        if 'roughness' in final_paths and 'gloss' in final_paths: del final_paths['gloss']

        if not final_paths: self.report({'ERROR'}, "No valid PBR maps found."); return {'CANCELLED'}

        # ... (Material Creation / Overwriting Logic) ...
        mat = active_obj.active_material if self.overwrite_material else bpy.data.materials.new(name=f"{active_obj.name}_Material")
        if not self.overwrite_material: active_obj.data.materials.append(mat)
        mat.use_nodes = True
        if 'displacement' in final_paths: mat.cycles.displacement_method = 'DISPLACEMENT'
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        if self.overwrite_material:
            for n in [node for node in nodes if node.type in {'TEX_IMAGE', 'NORMAL_MAP', 'BUMP', 'DISPLACEMENT', 'MIX_RGB', 'INVERT'} or node.bl_idname in ['ShaderNodeMix', 'ShaderNodeMixRGB', 'ShaderNodeSeparateColor']]: nodes.remove(n)
        bsdf_node = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None) or nodes.new('ShaderNodeBsdfPrincipled')
        bsdf_node.location = (250, 0)
        output_node = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None) or nodes.new('ShaderNodeOutputMaterial')
        output_node.location = (600, 0)
        if not output_node.inputs['Surface'].is_linked: links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
        mapping_node = next((n for n in nodes if n.type == 'MAPPING'), None)
        if not mapping_node:
            tex_coord_node = nodes.new('ShaderNodeTexCoord'); tex_coord_node.location = (-750, 0)
            mapping_node = nodes.new('ShaderNodeMapping'); mapping_node.location = (-550, 0)
            links.new(tex_coord_node.outputs['UV'], mapping_node.inputs['Vector'])

        # --- Node Creation and Connection ---
        texture_nodes, node_pos_y = {}, 500
        draw_order = ['diffuse', 'metallic', 'roughness', 'gloss', 'cavity', 'alpha', 'normal', 'bump', 'sss', 'sss_radius', 'specular', 'specular_color', 'transmission', 'coat', 'ao', 'displacement', 'packed_orm']
        label_map = {'diffuse': 'Base Color', 'sss': 'SSS Weight', 'sss_radius': 'SSS Radius', 'ao': 'Ambient Occlusion', 'specular_color': 'Specular Color', 'packed_orm': 'Packed ORM/ARM'}
        for map_type in draw_order:
            if map_type in final_paths:
                path = final_paths[map_type]
                tex_node = nodes.new('ShaderNodeTexImage')
                tex_node.image = bpy.data.images.load(path)
                tex_node.label = label_map.get(map_type, map_type.replace('_', ' ').title())
                tex_node.location = (-350, node_pos_y); node_pos_y -= 320
                links.new(mapping_node.outputs['Vector'], tex_node.inputs['Vector'])
                texture_nodes[map_type] = tex_node
                if map_type in ['diffuse', 'sss_radius', 'specular_color']: tex_node.image.colorspace_settings.name = 'sRGB'
                else: tex_node.image.colorspace_settings.name = 'Non-Color'
        
        blender_version = bpy.app.version
        special_node_y = 300
        
        # --- Connection logic now checks for packed maps first ---
        packed_node = texture_nodes.get('packed_orm')
        sep_col_node = None
        if packed_node:
            sep_col_node = nodes.new('ShaderNodeSeparateColor')
            sep_col_node.location = (-100, packed_node.location.y)
            links.new(packed_node.outputs['Color'], sep_col_node.inputs['Color'])

        # Base Color & AO
        if 'diffuse' in texture_nodes:
            ao_source = None
            if 'ao' in texture_nodes: ao_source = texture_nodes['ao'].outputs['Color']
            elif sep_col_node: ao_source = sep_col_node.outputs['Red'] # R for AO
            
            if ao_source:
                mix_node = nodes.new('ShaderNodeMix'); mix_node.data_type = 'RGBA'; mix_node.blend_type = 'MULTIPLY'
                mix_node.location = (0, special_node_y); special_node_y -= 220
                links.new(texture_nodes['diffuse'].outputs['Color'], mix_node.inputs['A'])
                links.new(ao_source, mix_node.inputs['B'])
                links.new(mix_node.outputs['Result'], bsdf_node.inputs['Base Color'])
            else:
                links.new(texture_nodes['diffuse'].outputs['Color'], bsdf_node.inputs['Base Color'])

        # Roughness
        if 'roughness' in texture_nodes or 'gloss' in texture_nodes:
             # This block handles individual gloss/roughness + cavity
            roughness_source_node = None
            if 'gloss' in texture_nodes:
                invert_node = nodes.new('ShaderNodeInvert'); invert_node.location = (0, special_node_y); special_node_y -= 180
                links.new(texture_nodes['gloss'].outputs['Color'], invert_node.inputs['Color'])
                roughness_source_node = invert_node
            elif 'roughness' in texture_nodes: roughness_source_node = texture_nodes['roughness']
            if roughness_source_node:
                if 'cavity' in texture_nodes:
                    cavity_mix_node = nodes.new('ShaderNodeMix'); cavity_mix_node.data_type = 'RGBA'
                    cavity_mix_node.blend_type = 'SCREEN'; cavity_mix_node.inputs['Factor'].default_value = 0.2
                    cavity_mix_node.location = (0, special_node_y); special_node_y -= 220
                    links.new(roughness_source_node.outputs['Color'], cavity_mix_node.inputs['A'])
                    links.new(texture_nodes['cavity'].outputs['Color'], cavity_mix_node.inputs['B'])
                    links.new(cavity_mix_node.outputs['Result'], bsdf_node.inputs['Roughness'])
                else: links.new(roughness_source_node.outputs['Color'], bsdf_node.inputs['Roughness'])
        elif sep_col_node: # Use packed roughness
            links.new(sep_col_node.outputs['Green'], bsdf_node.inputs['Roughness'])

        # Metallic
        if 'metallic' in texture_nodes: links.new(texture_nodes['metallic'].outputs['Color'], bsdf_node.inputs['Metallic'])
        elif sep_col_node: # Use packed metallic
            links.new(sep_col_node.outputs['Blue'], bsdf_node.inputs['Metallic'])
        
        # ... (All other connection logic remains the same) ...
        if self.mark_as_asset: mat.asset_mark()
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}