#operators/vrcanalysisops.py

# VRC Analysis of Selected
## Analysis tool for VRchat avatars. Takes the selected objects and returns an estimate of it's performance ranking. 
### Naturally this will be prone to inaccuracies as some things don't directly translate. It currently shows warnings when you are potentially in the Very Poor catgeory, but should still show what performance rank you have

import bpy
import json
from bpy.types import Operator, Panel

def performance_rank(statistics):
    ranks = [
        ('Excellent', {'triangles': 32000, 'texture_memory': 40 * 1024 * 1024, 'skinned_meshes': 1, 'meshes': 4, 'material_slots': 4, 'bones': 75}),
        ('Good', {'triangles': 70000, 'texture_memory': 75 * 1024 * 1024, 'skinned_meshes': 2, 'meshes': 8, 'material_slots': 8, 'bones': 150}),
        ('Medium', {'triangles': 70000, 'texture_memory': 110 * 1024 * 1024, 'skinned_meshes': 8, 'meshes': 16, 'material_slots': 16, 'bones': 256}),
        ('Poor', {'triangles': 70000, 'texture_memory': 150 * 1024 * 1024, 'skinned_meshes': 16, 'meshes': 24, 'material_slots': 32, 'bones': 400}),
        ('Very Poor', {}),
    ]
    
    rank_index = 0
    for key, value in statistics.items():
        for i, (rank, limits) in enumerate(ranks[:-1]):
            if value > limits[key]:
                rank_index = max(rank_index, i + 1)
    
    return ranks[rank_index][0]

def performance_warning(statistics):
    warnings = []

    if statistics['triangles'] > 70000:
        warnings.append("Polygon count is high. Consider dissolving unnecessary geometry, decimation, or removing unnecessary geometry entirely.")

    if statistics['texture_memory'] > 150 * 1024 * 1024:
        warnings.append("Detected VRAM is high! Consider reducing texture resolution, or using VRAM reduction techniques in Unity. If you are using high resolution source textures, remember Unity will downres these to 2K on import.")

    if statistics['skinned_meshes'] > 16:
        warnings.append("Skinned Mesh count is high. Consider merging skinned meshes as appropriate, or offloading things like outfit changes to a different avatar entirely.")
        
    if statistics['meshes'] > 24:
        warnings.append("Meshes count is high. It is questionable why you need so many meshes, and you should consider merging them as appropriate, or removing them as appropriate.")

    if statistics['material_slots'] > 32:
        warnings.append("Material Count is very high. Check for duplicate entries, unused material slots, and atlas textures if required. If you can merge two meshes that share the exact same material, this stat will effectively be lowered.")

    if statistics['bones'] > 400:
        warnings.append("Bones count is very high. Check for duplicate or unused armatures, _end bones (leaf bones), zero weight bones and remove them as needed.")

    return warnings

def analyze_selected_objects():
    statistics = {
        'triangles': 0,
        'texture_memory': 0,
        'skinned_meshes': 0,
        'meshes': 0,
        'material_slots': 0,
        'bones': 0,
    }

    texture_memory_usage = {}
    
    # Iterate through selected objects
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            # Apply modifiers to a temporary mesh. This is so things like Subdiv get calcuated properly, since they can and do get exported. 
            depsgraph = bpy.context.evaluated_depsgraph_get()
            temp_obj = obj.evaluated_get(depsgraph)
            temp_mesh = bpy.data.meshes.new_from_object(temp_obj)
            
            #Calculate triangle count. We need to calculate *tris* since perf rank is based on these, not the internal Blender polygon calculation
            triangles = sum(len(p.vertices) - 2 for p in temp_mesh.polygons)
            statistics['triangles'] += triangles

            bpy.data.meshes.remove(temp_mesh)
            statistics['material_slots'] += len(obj.material_slots)

            if any(mod for mod in obj.modifiers if mod.type == 'ARMATURE'):
                statistics['skinned_meshes'] += 1
            else:
                statistics['meshes'] += 1

            # Estimate texture memory... I think this is correct and accounts for texture sharing?
            for mat_slot in obj.material_slots:
                if mat_slot.material:
                    for node in mat_slot.material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            img = node.image
                            if img:
                                if img not in texture_memory_usage:
                                    texture_memory_usage[img] = img.size[0] * img.size[1] * 4 // 4 # Assuming a DXT5 compression ratio for textures, at their current resolution (not 2k). This should be a little more accurate, I think?
                                    
        elif obj.type == 'ARMATURE':
            statistics['bones'] += len(obj.data.bones)
    
    statistics['texture_memory'] = sum(texture_memory_usage.values())
    return statistics

class VVTools_OT_VRCAnalyse(Operator):
    bl_idname = "vv_tools.vrc_analyse"
    bl_label = "VRC Analyse"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        context.area.tag_redraw()
        result = analyze_selected_objects()
        context.scene["VRC_Analysis_Results"] = json.dumps(result)

        # Redraw the area to update the panel. Without this, user input is required to make the panel update. 
        context.area.tag_redraw()

        return {"FINISHED"}


classes = [
    VVTools_OT_VRCAnalyse,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)