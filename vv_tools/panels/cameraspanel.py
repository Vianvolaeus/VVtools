# panels/cameraspanel.py

import bpy
from bpy.types import Panel

class VVTools_PT_Cameras(Panel):
    bl_label = "VV Tools - Cameras"
    bl_idname = "VVTOOLS_PT_Cameras"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'VV'

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.add_viewport_camera")
        row = layout.row(align=True)
        row.operator("vv_tools.switch_to_previous_camera", text="Prev")
        row.operator("vv_tools.switch_to_next_camera", text="Next")
        
classes = [
    VVTools_PT_Cameras,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)