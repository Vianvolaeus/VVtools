# main init.py

bl_info = {
    "name": "VV_Tools",
    "author": "Vianvolaeus",
    "version": (0, 6, 0),
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
import math
import mathutils

from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, PointerProperty, BoolProperty, IntProperty, FloatProperty
from bpy.utils import previews
from mathutils import Vector

from .operators import (
    VVTools_OT_MergeToActiveBone,
    VVTools_OT_SmoothRigXfer,
    # VVTools_PT_Rigging  # Remove this line
)

from .panels import (
    VVTools_PT_Rigging
)

classes = [
    VVTools_OT_MergeToActiveBone,
    VVTools_OT_SmoothRigXfer,
    VVTools_PT_Rigging,
]

classes = [
    VVTools_OT_MergeToActiveBone,
    VVTools_OT_SmoothRigXfer,
    VVTools_PT_Rigging,
    
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # ... other register code ...

def unregister():
    # ... other unregister code ...
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()