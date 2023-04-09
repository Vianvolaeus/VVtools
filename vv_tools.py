bl_info = {
    "name": "VV_Tools",
    "author": "Vianvolaeus",
    "version": (0, 4, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > VV",
    "description": "General toolkit, mainly for automating short processes.",
    "warning": "UNSTABLE! Documentation not yet live.",
    "doc_url": "https://vianvolae.us/",
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

# Draw submenu and menu for header

class TOPBAR_MT_custom_sub_menu(bpy.types.Menu):
    bl_label = "VV Tools Submenu"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.add_visual_geometry")
        layout.operator("vv_tools.rename_data_blocks")
        layout.operator("vv_tools.set_modifiers_visibility")
        layout.operator("vv_tools.merge_to_active_bone")
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


# New functions can be added here. 

#Final side panel / register

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


def register():
    bpy.utils.register_class(VVTools_OT_VisGeoShapeKey)
    bpy.utils.register_class(VVTools_OT_RenameDataBlocks)
    bpy.utils.register_class(VVTools_OT_SetModifiersVisibility)
    bpy.utils.register_class(VVTools_OT_MergeToActiveBone)
    bpy.utils.register_class(VVTools_PT_Panel)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_custom_menu.menu_draw)


def unregister():
    bpy.utils.unregister_class(VVTools_OT_VisGeoShapeKey)
    bpy.utils.unregister_class(VVTools_OT_RenameDataBlocks)
    bpy.utils.unregister_class(VVTools_OT_SetModifiersVisibility)
    bpy.utils.unregister_class(VVTools_OT_MergeToActiveBone)
    bpy.utils.unregister_class(VVTools_PT_Panel)
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_custom_menu.menu_draw)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

# internal tag applied to operators since we draw a top menu and submenu, things will be categorized in search nicely