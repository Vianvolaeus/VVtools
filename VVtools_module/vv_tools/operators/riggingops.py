# operators/riggingops.py

import bpy
from bpy.types import Operator

# Merge Bones to Active
## Merges weights of selected bones to the active bone, and removes the 'empty' bones. 
### Use case here is generally bone chain reduction, or removing end / leaf bones manually, hair chain reduction, etc. 

def normalize_weights(weights):
    total_weight = sum(weights.values())
    if total_weight == 0:
        return weights
    return {key: value / total_weight for key, value in weights.items()}

def merge_vertex_weights_and_remove_bones(context):
    obj = context.active_object
    if obj is None or obj.type != "ARMATURE":
        return {"ERROR"}, "Active object must be an armature"

    if context.mode != "POSE":
        return {"ERROR"}, "Must be in Pose mode to perform this operation"

    active_bone = context.active_pose_bone
    if active_bone is None:
        return {"ERROR"}, "No active bone selected"

    selected_bones = context.selected_pose_bones.copy()
    selected_bones.remove(active_bone)

    bpy.ops.object.mode_set(mode='OBJECT')

    mesh_objects = [ob for ob in context.scene.objects if ob.type == 'MESH' and ob.find_armature() == obj]

    if not mesh_objects:
        return {"ERROR"}, "No mesh objects found with the active armature as their modifier"

    for mesh_obj in mesh_objects:
        if active_bone.name not in mesh_obj.vertex_groups:
            mesh_obj.vertex_groups.new(name=active_bone.name)

        active_group = mesh_obj.vertex_groups[active_bone.name]

        vertex_weights = {}
        for bone in selected_bones:
            if bone.name in mesh_obj.vertex_groups:
                source_group = mesh_obj.vertex_groups[bone.name]
                for vertex in mesh_obj.data.vertices:
                    for group in vertex.groups:
                        if group.group == source_group.index:
                            if vertex.index not in vertex_weights:
                                vertex_weights[vertex.index] = {bone.name: group.weight}
                            else:
                                vertex_weights[vertex.index][bone.name] = max(group.weight, vertex_weights[vertex.index].get(bone.name, 0))

        for vertex_index, weights in vertex_weights.items():
            normalized_weights = normalize_weights(weights)
            total_weight = sum(normalized_weights.values())
            if total_weight > 0:
                active_group.add([vertex_index], total_weight, 'ADD')

        bpy.ops.object.mode_set(mode='EDIT')
        for bone in selected_bones:
            edit_bone = obj.data.edit_bones.get(bone.name)
            if edit_bone is not None:
                obj.data.edit_bones.remove(edit_bone)
            if bone.name in mesh_obj.vertex_groups:
                source_group = mesh_obj.vertex_groups[bone.name]
                mesh_obj.vertex_groups.remove(source_group)

    bpy.ops.object.mode_set(mode='POSE')

    for mesh_obj in mesh_objects:
        mesh_obj.data.update()

    return {"FINISHED"}, ""

class VVTools_OT_MergeToActiveBone(Operator):
    bl_idname = "vv_tools.merge_to_active_bone"
    bl_label = "Merge Bones to Active"
    bl_description = "Merge selected bones' vertex weights to the active bone and remove them"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        result, message = merge_vertex_weights_and_remove_bones(context)
        if result == "ERROR":
            self.report({"ERROR"}, message)
            return {"CANCELLED"}
        return {"FINISHED"}
        

# Smoothed Rigging Xfer from Active
## Uses Data Transfer modifier to project interpolated face vertex groups to selected meshes, then parents them to the Armature active on the object it took it's data from
### Use case: Nearly automatic rigging of clothing in some cases

class VVTools_OT_SmoothRigXfer(Operator):
    bl_idname = "vv_tools.smooth_rig_xfer"
    bl_label = "Smooth Rig Transfer"
    bl_description = "Transfer vertex weights from active object to selected objects with smoothing"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL',}

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "vv_tools_source_object")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        source_object = context.scene.vv_tools_source_object
        selected_objects = context.selected_objects
        source_armature = source_object.find_armature()

        if source_armature is None:
            self.report({'ERROR'}, "Source object has no armature")
            return {'CANCELLED'}

        for obj in selected_objects:
            if obj == source_object:
                continue
            if obj.type != 'MESH':
                continue

            obj.select_set(True)
            context.view_layer.objects.active = obj

            # Create vertex groups in the target object
            for vertex_group in source_object.vertex_groups:
                obj.vertex_groups.new(name=vertex_group.name)

            # Add Data Transfer modifier
            dt_modifier = obj.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
            dt_modifier.object = source_object
            dt_modifier.use_vert_data = True
            dt_modifier.data_types_verts = {'VGROUP_WEIGHTS'}
            dt_modifier.vert_mapping = 'POLYINTERP_NEAREST'

            # Apply the Data Transfer modifier
            bpy.ops.object.modifier_apply({"object": obj}, modifier=dt_modifier.name)

            # Parent to the armature
            bpy.ops.object.select_all(action='DESELECT')
            source_armature.select_set(True)
            obj.select_set(True)
            context.view_layer.objects.active = source_armature
            bpy.ops.object.parent_set(type='ARMATURE')

            # Smooth vertex groups
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
            bpy.ops.object.vertex_group_smooth(
                group_select_mode='ALL',
                factor=0.5,
                repeat=3,
                expand=-0.25
            )
            bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}