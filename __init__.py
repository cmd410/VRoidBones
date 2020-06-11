'''
A simple script addon for Blender 
to rename bones in armature imported from VRoid Studio
so it mathces with Blender bone symmetry naming.
'''

import bpy

bl_info = {
    "name": "VRoid Studio Bone Renamer",
    "description": "Renames bones in armature imported from VRoid Studio so it mathces with Blender bone symmetry naming",
    "author": "Crystal Melting Dot",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "category": "Rigging",
}

def rename_bones():
    bones = bpy.context.selected_editable_bones
    if not bones:
        return
    for bone in bones[:]:
        parts = bone.name.split('_')
        if not len(parts) >= 2:
            continue
        side = parts[-2]
        name = parts[-1]
        if side not in {'R', 'L'}:
            continue
        bone.name = f'{name}_{side}'


class RenameOperator(bpy.types.Operator):
    '''Rename symmetrical VRoid bones to blender convention.'''
    bl_idname = "bones.rename_vroid"
    bl_label = "Rename Vroid bones"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_editable_bones')
    
    def execute(self, context):
        rename_bones()
        return {'FINISHED'}
    
class VRoidBonesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_vroid_panel"
    bl_label = "VRoid Bones"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "armature_edit"

    def draw(self, context):
        self.layout.operator('bones.rename_vroid')


def register():
    bpy.utils.register_class(RenameOperator)
    bpy.utils.register_class(VRoidBonesPanel)

def unregister():
    bpy.utils.unregister_class(VRoidBonesPanel)
    bpy.utils.unregister_class(RenameOperator)

if __name__ == "__main__":
    register()