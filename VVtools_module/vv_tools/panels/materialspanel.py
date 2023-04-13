# panels/materialspanel.py

import bpy
from bpy.types import Panel

class VVTools_PT_Materials(Panel):
    bl_idname = "VV_TOOLS_PT_materials"
    bl_label = "VV Tools - Materials"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.reload_textures_of_selected")
        layout.operator("vv_tools.remove_unused_materials")