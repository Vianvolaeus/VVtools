Adding new functions to the VVTools addon should follow the following process:
(assuming simple button function)

- Define or create a new category for the function (Camera, Mesh Operator, etc) 

- Define and complete the operator class code, and add to the category Operators.py file (camerasops.py, etc)

import (required modules)
---

class VVTOOLS_OT_ExampleOperator(bpy.types.Operator):
    bl_idname = "vv_tools.example_operator"
    bl_label = "Example Operator"
    bl_description = "An example operator, not actually functional."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}


The bl_idname of the operator will need to be added to: 

- The TOPMENU file for the associated category (camerasmenu.py):

class TOPBAR_MT_VV_Example(bpy.types.Menu):
    bl_label = "Example"
    bl_idname = "TOPBAR_MT_VV_Example"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.example_operator")

- The Panel file for the associated category (cameraspanel.py, etc):
(note, the bl_label needs the "VV Tools -" prefix) 
class VVTools_PT_Example_Panel(Panel):
    bl_idname = "VV_TOOLS_PT_Example_Operator"
    bl_label = "VV Tools - Example"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VV"

    def draw(self, context):
        layout = self.layout
        layout.operator("vv_tools.example_operator")
		
TL;DR: Create operator code in (category)ops.py, reference in (category)menu.py, reference in (category)panel.py using bl_info code