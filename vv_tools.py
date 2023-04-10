bl_info = {
    "name": "VV_Tools",
    "author": "Vianvolaeus",
    "version": (0, 4, 3),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > VV",
    "description": "General toolkit, mainly for automating short processes.",
    "warning": "Potentially unstable, documentation incomplete.",
    "doc_url": "https://github.com/Vianvolaeus/VVtools",
    "category": "General",
}

import bpy
import os
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, PointerProperty, BoolProperty
from bpy.utils import previews

icon_collection = None

# Register icons, incomplete, but not code-breaking. Finish later

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

# Draw submenu and menu for header. NEW OPERATORS SHOULD BE ADDED HERE AS WELL AS CLASS REGISTRY. 

class TOPBAR_MT_custom_sub_menu(bpy.types.Menu):
    bl_label = "VV Tools Submenu"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.add_visual_geometry")
        layout.operator("vv_tools.rename_data_blocks")
        layout.operator("vv_tools.set_modifiers_visibility")
        layout.operator("vv_tools.merge_to_active_bone")
        layout.operator("vv_tools.reload_textures_of_selected")
        layout.operator("vv_tools.vrc_analyse")
        #Add more operators here as required

class TOPBAR_MT_custom_menu(bpy.types.Menu):
    bl_label = "VV Tools"
    
    def draw(self, context):
        layout = self.layout
        layout.menu("TOPBAR_MT_custom_sub_menu")

    def menu_draw(self, context):
        self.layout.menu("TOPBAR_MT_custom_menu")

classes = (TOPBAR_MT_custom_sub_menu, TOPBAR_MT_custom_menu)


# Operators below. Probably should sort these out into some logical order, or into categories if possible


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

def delete_bones(obj, bones):
    bpy.ops.object.mode_set(mode='POSE')
    
    for bone in bones:
        bpy.context.active_bone.select = False
        bone.bone.select = True
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.delete()
    bpy.ops.object.mode_set(mode='POSE')


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

    # Find the mesh object associated with the armature
    mesh_obj = None
    for ob in context.scene.objects:
        if ob.type == 'MESH' and ob.find_armature() == obj:
            mesh_obj = ob
            break

    if mesh_obj is None:
        return {"ERROR"}, "No mesh object found with the active armature as its modifier"

    for bone in selected_bones:
        # Merge vertex weights
        if bone.name in mesh_obj.vertex_groups:
            source_group = mesh_obj.vertex_groups[bone.name]
            active_group = mesh_obj.vertex_groups.get(active_bone.name, mesh_obj.vertex_groups.new(name=active_bone.name))

            for vertex in mesh_obj.data.vertices:
                try:
                    weight = source_group.weight(vertex.index)
                    active_group.add([vertex.index], weight, 'ADD')
                except RuntimeError:
                    pass

            mesh_obj.vertex_groups.remove(source_group)

    delete_bones(obj, selected_bones)

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
### Naturally this will be prone to inaccuracies as some things don't directly translate. It currently is limited to Poor or below. 

def analyze_selected_objects():
    import bpy

    statistics = {
        'polygons': 0,
        'texture_memory': 0,
        'skinned_meshes': 0,
        'meshes': 0,
        'material_slots': 0,
        'bones': 0,
    }

    # Iterate through selected objects
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            statistics['polygons'] += len(obj.data.polygons)
            statistics['material_slots'] += len(obj.material_slots)

            if any(mod for mod in obj.modifiers if mod.type == 'ARMATURE'):
                statistics['skinned_meshes'] += 1
            else:
                statistics['meshes'] += 1

            # Estimate texture memory
            for mat_slot in obj.material_slots:
                if mat_slot.material:
                    for node in mat_slot.material.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            img = node.image
                            if img:
                                statistics['texture_memory'] += img.size[0] * img.size[1] * 4
                                
        elif obj.type == 'ARMATURE':
            statistics['bones'] += len(obj.data.bones)

    return statistics

class VVTools_OT_VRCAnalyse(Operator):
    bl_idname = "vv_tools.vrc_analyse"
    bl_label = "VRC Analyse"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        result = analyze_selected_objects()
        context.scene["VRC_Analysis_Results"] = result
        return {"FINISHED"}

max_values = {
    'polygons': 69999,
    'texture_memory': 536870912,
    'skinned_meshes': 16,
    'meshes': 24,
    'material_slots': 32,
    'bones': 400,
}

# New functions can be added here. Keep this line for organisation haha

#Final side panel, top menu / register classes

class VVTools_PT_Panel(Panel):
    bl_idname = "VV_TOOLS_PT_panel"
    bl_label = "VV Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.add_visual_geometry")
        layout.operator("vv_tools.rename_data_blocks")
        layout.operator("vv_tools.set_modifiers_visibility")
        layout.operator("vv_tools.merge_to_active_bone")
        layout.operator("vv_tools.reload_textures_of_selected")

class VVTools_PT_VRCAnalysis(Panel):
    bl_idname = "VVTools_PT_vrc_analysis"
    bl_label = "VV Tools - VRC"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    def draw(self, context):
        layout = self.layout

        # Create a button to perform VRC Analysis
        layout.operator("vv_tools.vrc_analyse")

        # Check if the results are available and display them
        if "VRC_Analysis_Results" in context.scene:
            results = context.scene["VRC_Analysis_Results"]
            for key, value in results.items():
                row = layout.row()
                row.label(text=f"{key.capitalize()}: {value}/{max_values[key]}")


def register():
    bpy.utils.register_class(VVTools_OT_VisGeoShapeKey)
    bpy.utils.register_class(VVTools_OT_RenameDataBlocks)
    bpy.utils.register_class(VVTools_OT_SetModifiersVisibility)
    bpy.utils.register_class(VVTools_OT_MergeToActiveBone)
    bpy.utils.register_class(VVTools_OT_ReloadTexturesOfSelected)
    bpy.utils.register_class(VVTools_OT_VRCAnalyse)
    bpy.utils.register_class(VVTools_PT_VRCAnalysis)
    bpy.utils.register_class(VVTools_PT_Panel)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_custom_menu.menu_draw)


def unregister():
    bpy.utils.unregister_class(VVTools_OT_VisGeoShapeKey)
    bpy.utils.unregister_class(VVTools_OT_RenameDataBlocks)
    bpy.utils.unregister_class(VVTools_OT_SetModifiersVisibility)
    bpy.utils.unregister_class(VVTools_OT_MergeToActiveBone)
    bpy.utils.unregister_class(VVTools_OT_ReloadTexturesOfSelected)
    bpy.utils.unregister_class(VVTools_OT_VRCAnalyse)
    bpy.utils.unregister_class(VVTools_PT_VRCAnalysis)
    bpy.utils.unregister_class(VVTools_PT_Panel)
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_custom_menu.menu_draw)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

# internal tag applied to operators since we draw a top menu and submenu, things will be categorized in search nicely