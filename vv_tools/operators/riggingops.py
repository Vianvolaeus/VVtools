# operators/riggingops.py

import bpy
import bmesh
import mathutils
from bpy.types import Operator, PropertyGroup
from mathutils import Vector, Matrix

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
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'INTERNAL',}

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
            bpy.ops.object.modifier_apply(modifier=dt_modifier.name)

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

# Button Attach
## Used to transfer the weights of a single vertex, or a generated vertex from a Face selection to another object, which is snapped to the selection in Edit mode.
### Use case - attaching buttons / patches etc to clothing items that already have weights. 


class VVTools_OT_ButtonAttach(Operator):
    bl_idname = "vv_tools.button_attach"
    bl_label = "Button Attach"
    bl_description = "Attach object to an Edit Mode selection, transferring weights."
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    weight_transfer_method: bpy.props.EnumProperty(
        name="Weight Method",
        description="Choose the method for transferring vertex weights",
        items=[
            ("EXACT", "Exact", "Transfer exact vertex or poke face vertex weight"),
            ("DATA_TRANSFER", "Data Transfer", "Transfer weights using Nearest Face Interpolated data transfer"),
        ],
        default="EXACT",
    )

    normal_offset: bpy.props.FloatProperty(
        name="Normal Offset",
        description="Offset the target object along the normal direction",
        default=0.0,
        soft_min=-10.0,
        soft_max=10.0,
    )

    confirm: bpy.props.BoolProperty(
        name="Confirm",
        description="Confirm the position before attaching",
        default=False,
    )

    def invoke(self, context, event):
        self.normal_offset = 0.0
        self.confirm = False
        return self.execute(context)

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def snap_to_vertex(self, source_obj, target_obj, vertex):
        target_obj.location = source_obj.matrix_world @ (vertex.co + vertex.normal * self.normal_offset)
        normal_world = source_obj.matrix_world.to_3x3() @ vertex.normal
        target_obj.rotation_euler = normal_world.to_track_quat('Z', 'Y').to_euler()

    def snap_to_face(self, source_obj, target_obj, center_vert, normal):
        center = source_obj.matrix_world @ (center_vert.co + normal * self.normal_offset)
        target_obj.location = center
        normal_world = source_obj.matrix_world.to_3x3() @ normal
        target_obj.rotation_euler = normal_world.to_track_quat('Z', 'Y').to_euler()


    def parent_to_armature(self, source_obj, target_obj):
        armature_obj = None
        for modifier in source_obj.modifiers:
            if modifier.type == 'ARMATURE':
                armature_obj = modifier.object
                break

        if armature_obj is not None:
            target_obj.parent = armature_obj

            # Check if the Armature modifier with the same armature object already exists on the target object
            existing_mod = next((mod for mod in target_obj.modifiers if mod.type == 'ARMATURE' and mod.object == armature_obj), None)

            # Add an Armature modifier only if it doesn't exist already
            if not existing_mod:
                armature_mod = target_obj.modifiers.new("Armature", 'ARMATURE')
                armature_mod.object = armature_obj

        else:
            self.report({"WARNING"}, "No Armature modifier found in source object")


    def transfer_weights(self, source_obj, target_obj, temp_bm, center_vert_index):
        if self.weight_transfer_method == "EXACT":
            target_obj.vertex_groups.clear()

            deform_layer = temp_bm.verts.layers.deform.active

            if deform_layer is None:
                return

            vert_groups = {}
            for v in temp_bm.verts:
                vert_groups[v.index] = {source_obj.vertex_groups[group].name: v[deform_layer][group] for group in v[deform_layer].keys()}

            center_vert_groups = vert_groups[center_vert_index]

            for group_name, weight in center_vert_groups.items():
                target_group = target_obj.vertex_groups.get(group_name)
                if target_group is None:
                    target_group = target_obj.vertex_groups.new(name=group_name)

                if target_obj.mode == 'EDIT':
                    bpy.ops.object.mode_set(mode='OBJECT')

                target_group.add([v.index for v in target_obj.data.vertices], weight, 'REPLACE')

                if target_obj.mode == 'OBJECT':
                    bpy.ops.object.mode_set(mode='EDIT')

        elif self.weight_transfer_method == "DATA_TRANSFER":
            # Switch to OBJECT mode
            if target_obj.mode == 'EDIT':
                bpy.ops.object.mode_set(mode='OBJECT')

            # Create vertex groups in the target object with the same names as in the source object
            for group in source_obj.vertex_groups:
                if group.name not in target_obj.vertex_groups:
                    target_obj.vertex_groups.new(name=group.name)

            # Add a Data Transfer modifier to the target object
            data_transfer_mod = target_obj.modifiers.new("Data Transfer", 'DATA_TRANSFER')
            data_transfer_mod.object = source_obj
            data_transfer_mod.use_vert_data = True
            data_transfer_mod.data_types_verts = {'VGROUP_WEIGHTS'}
            data_transfer_mod.vert_mapping = 'POLYINTERP_NEAREST'

            # Call the datalayout_transfer operator to generate data layers
            bpy.ops.object.datalayout_transfer()

            # Apply the Data Transfer modifier
            bpy.ops.object.modifier_apply({"object": target_obj}, modifier=data_transfer_mod.name)

            # Switch back to EDIT mode
            if target_obj.mode == 'OBJECT':
                bpy.ops.object.mode_set(mode='EDIT')


        
    def execute(self, context):
        source_obj = context.active_object
        other_objs = [obj for obj in context.selected_objects if obj != source_obj]
        if not other_objs:
            self.report({"ERROR"}, "No target object found")
            return {"CANCELLED"}

        target_obj = other_objs[0]

        bm = bmesh.from_edit_mesh(source_obj.data)
        selected_elems = [e for e in bm.select_history if isinstance(e, (bmesh.types.BMVert, bmesh.types.BMFace))]

        if not selected_elems:
            self.report({"ERROR"}, "No vertex or face selection found")
            return {"CANCELLED"}

        if len(selected_elems) > 1:
            self.report({"ERROR"}, "Please select only one vertex or one face")
            return {"CANCELLED"}

        elem = selected_elems[0]

        if isinstance(elem, bmesh.types.BMVert):
            self.snap_to_vertex(source_obj, target_obj, elem)
        elif isinstance(elem, bmesh.types.BMFace):
            temp_bm = bmesh.new()
            temp_bm.from_mesh(source_obj.data)
            temp_bm.faces.ensure_lookup_table()
            temp_face = temp_bm.faces[elem.index]

            res = bmesh.ops.poke(temp_bm, faces=[temp_face])
            center_vert = res["verts"][0]

            self.snap_to_face(source_obj, target_obj, center_vert, elem.normal)
            temp_bm.free()

        if self.confirm:
            if isinstance(elem, bmesh.types.BMVert):
                self.transfer_weights(source_obj, target_obj, bm, elem.index)
            elif isinstance(elem, bmesh.types.BMFace):
                temp_bm = bmesh.new()
                temp_bm.from_mesh(source_obj.data)
                temp_bm.faces.ensure_lookup_table()
                temp_face = temp_bm.faces[elem.index]

                res = bmesh.ops.poke(temp_bm, faces=[temp_face])
                center_vert = res["verts"][0]

                self.transfer_weights(source_obj, target_obj, temp_bm, center_vert.index)
                temp_bm.free()

            self.parent_to_armature(source_obj, target_obj)
        return {"FINISHED"}


classes = [
    VVTools_OT_MergeToActiveBone,
    VVTools_OT_SmoothRigXfer,
    VVTools_OT_ButtonAttach,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)