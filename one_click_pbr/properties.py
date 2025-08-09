# one_click_pbr/properties.py

import bpy

class OCP_Settings(bpy.types.PropertyGroup):
    """Properties to control the addon's behavior."""
    
    show_selective_mode: bpy.props.BoolProperty(
        name="Selective Mode",
        description="Enable to choose which texture maps to import",
        default=False
    )
    
    packed_workflow: bpy.props.EnumProperty(
        name="Packed Workflow",
        description="Select a channel-packing convention to search for",
        items=[
            ('NONE', "None", "Only search for individual texture files"),
            ('UNREAL', "Unreal Engine (ORM)", "Prioritize Occlusion(R), Roughness(G), Metallic(B) packed textures"),
            ('POLYHAVEN', "PolyHaven (ARM)", "Prioritize AO(R), Roughness(G), Metallic(B) packed textures"),
            ('UNITY', "Unity (Metallic Smoothness)", "Prioritize Metallic(RGB) with Smoothness(A)"),
        ],
        default='NONE'
    )
    
    use_diffuse: bpy.props.BoolProperty(name="Diffuse / Color", default=True)
    use_metallic: bpy.props.BoolProperty(name="Metallic", default=True)
    use_roughness: bpy.props.BoolProperty(name="Roughness / Gloss", default=True)
    use_normal_map: bpy.props.BoolProperty(name="Normal", default=True)
    use_bump_map: bpy.props.BoolProperty(name="Bump", default=True)
    use_displacement: bpy.props.BoolProperty(name="Displacement / Height", default=True)
    use_ao: bpy.props.BoolProperty(name="Ambient Occlusion", default=True)
    use_cavity: bpy.props.BoolProperty(name="Cavity", default=True)
    use_alpha: bpy.props.BoolProperty(name="Alpha / Opacity", default=True)
    use_sss: bpy.props.BoolProperty(name="Subsurface (SSS)", default=True)
    use_specular: bpy.props.BoolProperty(name="Specular", default=True)
    use_transmission: bpy.props.BoolProperty(name="Transmission", default=True)
    use_coat: bpy.props.BoolProperty(name="Coat", default=True)
