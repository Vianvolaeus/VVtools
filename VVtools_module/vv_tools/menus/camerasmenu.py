import bpy
from bpy.types import Menu

class TOPBAR_MT_VV_Cameras(bpy.types.Menu):
    bl_label = "Cameras"
    bl_idname = "TOPBAR_MT_VV_Cameras"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.add_viewport_camera")
        row = layout.row(align=True)
        row.operator("vv_tools.switch_to_previous_camera", text="Prev")
        row.operator("vv_tools.switch_to_next_camera", text="Next")
        

classes = [
    TOPBAR_MT_VV_Cameras,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)