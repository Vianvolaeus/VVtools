# VVtools
General Blender toolkit, for automating some short processes. 

Addon should be currently be considered experimental, in progress, incomplete.

![](https://github.com/Vianvolaeus/VVtools/blob/assets/vv_tools_header.jpg)

## Support
I'm yet to make a cent off of my free, public work, and I'm fairly confident that they've been helpful - if you've got a couple coffee dollars to spare, i'd appreciate it!
https://ko-fi.com/vianvolaeus

## Installation
Download the latest release, install the vv_tools.zip in the add-ons section of your Blender Preferences menu.  
 
(Haven't tested versions except 3.0+, but *should* be 2.8+ compatible)

## Usage 

VV Tools operators can be use with 3 methods. 
- Top header menu, (next to where you select your tabs (Layout, etc) which subcategorises everything, like ordinary Blender menus.
- Side panel menu, sometimes called n-panel, where most addons tend to live. Categorized into different functions. 
- Search (default F3). Simply type 'vv' or 'VV' into the search. The operators should be at the top of search. 

# Operator Categories

## General

### Object Name Data Block Rename

Renames the Data Block of the associated object using the Object name of the active object(s).

This is mainly used for cleanup for exporting assets etc. No more 'Cube.003', etc - this operator takes the Object name to change that. 

### Viewport Wireframe

Mode agnostic wireframe toggle. 
Simply enables wireframe overlay in the viewport. 

## Cameras

### Add Viewport Camera
Adds a camera using the current viewport as it's view transform, and the view mode (Perspective / Ortho) of the viewport. 
  
Passepartout (black border) is set as 1, as a personal preference.  

(This may be exposed later, but for now it's faster hardcoded)  

Generated camera will take Perspective or Orthographic into account based on your viewport when the operator is run. 

It also sets up Depth of Field with a few functions: 

- Enables DoF (with fStop1.2) for perspective cams
- Adds an Empty object as a DoF object, and parents it to camera  
- Raycasts this DoF Object to nearest surface from center of camera frame. If it misses, it'll be at origin. 
- Enables DoF in Solid mode, so you can preview your DoF effect without a full render  


(You can tweak this DoF object manually afterwards, also, just move it as desired.)

The operator will add Viewport Cameras to a Viewport Camera collection, to keep things organised. 

### Camera Switch

Side by side buttons that switch which cameras is active in your scene. 
New cameras that are added will still be compatible with this function, simply linearly runs though cameras as you press the button. 

## Mesh Operators

### Visual Geo to Shape

Takes a Visual Geometry to Mesh snapshot of the selected object and merges it into the active object.  
This is mainly useful for keeping active modifiers while using them to deform geometry.   
It is effectively similar to the 'Save As Shape Key' function found in some modifiers, but for everything active on the mesh.  
Quite literally it is Visual Geometry to Shape Key.

<!> Since it involves shapekeys, you cannot use modifiers that change vertex count / poly count etc, so not all modifiers will work. 

### Toggle Modifiers Visibility

Switches state of modifier enable in both Viewport and Render mode at the same time. It is a bool on/off switch, so will enable and disable *every* modifier on the active object(s). 

Mainly useful after using Visual Geo to Shape operator above, but also good for disabling stray modifiers pre-render, etc. 


## Rigging

### Button Attach
Snaps a selected object to an Edit Mode selection of an active object (vertex or face), and transfers either it's exact vertex weight, or uses a Data Transfer to project weights.  
Also comes with some user functions (offset from surface)  
This is useful for attaching static objects without weight painting to things that are already rigged.  
Personal use case is attaching buttons or patches to clothing, or decals and other hard surface objects to body parts (robotic arms, etc)
This will operator recieve more functionality in future. 

### Merge Bones to Active
Pose Mode operator used to merge down / dissolve bones *with their weights* down to an active bone.

This can be useful for reducing hair chains in characters, dissolving twist bones, things like that. 

### Smooth Rig Transfer

Mainly useful for clothing, this applies a Data Transfer modifier to transfer vertex weights from the Source Object, smooths them out while retaining the area of vertex weight projection, and then parents the selected objects to the Armature of the Source Object.

Personal use case: Taking unrigged clothing and projecting weights for a rigged body Source Object.

NOTE - This should work for multiple objects at the same time, if required - it is selection based.
## Materials

### Reload Textures of Selected
Will reload the textures of every currently selected object. 

Useful for external texture authorship (eg. Substance) - will refresh Image Texture nodes if they have been altered in the original directory. 

### Remove Unused Materials
Removes materials on selected objects that do not have any vertex assignment on the selected objects. 
Useful for optimizing, and ensuring unused material slots are not exported in model exports. 

## VRChat (VRC)

### VRC Analyse
A WIP analysis tool for VRChat avatars. It analyses the current *selected* objects against relevant / compatible PC [VRchat Avatar Performance Limits](https://docs.vrchat.com/docs/avatar-performance-ranking-system#pc-limits).

Running the VRC Analyse again with a new selection, or updated data, will report new analysis.

Since the analyser runs on *selected* objects, you can select a single / multiple objects to see what their contributions are to the Performance Rank individually by analysing them individually. 

Currently, this checks the following:

- Polygons (Tris)
- Texture Memory (EXPERIMENTAL)
- Skinned Meshes 
- Meshes
- Material Slots
- Bones

Texture Memory should be considered experimental, and assumes a rough calcuation for DXT5 compression rather than RGBA 32bit. It should still serve as a decent estimate. 

If the Performance Rank is detected as Very Poor, a warning will be displayed. 

# Other features

## Update check / auto update

Thanks to the lovely [blender-addon-updater module by CGCookie](https://github.com/CGCookie/blender-addon-updater), the addon has update checks, versioning and user-enabled Auto-Update.  
In the Preferences panel, you can check for updates and install different releases from this Github repo - if a new version comes out, you'll be able to install it from within Blender!
