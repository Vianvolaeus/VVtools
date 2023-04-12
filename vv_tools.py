bl_info = {
    "name": "VV_Tools",
    "author": "Vianvolaeus",
    "version": (0, 5, 4),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > VV",
    "description": "General toolkit, mainly for automating short processes.",
    "warning": "Potentially unstable, documentation incomplete.",
    "doc_url": "https://github.com/Vianvolaeus/VVtools",
    "category": "General",
}

import bpy
import os
import textwrap
import re
import json

from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, PointerProperty, BoolProperty, IntProperty, FloatProperty
from bpy.utils import previews
from mathutils import Vector

# Register icons, incomplete, but not code-breaking. Finish later

icon_collection = None

def register_icons():
    global icon_collection
    icon_collection = previews.new()

    icons_dir = os.path.join(os.path.dirname(__file__), "icons")

    for filename in os.listdir(icons_dir):
        if not filename.endswith(".png"):
            continue
        name, _ = os.path.splitext(filename)
        filepath = os.path.join(icons_dir, filename)
        icon_collection.load(name, filepath, 'IMAGE')

def unregister_icons():
    global icon_collection
    bpy.utils.previews.remove(icon_collection)
    icon_collection = None

# Draw menu for header. SUBMENUS NEED TO BE DRAWN INSIDE THE CUSTOM MENU, ADD THEM TO layout.menu HERE.  

class TOPBAR_MT_custom_menu(bpy.types.Menu):
    bl_label = "VV Tools"
    bl_idname = "TOPBAR_MT_custom_menu"

    def draw(self, context):
        layout = self.layout
        layout.menu("TOPBAR_MT_VV_General")
        layout.menu("TOPBAR_MT_VV_Cameras")
        layout.menu("TOPBAR_MT_VV_Materials")
        layout.menu("TOPBAR_MT_VV_Mesh_Operators")
        layout.menu("TOPBAR_MT_VV_Rigging")
        layout.menu("TOPBAR_MT_VV_VRC")

    def menu_draw(self, context):
        self.layout.menu("TOPBAR_MT_custom_menu")

# Draw submenus for header Top Menu. OPERATORS NEED TO BE ADDED TO LAYOUT OF SUBMENUS ("vv_tools(X)"), IN THEIR CORRECT CATEGORIES 

class TOPBAR_MT_VV_General(bpy.types.Menu):
    bl_label = "General"
    bl_idname = "TOPBAR_MT_VV_General"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.rename_data_blocks")
        layout.operator("vv_tools.vp_wireframe")
        

class TOPBAR_MT_VV_Cameras(bpy.types.Menu):
    bl_label = "Cameras"
    bl_idname = "TOPBAR_MT_VV_Cameras"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.add_viewport_camera")
        row = layout.row(align=True)
        row.operator("vv_tools.switch_to_previous_camera", text="Prev")
        row.operator("vv_tools.switch_to_next_camera", text="Next")
 
class TOPBAR_MT_VV_Materials(bpy.types.Menu):
    bl_label = "Materials"
    bl_idname = "TOPBAR_MT_VV_Materials"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.reload_textures_of_selected")
        layout.operator("vv_tools.remove_unused_materials")


class TOPBAR_MT_VV_Mesh_Operators(bpy.types.Menu):
    bl_label = "Mesh Operators"
    bl_idname = "TOPBAR_MT_VV_Mesh_Operators"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.add_visual_geometry")
        layout.operator("vv_tools.set_modifiers_visibility")

class TOPBAR_MT_VV_Rigging(bpy.types.Menu):
    bl_label = "Rigging"
    bl_idname = "TOPBAR_MT_VV_Rigging"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.merge_to_active_bone")
        layout.operator("vv_tools.smooth_rig_xfer")

class TOPBAR_MT_VV_VRC(bpy.types.Menu):
    bl_label = "VRC"
    bl_idname = "TOPBAR_MT_VV_VRC"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.vrc_analyse")

classes = (TOPBAR_MT_custom_menu, TOPBAR_MT_VV_General, TOPBAR_MT_VV_Materials, TOPBAR_MT_VV_Mesh_Operators, TOPBAR_MT_VV_Rigging, TOPBAR_MT_VV_VRC)

# Operators below. Probably should sort these out into some logical order, or into categories if possible

# Remove Unused Materials
## Looks at object selection and removes materials that are not in use / assigned to any vertex. Useful for material slot cleanup. 

