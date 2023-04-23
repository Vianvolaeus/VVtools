# Main __init__.py - this is where we determine addon info, import all the main py modules so everything else works, then import everything from the rest of the folder structure.

bl_info = {
    "name": "VV_Tools",
    "author": "Vianvolaeus",
    "version": (0, 7, 2), # Texture reload fix
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
from . import addon_updater_ops

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

# Updater prefs and panel. We're just following the demo for now and chucking it into the init. Not sure if it's correct. 

class DemoUpdaterPanel(bpy.types.Panel):
	"""Panel to demo popup notice and ignoring functionality"""
	bl_label = "Updater Demo Panel"
	bl_idname = "OBJECT_PT_DemoUpdaterPanel_hello"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS' if bpy.app.version < (2, 80) else 'UI'
	bl_context = "objectmode"
	bl_category = "Tools"

	def draw(self, context):
		layout = self.layout

		# Call to check for update in background.
		# Note: built-in checks ensure it runs at most once, and will run in
		# the background thread, not blocking or hanging blender.
		# Internally also checks to see if auto-check enabled and if the time
		# interval has passed.
		addon_updater_ops.check_for_update_background()

		layout.label(text="Demo Updater Addon")
		layout.label(text="")

		col = layout.column()
		col.scale_y = 0.7
		col.label(text="If an update is ready,")
		col.label(text="popup triggered by opening")
		col.label(text="this panel, plus a box ui")

		# Could also use your own custom drawing based on shared variables.
		if addon_updater_ops.updater.update_ready:
			layout.label(text="Custom update message", icon="INFO")
		layout.label(text="")

		# Call built-in function with draw code/checks.
		addon_updater_ops.update_notice_box_ui(self, context)


@addon_updater_ops.make_annotations
class DemoPreferences(bpy.types.AddonPreferences):
	"""Demo bare-bones preferences"""
	bl_idname = __package__

	# Addon updater preferences.

	auto_check_update = bpy.props.BoolProperty(
		name="Auto-check for Update",
		description="If enabled, auto-check for updates using an interval",
		default=False)

	updater_interval_months = bpy.props.IntProperty(
		name='Months',
		description="Number of months between checking for updates",
		default=0,
		min=0)

	updater_interval_days = bpy.props.IntProperty(
		name='Days',
		description="Number of days between checking for updates",
		default=7,
		min=0,
		max=31)

	updater_interval_hours = bpy.props.IntProperty(
		name='Hours',
		description="Number of hours between checking for updates",
		default=0,
		min=0,
		max=23)

	updater_interval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description="Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59)

	def draw(self, context):
		layout = self.layout

		# Works best if a column, or even just self.layout.
		mainrow = layout.row()
		col = mainrow.column()

		# Updater draw function, could also pass in col as third arg.
		addon_updater_ops.update_settings_ui(self, context)

		# Alternate draw function, which is more condensed and can be
		# placed within an existing draw function. Only contains:
		#   1) check for update/update now buttons
		#   2) toggle for auto-check (interval will be equal to what is set above)
		# addon_updater_ops.update_settings_ui_condensed(self, context, col)

		# Adding another column to help show the above condensed ui as one column
		# col = mainrow.column()
		# col.scale_y = 2
		# ops = col.operator("wm.url_open","Open webpage ")
		# ops.url=addon_updater_ops.updater.website


# Classes specifically in this __init__.py - actual functionality should go into modules

classes = (
	DemoPreferences,
	DemoUpdaterPanel
)

# End of updater code

def register():
    addon_updater_ops.register(bl_info)  # Keep this at top of register functions as per addon functionality recommendation
    bpy.types.Scene.vv_tools_source_object = bpy.props.PointerProperty(
        name="Source Object",
        type=bpy.types.Object,
        description="Object to transfer vertex weights from",
    )

    for cls in classes:
        bpy.utils.register_class(cls)

    for module in modules:
        print(f"Registering {module.__name__}")
        module.register()


def unregister():
    addon_updater_ops.unregister()  # Unregister first as per update functionality recommendation
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for module in reversed(modules):
        print(f"Unregistering {module.__name__}")
        module.unregister()

    del bpy.types.Scene.vv_tools_source_object

