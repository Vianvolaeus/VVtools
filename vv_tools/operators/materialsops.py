#operators/materialsops.py

import bpy
from bpy.types import Operator

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
        removed_count = 0
        for i, mat_slot in reversed(list(enumerate(obj.material_slots))):
            if i not in used_materials:
                obj.active_material_index = i
                bpy.ops.object.material_slot_remove({'object': obj})
                removed_count += 1

        return removed_count

    def execute(self, context):
        total_removed = 0
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                total_removed += self.remove_unused_materials(obj)

        self.report({"INFO"}, f"{total_removed} unused materials removed")
        return {"FINISHED"}

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


class VVTools_OT_ReloadTexturesOfSelected(Operator):
    bl_idname = "vv_tools.reload_textures_of_selected"
    bl_label = "Reload Textures of Selected"
    bl_description = "Reload all textures in materials of the selected objects. WARNING! Can run slow."
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def reload_textures(self, objects):
        for obj in objects:
            for slot in obj.material_slots:
                if slot.material:
                    for node in slot.material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            node.image.reload()

    def execute(self, context):
        selected_objects = context.selected_objects
        self.reload_textures(selected_objects)
        return {"FINISHED"}



# Class list for registration in __init__.py
classes = [
    VVTools_OT_RemoveUnusedMaterials,
    VVTools_OT_ReloadTexturesOfSelected,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