class VVTools_OT_RemoveUnusedMaterials(Operator):
    bl_idname = "vv_tools.remove_unused_materials"
    bl_label = "Remove Unused Materials"
    bl_description = "Remove materials that aren't being used by any vertex on objects."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    warning_shown = False

    def remove_unused_materials(self, obj):
        used_materials = set()

        # Collect used materials
        for poly in obj.data.polygons:
            used_materials.add(poly.material_index)

        # Remove unused materials
        for i, mat_slot in reversed(list(enumerate(obj.material_slots))):
            if i not in used_materials:
                obj.active_material_index = i
                bpy.ops.object.material_slot_remove({'object': obj})

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                self.remove_unused_materials(obj)

        self.warning_shown = False
        self.report({'INFO'}, "Materials removed.")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.warning_shown = True
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        if self.warning_shown:
            layout = self.layout
            col = layout.column()
            col.label(text="Removing materials that aren't being used by any vertex on objects.")
            col.label(text="If you would like to retain the materials in the Blender file,")
            col.label(text="consider adding a Fake User (Shield Icon) to them first.")

# Camera Switch
## Two functions to cycle between cameras

class VVTools_OT_SwitchToNextCamera(Operator):
    bl_idname = "vv_tools.switch_to_next_camera"
    bl_label = "Next Camera"
    bl_description = "Switch to the next camera in the scene."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        cameras = [obj for obj in context.scene.objects if obj.type == 'CAMERA']
        if not cameras:
            self.report({'WARNING'}, "No cameras found in the scene")
            return {'CANCELLED'}

        current_camera = context.scene.camera
        idx = cameras.index(current_camera)
        next_idx = (idx + 1) % len(cameras)
        context.scene.camera = cameras[next_idx]

        return {'FINISHED'}


class VVTools_OT_SwitchToPreviousCamera(Operator):
    bl_idname = "vv_tools.switch_to_previous_camera"
    bl_label = "Previous Camera"
    bl_description = "Switch to the previous camera in the scene."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        cameras = [obj for obj in context.scene.objects if obj.type == 'CAMERA']
        if not cameras:
            self.report({'WARNING'}, "No cameras found in the scene")
            return {'CANCELLED'}

        current_camera = context.scene.camera
        idx = cameras.index(current_camera)
        prev_idx = (idx - 1) % len(cameras)
        context.scene.camera = cameras[prev_idx]

        return {'FINISHED'}

# Add Viewport Camera
## Adds a passepartout camera using the current viewport position, adds a DoF Empty and projects it towards the nearest object the camera is pointing at

import bpy
from bpy.types import Operator
from mathutils import Vector

class VVTools_OT_AddViewportCamera(Operator):
    bl_idname = "vv_tools.add_viewport_camera"
    bl_label = "Add Viewport Camera"
    bl_description = "Add a new camera named 'Viewport Camera', set it as active, align it to the current viewport view, and set up an Empty as its Depth of Field object."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        # Create a new camera and set it as the active camera
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
        camera.name = "Viewport Camera"
        bpy.context.scene.camera = camera

        # Set camera properties
        camera.data.passepartout_alpha = 1

        # Align the camera to the current viewport view
        bpy.ops.view3d.camera_to_view()

        # Create a new Empty object
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        empty = bpy.context.active_object
        empty.name = "DoF Empty"

        # Set up the Depth of Field object for the camera
        camera.data.dof.aperture_fstop = 1.2
        camera.data.dof.use_dof = True
        camera.data.dof.focus_object = empty

        # Parent the Empty object to the camera
        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(True)
        camera.select_set(True)
        context.view_layer.objects.active = camera
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        # Project a ray from the camera to find the first face it touches
        context = bpy.context
        depsgraph = context.evaluated_depsgraph_get()

        origin = camera.location
        direction = camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
        result, location, normal, index, obj, matrix = context.scene.ray_cast(depsgraph, origin, direction)

        # Move the Empty object to the position of the first face touched by the projected ray
        if result:
            empty.location = location

        # Move objects to the 'Viewport Camera' collection
        coll_name = "Viewport Camera"
        if coll_name not in bpy.data.collections:
            viewport_camera_collection = bpy.data.collections.new(coll_name)
            bpy.context.scene.collection.children.link(viewport_camera_collection)
        else:
            viewport_camera_collection = bpy.data.collections[coll_name]

        # Move camera and empty to the collection
        current_collection = camera.users_collection[0]
        current_collection.objects.unlink(camera)
        current_collection.objects.unlink(empty)
        viewport_camera_collection.objects.link(camera)
        viewport_camera_collection.objects.link(empty)

        return {'FINISHED'}



