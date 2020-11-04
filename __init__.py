import bpy
from .util import *
from .constraints import *


bl_info = {
    "name": "VRoid Bones",
    "description": "Make it pretty button for VRoid skeletons.",
    "author": "Crystal Melting Dot",
    "version": (1, 5),
    "blender": (2, 80, 0),
    "category": "Rigging",
    "tracker_url": "https://github.com/cmd410/VRoidBones/issues",
}

def simplify_symmetrize_names():
    '''Rename bones to blenders armature symmetry names'''
    settings = bpy.context.scene.vroid_params
    bones = bpy.context.active_object.data.edit_bones
    n = 1
    vg_remap = dict()
    for bone in bones[:]:
        original_name = bone.name
        if bone.name.startswith('HairJoint-') and settings.simplify_names:
            bone.name = f'HairJoint_{n}'
            vg_remap[original_name] = bone.name
            n += 1
            continue
        parts = bone.name.split('_')
        if len(parts) <= 2:
            continue
        side = parts[-2]
        name = parts[-1]
        if side not in {'R', 'L'}:
            if settings.simplify_names and name != 'end': 
                bone.name = name
                vg_remap[original_name] = bone.name
            continue
        if settings.symmetrize: 
            bone.name = f'{name}_{side}'
            vg_remap[original_name] = bone.name
    
    # Need to make sure all vertex groups are properly renamed
    # they are not renamed automaticaly all the times for some reason
    armature = bpy.context.object
    children = get_children(armature)
    for obj in children:
        vgs = obj.vertex_groups
        for orig, new in vg_remap.items():
            group = vgs.get(orig)
            if group is not None:
                group.name = new


def fix_bones_chains():
    '''Put tails of bones in chain to the head of child bone
       And connect them properly...'''

    def disconnect_child(bone):
        bone.use_connect = False
    
    bpy.ops.armature.select_all(action='DESELECT')
    bones = bpy.context.active_object.data.edit_bones
    exceptions = ['Sleeve','Skirt','Bust','FaceEye',
                  'HairJoint', 'Tops', 'Food', 'Hood']
    for bone in bones:
        children = bone.children
        if not children:
            continue
        target = children[0]
        chosen = True
        if len(children) > 1:
            chosen = False
            for candidate in children:
                valid = True
                for ex in exceptions:
                    if ex in candidate.name: 
                        disconnect_child(candidate)
                        valid = False
                        break
                if valid:
                    target = candidate
                    chosen = True
                    break
        if not chosen: continue
        if bone.name.startswith('Hand_'):
            continue
        bone.select_tail = True
        offset = target.head - bone.tail
        bpy.ops.transform.translate(value=offset)
        bone.select_tail = False

        if bone.name.lower() == 'root': 
            bone.select_tail = True
            bpy.ops.transform.translate(value=(0,0,-bone.length * 0.8))
            bone.select_tail = False
            continue
        # Connect bones
        bones.active = bone
        target.select = True
        bpy.ops.armature.parent_set(type='CONNECTED')
        bpy.ops.armature.select_all(action='DESELECT')


def clear_leaf_bones():
    '''Delete all leaf bones that don't really do anything'''
    bpy.ops.armature.select_all(action='DESELECT')
    found_leafs = set()
    for bone in bpy.context.active_object.data.edit_bones:
        children = bone.children
        if not children and bone.name.endswith('_end') and not bone_has_effect(bone):
            found_leafs.add(bone.name)
            bone.select = True
            bpy.ops.armature.delete()
        if bone.name.startswith('HairJoint') and not bone.children and not bone_has_effect(bone):
            found_leafs.add(bone.name)
            bone.select = True
            bpy.ops.armature.delete()
    armature = bpy.context.object
    children = get_children(armature)
    for obj in children:
        for name in found_leafs:
            vg = obj.vertex_groups.get(name)
            if vg is not None:
                obj.vertex_groups.remove(vg)


class VRoidSettings(bpy.types.PropertyGroup):
    symmetrize: bpy.props.BoolProperty(name="Fix symmetry", default=True,
                                       description="Rename bones to match blenders symmetry naming")
    bone_chains: bpy.props.BoolProperty(name="Fix bone chains", default=True,
                                        description="Connect bones in chains, i.e. arms, legs, fingers, etc..")
    leaf_bones: bpy.props.BoolProperty(name="Remove leaf bones", default=True,
                                       description="Remove leaf bones at the end of chains")
    simplify_names: bpy.props.BoolProperty(name="Simplify bones names", default=True,
                                           description="Leave only meaningful parts of bones' names")


