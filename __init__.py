import bpy

bl_info = {
    "name": "VRoid Bones",
    "description": "Make it pretty button for VRoid skeletons.",
    "author": "Crystal Melting Dot",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "category": "Rigging",
    "tracker_url": "https://github.com/cmd410/VRoidBonesRenamer/issues",
}

ik_config = {
    'LowerArm_L': {
        'chain_count': 2,
        'lock_ik_y': True,
        'lock_ik_x': True,
        'use_ik_limit_z': True,
        'ik_max_z': 0,
        'ik_min_z': -2.61799
    },
    'LowerArm_R': {
        'chain_count': 2,
        'lock_ik_y': True,
        'lock_ik_x': True,
        'use_ik_limit_z': True,
        'ik_max_z': 2.61799,
        'ik_min_z': 0
    },
    'LowerLeg_L': {
        'chain_count': 2,
        'lock_ik_y': True,
        'lock_ik_z': True,
        'use_ik_limit_x': True,
        'ik_max_x': 0,
        'ik_min_x': -2.61799
    },
    'LowerLeg_R': {
        'chain_count': 2,
        'lock_ik_y': True,
        'lock_ik_z': True,
        'use_ik_limit_x': True,
        'ik_max_x': 0,
        'ik_min_x': -2.61799
    }
}

def setup_ik():
    def create_ik(bone):
        for constraint in bone.constraints:
            if constraint.type == 'IK':
                return constraint
        constraint = bone.constraints.new(type='IK')
        return constraint
    
    pose_bones = bpy.context.object.pose.bones
    for bone_name, params in ik_config.items():
        
        bone = None
        if bone_name in pose_bones:
            bone = pose_bones[bone_name]
        else:
            name, side = bone_name.split('_')
            for b in pose_bones:
                if b.name.endswith(f'{side}_{name}'):
                    bone = b
                    break
        if bone is None: continue
        
        constraint = create_ik(bone)   
        constraint.chain_count = params.get('chain_count', 0)

        bone.lock_ik_x = params.get('lock_ik_x', False)
        bone.lock_ik_y = params.get('lock_ik_y', False)
        bone.lock_ik_z = params.get('lock_ik_z', False)

        bone.use_ik_limit_x = params.get('use_ik_limit_x', False)
        bone.use_ik_limit_y = params.get('use_ik_limit_y', False)
        bone.use_ik_limit_z = params.get('use_ik_limit_z', False)

        bone.ik_max_x = params.get('ik_max_x', 3.14159)
        bone.ik_min_x = params.get('ik_min_x', -3.14159)
        bone.ik_max_y = params.get('ik_max_y', 3.14159)
        bone.ik_min_y = params.get('ik_min_y', -3.14159)
        bone.ik_max_z = params.get('ik_max_z', 3.14159)
        bone.ik_min_z = params.get('ik_min_z', -3.14159)


def simplify_symmetrize_names():
    '''Rename bones to blenders armature symmetry names'''
    settings = bpy.context.scene.vroid_params
    bones = bpy.context.active_object.data.edit_bones
    for bone in bones[:]:
        parts = bone.name.split('_')
        if len(parts) <= 2:
            continue
        side = parts[-2]
        name = parts[-1]
        if side not in {'R', 'L'}:
            if settings.simplify_names and name != 'end': bone.name = name
            continue
        if settings.symmetrize: bone.name = f'{name}_{side}'


def rename_hairjoints():
    '''Get rid of HairJoint-2rv1235ve... like nonsense names'''
    bones = bpy.context.active_object.data.edit_bones
    n = 1
    for bone in bones[:]:
        if bone.name.startswith('HairJoint-'):
            bone.name = f'HairJoint_{n}'
            n += 1

def resize_root(bone):
    bone.select_tail = True
    bpy.ops.transform.translate(value=(0,0,-bone.length * 0.8))
    bone.select_tail = False

def fix_bones_chains():
    '''Put tails of bones in chain to the head of child bone
       And connect them properly...'''
    bpy.ops.armature.select_all(action='DESELECT')
    bones = bpy.context.active_object.data.edit_bones
    for bone in bones:
        children = bone.children
        if len(children) != 1:
            continue
        bone.select_tail = True
        offset = children[0].head - bone.tail
        bpy.ops.transform.translate(value=offset)
        bone.select_tail = False
        
        # Connect bones
        if bone.name.lower() == 'root': 
            resize_root(bone)
            continue
        bones.active = bone
        children[0].select = True
        bpy.ops.armature.parent_set(type='CONNECTED')
        bpy.ops.armature.select_all(action='DESELECT')

def get_children(parent):
    l = []
    for obj in bpy.context.scene.objects:
        if obj.name == parent.name: continue
        if obj.parent.name == parent.name:
            l.append(obj)
    return l

def bone_has_effect(bone):
    '''Check if bone has vertex groups attached to it'''
    armature = bpy.context.object
    children = get_children(armature)
    for obj in children:
        me = obj.data
        vg_id = None
        for i in obj.vertex_groups:
            if i.name == bone.name:
                vg_id = i.index
                break
        if vg_id is None:
            continue
        for vertex in me.vertices:
            if i.index in list([vg.group for vg in vertex.groups]):
                return True
    return False


def clear_leaf_bones():
    '''Delete all leaf bones that don't really do anything'''
    bpy.ops.armature.select_all(action='DESELECT')
    for bone in bpy.context.active_object.data.edit_bones:
        children = bone.children
        if not children and bone.name.endswith('_end') and not bone_has_effect(bone):
            bone.select = True
            bpy.ops.armature.delete()
        if bone.name.startswith('HairJoint') and not bone.children and not bone_has_effect(bone):
            bone.select = True
            bpy.ops.armature.delete()


class VRoidSettings(bpy.types.PropertyGroup):
    symmetrize: bpy.props.BoolProperty(name="Fix symmetry", default=True,
                                       description="Rename bones to match blenders symmetry naming")
    bone_chains: bpy.props.BoolProperty(name="Fix bone chains", default=True,
                                        description="Connect bones in chains, i.e. arms, legs, fingers, etc..")
    leaf_bones: bpy.props.BoolProperty(name="Remove leaf bones", default=True,
                                       description="Remove leaf bones at the end of chains")
    hairjoints: bpy.props.BoolProperty(name="Simplify hairjoints", default=True,
                                       description="Get rid of incomprehensible long names in hairjoints")
    simplify_names: bpy.props.BoolProperty(name="Simplify all bones names", default=True,
                                           description="Leave only meaningful parts of bones' names")
    ik: bpy.props.BoolProperty(name="Setup Inverse Kinematics", default=True,
                               description="Set up inverse kinematics for arms and legs")


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
        if settings.hairjoints: 
            rename_hairjoints()
        if settings.ik:
            setup_ik()
        return {'FINISHED'}
    

class VRoidBonesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_vroid_panel"
    bl_label = "VRoid Bones"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "armature_edit"

    def draw(self, context):
        settings = bpy.context.scene.vroid_params
        box = self.layout.box()
        box.label(text="Naming")
        box.prop(settings, "symmetrize")
        box.prop(settings, "hairjoints")
        box.prop(settings, "simplify_names")

        box = self.layout.box()
        box.label(text="Structure")
        box.prop(settings, "leaf_bones")
        box.prop(settings, "bone_chains")

        box = self.layout.box()
        box.label(text="Extra")
        box.prop(settings, "ik")

        self.layout.operator('bones.vroid_fix')


classes = [
    VRoidFixOperator,
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