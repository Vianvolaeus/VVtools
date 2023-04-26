# panels/riggingpanel.py

import bpy
from bpy.types import Panel
from bpy.props import StringProperty, PointerProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty

class VVTools_PT_Rigging(Panel):
    bl_idname = "VV_TOOLS_PT_rigging"
    bl_label = "VV Tools - Rigging"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_ARMATURE', 'POSE', 'EDIT_MESH'}

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.merge_to_active_bone")
        layout.operator("vv_tools.button_attach")
        layout.separator()
        box = layout.box()
        box.operator("vv_tools.smooth_rig_xfer")


classes = [
    VVTools_PT_Rigging,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)