class VRoidFixOperator(bpy.types.Operator):
    '''Rename symmetrical VRoid bones to blender convention.'''
    bl_idname = "bones.vroid_fix"
    bl_label = "Fix Armature"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_ARMATURE'
    
    def execute(self, context):
        settings = bpy.context.scene.vroid_params
        if settings.symmetrize or settings.simplify_names: 
            simplify_symmetrize_names()
        if settings.bone_chains: 
            fix_bones_chains()
        if settings.leaf_bones: 
            clear_leaf_bones()
        self.report({'INFO'}, 'Armature was fixed!')
        return {'FINISHED'}


class VRoidIKOperator(bpy.types.Operator):
    '''Auto setup inverse kinematics for arms and legs'''
    bl_idname = "bones.vroid_ik"
    bl_label = "Setup IK"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_ARMATURE'
    
    def execute(self, context):
        setup_ik()
        self.report({'INFO'}, 'IK was setup!')
        return {'FINISHED'}


class VRoidFingersOperator(bpy.types.Operator):
    '''Auto setup Fingers constraints'''
    bl_idname = "bones.vroid_fingers"
    bl_label = "Add fingers constraints"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_ARMATURE'
    
    def execute(self, context):
        add_finger_constraitns()
        self.report({'INFO'}, 'Finger constraints were setup!')
        return {'FINISHED'}


class VRoidLimitsOperator(bpy.types.Operator):
    '''Auto setup Rotation Limits for bones'''
    bl_idname = "bones.vroid_rotlimits"
    bl_label = "Add Rotation limits"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_ARMATURE'
    
    def execute(self, context):
        add_rotation_limits()
        self.report({'INFO'}, 'Rotation limits were added!')
        return {'FINISHED'}


class VRoidCleanerOperator(bpy.types.Operator):
    '''Remove all bones that dont have effect'''
    bl_idname = "bones.vroid_cleanup"
    bl_label = "Clean skeleton"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_ARMATURE'
    
    def execute(self, context):
        def check_chain(root):
            children = root.children
            junk = list()
            if bone_has_effect(root): return [None]
            junk.append(root)
            for i in children:
                c = check_chain(i)
                junk.extend(c)
                if c is None:
                    break
            return junk

        found_junk = set()
        for bone in bpy.context.active_object.data.edit_bones:
            if bone_has_effect(bone): continue
            chain = check_chain(bone)
            if not all([i is not None for i in chain]): continue
            for i in chain:
                found_junk.add(i.name)
                i.select = True
                bpy.ops.armature.delete()
        armature = bpy.context.object
        children = get_children(armature)
        for obj in children:
            for name in found_junk:
                vg = obj.vertex_groups.get(name)
                if vg is not None:
                    obj.vertex_groups.remove(vg)

        self.report({'INFO'}, 'Cleanup complete!')
        return {'FINISHED'}


class VRoidBonesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_vroid_panel"
    bl_label = "VRoid Bones"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "armature_edit"

    def draw(self, context):
        big_box = self.layout.box()
        settings = bpy.context.scene.vroid_params
        box = big_box.box()
        box.label(text="Naming")
        box.prop(settings, "symmetrize")
        box.prop(settings, "simplify_names")

        box = big_box.box()
        box.label(text="Structure")
        box.prop(settings, "leaf_bones")
        box.prop(settings, "bone_chains")

        big_box.operator('bones.vroid_fix')
        big_box.operator('bones.vroid_ik')
        big_box.operator('bones.vroid_fingers')
        big_box.operator('bones.vroid_rotlimits')
        big_box.operator('bones.vroid_cleanup')


classes = [
    VRoidFixOperator,
    VRoidIKOperator,
    VRoidFingersOperator,
    VRoidLimitsOperator,
    VRoidCleanerOperator,
    VRoidBonesPanel,
    VRoidSettings
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.vroid_params = bpy.props.PointerProperty(type=VRoidSettings)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
