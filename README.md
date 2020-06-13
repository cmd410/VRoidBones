# VRoidBones for Blender
Blender's "make it pretty" button for armatures imported from VRoidStudio.

----

> Look at this armature this is ugly as hell!!

![](./imgs/before.png)

> But... with a single button press it becomes nice and pretty

![](./imgs/after.png)

## Installation

1. Download latest release from [releases page](https://github.com/cmd410/VRoidBonesRenamer/releases)
2. Open Blender 2.8 or higher
3. Navigate to `edit -> preferences -> addons`
4. Click `Install...` button and choose the downloaded zip archive
5. Check `VRoid Bones` addon in the list
6. Enjoy!

## Usage

First of all you need a model from VRoidStudio. Make whatever character you want and export it in `.vrm` format. Then rename exported file to `[whatever].glb` . Now you can import it into blender with GLTF/GLB importer. After you do that, select character's armature and go into edit mode. In the `N` Panel you can find a `Misc` tab where all the addon's controls are. By default it does full cleanup and does not require changing a thing, just press `Fix Armature` button.