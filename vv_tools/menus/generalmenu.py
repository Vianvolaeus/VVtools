import bpy
from bpy.types import Menu

class TOPBAR_MT_VV_General(bpy.types.Menu):
    bl_label = "General"
    bl_idname = "TOPBAR_MT_VV_General"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.rename_data_blocks")
        layout.operator("vv_tools.vp_wireframe")

classes = [
    TOPBAR_MT_VV_General,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)