# Main __init__.py - this is where we determine addon info, import all the main py modules so everything else works, then import everything from the rest of the folder structure.

bl_info = {
    "name": "VV_Tools",
    "author": "Vianvolaeus",
    "version": (0, 7, 0), # Refactor update
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > VV",
    "description": "General toolkit, mainly for automating short processes.",
    "warning": "Potentially unstable, documentation incomplete.",
    "doc_url": "https://github.com/Vianvolaeus/VVtools",
    "category": "General",
}

import bpy
import os
import sys
import importlib
import textwrap
import re
import json
import math
import mathutils

from bpy.types import Panel, Operator, PropertyGroup, Object
from bpy.props import StringProperty, PointerProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty
from bpy.utils import previews
from mathutils import Vector

from .menus import topbar
from .menus import camerasmenu
from .menus import generalmenu
from .menus import materialsmenu
from .menus import meshoperatorsmenu
from .menus import riggingmenu
from .menus import vrcmenu
from .operators import camerasops
from .operators import generalops
from .operators import materialsops
from .operators import meshoperatorsops
from .operators import riggingops
from .operators import vrcanalysisops
from .panels import cameraspanel
from .panels import generalpanel
from .panels import materialspanel
from .panels import meshoperatorspanel
from .panels import riggingpanel
from .panels import vrcanalysispanel


modules = [

    topbar,
    camerasmenu,
    generalmenu,
    materialsmenu,
    meshoperatorsmenu,
    riggingmenu,
    vrcmenu,
    camerasops,
    generalops,
    materialsops,
    meshoperatorsops,
    riggingops,
    vrcanalysisops,
    cameraspanel,
    generalpanel,
    materialspanel,
    meshoperatorspanel,
    riggingpanel,
    vrcanalysispanel,

]

def register():
    bpy.types.Scene.vv_tools_source_object = bpy.props.PointerProperty(
        name="Source Object",
        type=bpy.types.Object,
        description="Object to transfer vertex weights from",
    )

    for module in modules:
        print(f"Registering {module.__name__}")
        module.register()

def unregister():
    for module in reversed(modules):
        print(f"Unregistering {module.__name__}")
        module.unregister()

    del bpy.types.Scene.vv_tools_source_object
