#operators/generalops.py

import bpy
from bpy.types import Operator

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
        
classes = [
    VVTools_OT_RenameDataBlocks,
    VVTools_OT_ViewportWireframe,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)