# VVtools
General Blender toolkit, for automating some short processes. 

Addon should be currently be considered experimental, in progress, incomplete.

![](https://github.com/Vianvolaeus/VVtools/blob/assets/vv_tools_header.jpg)

## Installation
Download the latest release, and install th .py as usual (will replace this with quick visual, but it's like every other Blender addon lol). 
Haven't tested versions except 3.0+, but *should* be 2.8+ compatible

## Usage 

The addon currently lives in a top header menu, as well as the side panel. 
Operators can also be called via the search function (F3) - using 'vv' in the search should bring everything up!

## General Operators

### Visual Geo to Shape

Takes a Visual Geometry to Mesh snapshot of the selected object and merges it into the active object.
This is mainly useful for keeping active modifiers while using them to deform geometry. It is effectively similar to the 'Save As Shape Key' function found in some modifiers, but for everything active on the mesh. Quite literally it is Visual Geometry to Shape Key.

Obviously, since it is shapekeys, you cannot use modifiers that change vertex count / poly count etc, so not all modifiers will work. 

### Toggle Modifiers Visibility

Switches state of modifier enable in both Viewport and Render mode at the same time. It is a bool on/off switch, so will enable and disable *every* modifier on the active object(s). 

Mainly useful after using Visual Geo to Shape operator above, but also good for disabling stray modifiers pre-render, etc. 

### Object Name Data Block Rename

Renames the Data Block of the associated object using the Object name of the active object(s). 
This is mainly used for cleanup for exporting assets etc. No more 'Cube.003', etc - this operator takes the Object name to change that. 

### Merge Bones to Active
Pose Mode operator used to merge down / dissolve bones *with their weights* down to an active bone.
This can be useful for reducing hair chains in characters, dissolving twist bones, things like that. 

### Reload Textures of Selected
Will reload the textures of every currently selected object. Useful for external texture authorship (eg. Substance) - will refresh Image Texture nodes if they have been altered in the original directory. 

## VRChat Operators

### VRC Analyse
An analysis tool for VRChat avatars. It analyses the current selected objects against relevant / compatible PC [VRchat Avatar Performance Limits](https://docs.vrchat.com/docs/avatar-performance-ranking-system#pc-limits).
Currently, this checks the following:

- Polygons
- Texture Memory
- Skinned Meshes 
- Meshes
- Material Slots
- Bones

If something is pushing the selected objects into the Very Poor Performance Rank, the UI will report what it is, with a mild suggestion on a fix. 

NOTE: Currently, the performance stats are hard-coded, so if there are updates to them, they could be incorrect if the code is not changed accordingly. 