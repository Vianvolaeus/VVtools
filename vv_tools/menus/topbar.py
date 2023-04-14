import bpy
from bpy.types import Menu

class TOPBAR_MT_custom_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_custom_menu"
    bl_label = "VV Tools"

    def draw(self, context):
        layout = self.layout
        layout.menu("TOPBAR_MT_VV_General")
        layout.menu("TOPBAR_MT_VV_Cameras")
        layout.menu("TOPBAR_MT_VV_Materials")
        layout.menu("TOPBAR_MT_VV_Mesh_Operators")
        layout.menu("TOPBAR_MT_VV_Rigging")
        layout.menu("TOPBAR_MT_VV_VRC")


def menu_draw_func(self, context):
    layout = self.layout
    layout.menu(TOPBAR_MT_custom_menu.bl_idname)

classes = [
    TOPBAR_MT_custom_menu,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(menu_draw_func)

def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(menu_draw_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