# Viewport Wireframe
## Simple global wireframe toggle for the viewport

class VVTools_OT_ViewportWireframe(Operator):
    bl_idname = "vv_tools.vp_wireframe"
    bl_label = "Viewport Wireframe"
    bl_description = "Toggles global wireframe in the viewport."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL',}
    
    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.overlay.show_wireframes = not space.overlay.show_wireframes
        return {'FINISHED'}

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

        
# Visual Geometry To Shape Key. Uses the Visual Geometry To Mesh operator on a dupliate mesh, and uses Join As Shapes to add it back as a Shape Key to original Mesh object. Cleans dupe. 
## Does not work with modifiers that change vertex count, since they cannot be added as a shapekey, of course!
### Useful for modifier based visual dev / concepting. 

def add_visual_geometry_as_shape_key(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    object_eval = obj.evaluated_get(depsgraph)
    mesh_from_eval = bpy.data.meshes.new_from_object(object_eval)

    # Check for shape keys, add them if not present
    if obj.data.shape_keys is None:
        obj.shape_key_add(name="Basis")

    obj.shape_key_add(name="Visual Geometry", from_mix=True)
    shape_key = obj.data.shape_keys.key_blocks["Visual Geometry"]
    shape_key.slider_min = 0
    shape_key.slider_max = 1

    for i, coord in enumerate(mesh_from_eval.vertices):
        obj.data.shape_keys.key_blocks["Visual Geometry"].data[i].co = coord.co

    bpy.data.meshes.remove(mesh_from_eval)

class VVTools_OT_VisGeoShapeKey(Operator):
    bl_idname = "vv_tools.add_visual_geometry"
    bl_label = "Visual Geo to Shape"
    bl_icon = "SHAPEKEY_DATA"
    bl_description = "Runs Visual Geometry To Mesh, appends to current object as Shape Key. Does not work with operations that change vertex count."
    bl_options = {"REGISTER", "UNDO", "INTERNAL",}
    bl_category = {"VV_tools"}

    def execute(self, context):
        obj = context.active_object
        add_visual_geometry_as_shape_key(obj)
        return {"FINISHED"}

# Modifier Toggle Viewport and Render. Used to toggle all modifiers on selected Objects. 
## It looks at the current state to determine whether to toggle on / off. This means it won't do a raw toggle resulting in switching off viewport, but render on, etc. 
### Useful in conjunction with Visual Geometry to Shape Key. (We treat Modifier choice as sacred and leave it up to user to globally toggle / remove all).

def set_modifiers_visibility(objs, state):
    for obj in objs:
        for modifier in obj.modifiers:
            modifier.show_viewport = state
            modifier.show_render = state

class VVTools_OT_SetModifiersVisibility(Operator):
    bl_idname = "vv_tools.set_modifiers_visibility"
    bl_label = "Toggle Modifiers Visibility"
    bl_description = "Toggles Viewport and Render visibility for all modifiers on the currently selected objects."
    bl_options = {"REGISTER", "UNDO", "INTERNAL",}

    on_off: BoolProperty(
        name="On/Off",
        description="Turn the modifiers' visibility on or off",
        default=True
    )

    def execute(self, context):
        selected_objs = context.selected_objects
        set_modifiers_visibility(selected_objs, self.on_off)
        self.on_off = not self.on_off
        return {"FINISHED"}
        
       

# Rename Data Blocks with Object Name. This takes the Object name and applies it to the relevant Data Block attached to the object. 
## Use case here is simply for scene cleanup / asset cleanup, so you don't have some unknown 'Cube.005' type object when exported to another program, etc. 

def rename_data_blocks(obj):
    obj.data.name = obj.name
    for block in obj.bl_rna.properties.keys():
        if block.endswith("_name"):
            if hasattr(obj.data, block):
                obj.data.__setattr__(block, obj.name)



class VVTools_OT_RenameDataBlocks(Operator):
    bl_idname = "vv_tools.rename_data_blocks"
    bl_label = "Object Name Data Block Rename"
    bl_description = "Rename the data blocks of the selected objects based on their Object's name"
    bl_options = {"REGISTER", "UNDO", "INTERNAL",}

    def execute(self, context):
        if not context.selected_objects:
            self.report({"ERROR"}, "No selected objects")
            return {"CANCELLED"}

        for obj in context.selected_objects:
            rename_data_blocks(obj)
        return {"FINISHED"}

 
# Merge Bones to Active
## Merges weights of selected bones to the active bone, and removes the 'empty' bones. 

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


# Selected Object Texture Reload
## Refreshes linked textures for selected objects. Useful for external texture authoring (Substance)
### WARNING! Can be slow!

def reload_textures(objects):
    for obj in objects:
        for slot in obj.material_slots:
            if slot.material:
                for node in slot.material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE':
                        node.image.reload()

class VVTools_OT_ReloadTexturesOfSelected(Operator):
    bl_idname = "vv_tools.reload_textures_of_selected"
    bl_label = "Reload Textures of Selected"
    bl_description = "Reload all textures of the selected objects. WARNING! Can run slow."
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        selected_objects = context.selected_objects
        reload_textures(selected_objects)
        return {"FINISHED"}

# VRC Analysis of Selected
## Analysis tool for VRchat avatars. Takes the selected objects and returns an estimate of it's performance ranking. 
### Naturally this will be prone to inaccuracies as some things don't directly translate. It currently shows warnings when you are potentially in the Very Poor catgeory, but should still show what performance rank you have

import bpy
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
        result = analyze_selected_objects()
        context.scene["VRC_Analysis_Results"] = json.dumps(result)

        # Redraw the area to update the panel. Without this, user input is required to make the panel update. 
        context.area.tag_redraw()

        return {"FINISHED"}

# End of operator list - internal tag applied to operators since we draw a top menu and submenus, things will be categorized in search nicely this way

# Panels, for 3Dview sidebar

class VVTools_PT_General(Panel):
    bl_idname = "VV_TOOLS_PT_General"
    bl_label = "VV Tools - General"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.rename_data_blocks")
        layout.operator("vv_tools.vp_wireframe")


class VVTools_PT_Cameras(Panel):
    bl_label = "VV Tools - Cameras"
    bl_idname = "VVTOOLS_PT_Cameras"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'VV'

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.add_viewport_camera")
        row = layout.row(align=True)
        row.operator("vv_tools.switch_to_previous_camera", text="Prev")
        row.operator("vv_tools.switch_to_next_camera", text="Next")

class VVTools_PT_Mesh_Operators(Panel):
    bl_idname = "VV_TOOLS_PT_mesh_operators"
    bl_label = "VV Tools - Mesh Operators"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.add_visual_geometry")
        layout.operator("vv_tools.set_modifiers_visibility")

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


class VVTools_PT_Materials(Panel):
    bl_idname = "VV_TOOLS_PT_materials"
    bl_label = "VV Tools - Materials"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.reload_textures_of_selected")
        layout.operator("vv_tools.remove_unused_materials")


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


# Class list, add new classes here so they (un)register properly...

classes = [
    VVTools_OT_RemoveUnusedMaterials,
    VVTools_OT_SwitchToNextCamera,
    VVTools_OT_SwitchToPreviousCamera,
    VVTools_OT_AddViewportCamera,
    VVTools_OT_ViewportWireframe,
    VVTools_OT_SmoothRigXfer,
    VVTools_OT_VisGeoShapeKey,
    VVTools_OT_RenameDataBlocks,
    VVTools_OT_SetModifiersVisibility,
    VVTools_OT_MergeToActiveBone,
    VVTools_OT_ReloadTexturesOfSelected,
    VVTools_OT_VRCAnalyse,
    VVTools_PT_General,
    VVTools_PT_Cameras,
    VVTools_PT_Mesh_Operators,
    VVTools_PT_Rigging,
    VVTools_PT_Materials,
    VVTools_PT_VRCAnalysis,
    TOPBAR_MT_custom_menu,
    TOPBAR_MT_VV_General,
    TOPBAR_MT_VV_Cameras, 
    TOPBAR_MT_VV_Materials,
    TOPBAR_MT_VV_Mesh_Operators,
    TOPBAR_MT_VV_Rigging,
    TOPBAR_MT_VV_VRC,
]

def register():
    for cls in classes:
            bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_custom_menu.menu_draw)
    bpy.types.Scene.vv_tools_source_object = bpy.props.PointerProperty(
        name="Source Object",
        type=bpy.types.Object,
        description="The source object to transfer vertex group data from"
    )

def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_custom_menu.menu_draw)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.vv_tools_source_object
    
if __name__ == "__main__":
    register()

