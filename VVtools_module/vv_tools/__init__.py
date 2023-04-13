# Main __init__.py - this is where we determine addon info, import all the main py modules so everything else works, then import everything from the rest of the folder structure. 

bl_info = {
    "name": "VV_Tools",
    "author": "Vianvolaeus",
    "version": (0, 6, 1), # Update to subfolder based addon rather than one juicy script
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > VV",
    "description": "General toolkit, mainly for automating short processes.",
    "warning": "Potentially unstable, documentation incomplete.",
    "doc_url": "https://github.com/Vianvolaeus/VVtools",
    "category": "General",
}
# Import all the addon modules needed to run the code in the addon

import bpy
import os
import textwrap
import re
import json
import math
import mathutils

# Import submodules and classes within submodule

from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, PointerProperty, BoolProperty, IntProperty, FloatProperty
from bpy.utils import previews
from mathutils import Vector


# Import menu classes. These are for the drawing the functions in the top menu! We import the TOPBAR_MT_custom_menu, which is the main menu, and then it's submenus. 

from .menus import (
    TOPBAR_MT_custom_menu,
    TOPBAR_MT_VV_General,
    TOPBAR_MT_VV_Cameras, 
    TOPBAR_MT_VV_Materials,
    TOPBAR_MT_VV_Mesh_Operators,
    TOPBAR_MT_VV_Rigging,
    TOPBAR_MT_VV_VRC,
)

# Import operators (an operator is a specific task or function for an add-on)

from .operators import (
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
)

# Import panel classes from panels/(x).py. This is for drawing the side panels to be displayed in Blender. 

from .panels import (
    VVTools_PT_General,
    VVTools_PT_Cameras,
    VVTools_PT_Mesh_Operators,
    VVTools_PT_Rigging,
    VVTools_PT_Materials,
    VVTools_PT_VRCAnalysis,
)
# Full class list for addon. This is a list of all the blocks of code we've made. It includes Operator Classes (OT), Panel Classes (PT) ,and Menu Classes (MT). These are like the blueprints of 

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

# Register = adding the class to Blender, basically! When a class is registered, it means Blender can use it to do stuff with it! (Make a panel, use an operator, etc.) The code here takes the 'classes =' (list) to determine what those classes are. 

# Not sure if the pointer stuff needs to be here, lol. 

def register():
    for cls in classes:
            bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_custom_menu.menu_draw)
    bpy.types.Scene.vv_tools_source_object = bpy.props.PointerProperty(
        name="Source Object",
        type=bpy.types.Object,
        description="The source object to transfer vertex group data from"
    )
# Unregister classes. Used to remove classes, like when the addon is disabled / removed!
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_custom_menu.menu_draw)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.vv_tools_source_object
    
if __name__ == "__main__":
    register()