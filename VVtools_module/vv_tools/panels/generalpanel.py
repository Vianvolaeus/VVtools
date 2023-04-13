# panels/generalpanel.py

import bpy
from bpy.types import Panel

class VVTools_PT_General(Panel):
    bl_idname = "VV_TOOLS_PT_General"
    bl_label = "VV Tools - General"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.rename_data_blocks")
        layout.operator("vv_tools.vp_wireframe")