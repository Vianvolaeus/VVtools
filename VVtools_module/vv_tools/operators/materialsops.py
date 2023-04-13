import bpy

class VVTools_OT_RemoveUnusedMaterials(bpy.types.Operator):
    bl_idname = "vv_tools.remove_unused_materials"
    bl_label = "Remove Unused Materials"
    bl_description = "Removes all unused materials from the current .blend file"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        materials = bpy.data.materials
        unused_materials = [mat for mat in materials if mat.users == 0]

        for mat in unused_materials:
            materials.remove(mat)

        self.report({"INFO"}, f"{len(unused_materials)} unused materials removed")
        return {"FINISHED"}


class VVTools_OT_ReloadTexturesOfSelected(bpy.types.Operator):
    bl_idname = "vv_tools.reload_textures_of_selected"
    bl_label = "Reload Textures of Selected"
    bl_description = "Reloads all textures of the materials assigned to the selected objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected_objects = context.selected_objects
        textures_reloaded = 0

        for obj in selected_objects:
            if obj.type == "MESH":
                for mat_slot in obj.material_slots:
                    if mat_slot.material:
                        for tex_slot in mat_slot.material.texture_slots:
                            if tex_slot and tex_slot.texture:
                                tex_slot.texture.reload()
                                textures_reloaded += 1

        self.report({"INFO"}, f"{textures_reloaded} textures reloaded")
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
