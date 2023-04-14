import bpy
from bpy.types import Menu

class TOPBAR_MT_VV_VRC(bpy.types.Menu):
    bl_label = "VRC"
    bl_idname = "TOPBAR_MT_VV_VRC"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.vrc_analyse")

classes = [
    TOPBAR_MT_VV_VRC,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)