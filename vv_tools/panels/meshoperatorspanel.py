# panels/meshoperatorspanel.py

import bpy
from bpy.types import Panel

class VVTools_PT_Mesh_Operators(Panel):
    bl_idname = "VV_TOOLS_PT_mesh_operators"
    bl_label = "VV Tools - Mesh Operators"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.add_visual_geometry")
        layout.operator("vv_tools.set_modifiers_visibility")

classes = [
    VVTools_PT_Mesh_Operators,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)