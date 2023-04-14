#operators/meshoperatorsops.py

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

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
        
classes = [
    VVTools_OT_VisGeoShapeKey,
    VVTools_OT_SetModifiersVisibility,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)