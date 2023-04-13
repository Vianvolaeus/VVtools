# panels/riggingpanel.py

import bpy
from bpy.types import Panel

class VVTools_PT_Rigging(Panel):
    bl_idname = "VV_TOOLS_PT_rigging"
    bl_idname = "VV_TOOLS_PT_rigging"
    bl_label = "VV Tools - Rigging"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_ARMATURE', 'POSE'}

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.merge_to_active_bone")
        layout.separator()
        box = layout.box()
        box.operator("vv_tools.smooth_rig_xfer")
        box.prop(context.scene, "vv_tools_source_object", text="Source Object")
