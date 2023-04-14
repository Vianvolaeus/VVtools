import bpy
from bpy.types import Panel, Operator, PropertyGroup, UIList

class TOPBAR_MT_VV_Rigging(bpy.types.Menu):
    bl_label = "Rigging"
    bl_idname = "TOPBAR_MT_VV_Rigging"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.merge_to_active_bone")
        layout.operator("vv_tools.smooth_rig_xfer")
        
classes = [
    TOPBAR_MT_VV_Rigging,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)