import bpy
from bpy.types import Menu

class TOPBAR_MT_VV_Materials(bpy.types.Menu):
    bl_label = "Materials"
    bl_idname = "TOPBAR_MT_VV_Materials"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.reload_textures_of_selected")
        layout.operator("vv_tools.remove_unused_materials")
        
classes = [
    TOPBAR_MT_VV_Materials,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)