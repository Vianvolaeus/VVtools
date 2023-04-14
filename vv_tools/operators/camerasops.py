import bpy
import re
from mathutils import Vector
from bpy.types import Operator

class VVTools_OT_AddViewportCamera(Operator):
    bl_idname = "vv_tools.add_viewport_camera"
    bl_label = "Add Viewport Camera"
    bl_description = "Add a new camera named 'Viewport Camera', set it as active, align it to the current viewport view, and set up an Empty as its Depth of Field object."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'

    def execute(self, context):
    
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Change the view from camera view to a regular 3D view
        for space in context.area.spaces:
            if space.type == 'VIEW_3D':
                space.region_3d.view_perspective = 'PERSP'
    
        # Create a new camera and set it as the active camera
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
        camera.name = "Viewport Camera.001" # Add .001 suffix so empty naming doesn't break later and result in off-by-one on the initial camera
        bpy.context.scene.camera = camera

        # Set camera passepartout
        camera.data.passepartout_alpha = 1

        # Align the camera to the current viewport view
        bpy.ops.view3d.camera_to_view()

        # Set the camera type based on the viewport perspective
        rv3d = context.space_data.region_3d
        is_persp = rv3d.window_matrix[3][3] == 0 # is_perspective was producing weird results, and we can't is_orthographic_side_view doesn't account for user orthographic view so gotta do this
        if is_persp:
            camera.data.type = 'PERSP'
            camera.data.dof.use_dof = True # Enable DoF for perspective cams only, since orthos obviously blur the fuck out of everything
        else:
            camera.data.type = 'ORTHO'
            camera.data.dof.use_dof = False

        # Set the orthographic scale of the camera to match the viewport zoom level
        if camera.data.type == 'ORTHO':
            camera.data.ortho_scale = context.space_data.region_3d.view_distance

        # Create a new Empty object
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        empty = bpy.context.active_object
        empty.name = "DoF Empty"

        # Set depth of field settings. actual DoF is handled 
        camera.data.dof.aperture_fstop = 1.2
        camera.data.dof.focus_object = empty

        # Parent the Empty object to the camera
        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(True)
        camera.select_set(True)
        context.view_layer.objects.active = camera
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        # Set suffix of empty (.XXX) to match it's parent camera, or it becomes 'DoF Empty'
        
        suffix_match = re.search(r'\.\d{3}$', camera.name)
        if suffix_match:
            suffix = suffix_match.group(0)
        else:
            suffix = ''

        # Set the name of the empty based on the parent camera suffix
        empty.name = f"DoF Empty{suffix}"
        
        # Set the name of the empty based on the parent camera name
        if 'Viewport Camera' in camera.name:
            empty.name = camera.name.replace('Viewport Camera', 'DoF Empty')
        else:
            empty.name = "DoF Empty"

        # Project a ray from the camera to find the first face it touches
        context = bpy.context
        depsgraph = context.evaluated_depsgraph_get()

        origin = camera.location
        direction = camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
        result, location, normal, index, obj, matrix = context.scene.ray_cast(depsgraph, origin, direction)

        # Move the Empty object to the position of the first face touched by the projected ray
        if result:
            empty.location = location

        # Move objects to the 'Viewport Camera' collection
        coll_name = "Viewport Camera"
        if coll_name not in bpy.data.collections:
            viewport_camera_collection = bpy.data.collections.new(coll_name)
            bpy.context.scene.collection.children.link(viewport_camera_collection)
        else:
            viewport_camera_collection = bpy.data.collections[coll_name]

        # Move camera and empty to the collection
        current_collection = camera.users_collection[0]
        current_collection.objects.unlink(camera)
        current_collection.objects.unlink(empty)
        viewport_camera_collection.objects.link(camera)
        viewport_camera_collection.objects.link(empty)
        
        # Enable Depth of Field in the Viewport for Solid mode, even if we're in lookdev etc. 
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].shading.use_dof = True

        return {'FINISHED'}
        

# Camera Switch
## Two functions to cycle between cameras

class VVTools_OT_SwitchToNextCamera(Operator):
    bl_idname = "vv_tools.switch_to_next_camera"
    bl_label = "Next Camera"
    bl_description = "Switch to the next camera in the scene."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        cameras = [obj for obj in context.scene.objects if obj.type == 'CAMERA']
        if not cameras:
            self.report({'WARNING'}, "No cameras found in the scene")
            return {'CANCELLED'}

        current_camera = context.scene.camera
        idx = cameras.index(current_camera)
        next_idx = (idx + 1) % len(cameras)
        context.scene.camera = cameras[next_idx]

        return {'FINISHED'}


class VVTools_OT_SwitchToPreviousCamera(Operator):
    bl_idname = "vv_tools.switch_to_previous_camera"
    bl_label = "Previous Camera"
    bl_description = "Switch to the previous camera in the scene."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        cameras = [obj for obj in context.scene.objects if obj.type == 'CAMERA']
        if not cameras:
            self.report({'WARNING'}, "No cameras found in the scene")
            return {'CANCELLED'}

        current_camera = context.scene.camera
        idx = cameras.index(current_camera)
        prev_idx = (idx - 1) % len(cameras)
        context.scene.camera = cameras[prev_idx]

        return {'FINISHED'}
        

classes = [
    VVTools_OT_AddViewportCamera,
    VVTools_OT_SwitchToNextCamera,
    VVTools_OT_SwitchToPreviousCamera,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

