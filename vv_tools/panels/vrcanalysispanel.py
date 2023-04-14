# panels/vrcanalysispanel.py

import bpy
import json
import re
from ..operators.vrcanalysisops import performance_rank, performance_warning, analyze_selected_objects
from bpy.types import Panel


class VVTools_PT_VRCAnalysis(Panel):
    bl_idname = "VV_TOOLS_PT_vrc_analysis"
    bl_label = "VV Tools - VRC"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    def draw(self, context):
        layout = self.layout

        results = None
        if "VRC_Analysis_Results" in context.scene:
            results_str = context.scene["VRC_Analysis_Results"]
            results = json.loads(results_str)


        if results:
            layout.label(text=f"Polygons (Tris): {results['triangles']}/69999")
            layout.label(text=f"Texture Memory (EXPERIMENTAL): {results['texture_memory'] / (1024 * 1024):.2f} MB")
            layout.label(text=f"Skinned Meshes: {results['skinned_meshes']}")
            layout.label(text=f"Meshes: {results['meshes']}")
            layout.label(text=f"Material Slots: {results['material_slots']}")
            layout.label(text=f"Bones: {results['bones']}")

            layout.separator()
            layout.label(text=f"Performance Rank: {performance_rank(results)}")
            warnings = performance_warning(results)
            for warning in warnings:
                box = layout.box()
                lines = re.split(r'(?<=[.!,] )', warning)  # Split the text at both '. ' and ', '. This is a bit of a hack - maybe I should shorten warnings...
                for line in lines:
                    if line:
                        box.label(text=line)

        else:
            layout.label(text="No analysis data available")
            layout.label(text="Will run slow on first use!")

        layout.operator("vv_tools.vrc_analyse")

classes = [
    VVTools_PT_VRCAnalysis,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)