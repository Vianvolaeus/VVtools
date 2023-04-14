import bpy
from bpy.types import Menu

class TOPBAR_MT_VV_Mesh_Operators(bpy.types.Menu):
    bl_label = "Mesh Operators"
    bl_idname = "TOPBAR_MT_VV_Mesh_Operators"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.add_visual_geometry")
        layout.operator("vv_tools.set_modifiers_visibility")

classes = [
    TOPBAR_MT_VV_Mesh_Operators,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)