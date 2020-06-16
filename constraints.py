from itertools import product

import bpy

from .util import unique_constraint, get_pose_bone

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


rotation_limits = {
    'UpperLeg_L': {
        'min_x': -0.698132,
        'max_x': 1.91986,
        'min_y': -0.436332,
        'max_y': 0.436332,
        'min_z': -0.785398,
        'max_z': 1.39626
    },
    'UpperLeg_R': {
        'min_x': -0.698132,
        'max_x': 1.91986,
        'min_y': -0.436332,
        'max_y': 0.436332,
        'min_z': -0.785398,
        'max_z': 1.39626
    },
    'UpperArm_L': {
        'min_x': -2.0944,
        'max_x': 0.436332,
        'min_y': -0.872665,
        'max_y': 0.872665,
        'min_z': -2.26893,
        'max_z': 1.5708
    },
    'UpperArm_R': {
        'min_x': -2.0944,
        'max_x': 0.436332,
        'min_y': -0.872665,
        'max_y': 0.872665,
        'min_z': -1.5708,
        'max_z': 2.26893
    },
    'Spine': {
        'min_x': -0.523599,
        'max_x': 0.523599,
        'min_y': -0.523599,
        'max_y': 0.523599,
        'min_z': -0.523599,
        'max_z': 0.523599
    },
    'Chest': {
        'min_x': -0.2617995,
        'max_x': 0.2617995,
        'min_y': -0.2617995,
        'max_y': 0.2617995,
        'min_z': -0.2617995,
        'max_z': 0.2617995
    },
    'UpperChest': {
        'min_x': -0.174533,
        'max_x': 0.174533,
        'min_y': -0.174533,
        'max_y': 0.174533,
        'min_z': -0.174533,
        'max_z': 0.174533
    },
    'Neck': {
        'min_x': -0.523599,
        'max_x': 0.523599,
        'min_y': -0.523599,
        'max_y': 0.523599,
        'min_z': -0.523599,
        'max_z': 0.523599
    },
    'Head': {
        'min_x': -0.523599,
        'max_x': 0.523599,
        'min_y': -0.523599,
        'max_y': 0.523599,
        'min_z': -0.523599,
        'max_z': 0.523599
    },
    '<fingers>':{
        'min_x': -1.5708,
        'max_x': 0.139626,
        'min_y': 0,
        'max_y': 0,
        'min_z': -0.349066,
        'max_z': 0.349066
    },
    'Thumb1_L':{
        'min_x': -0.994838,
        'max_x': 0.349066,
        'min_y': 0,
        'max_y': 0,
        'min_z': -0.349066,
        'max_z': 0.523599
    },
    'Thumb1_R':{
        'min_x': -0.994838,
        'max_x': 0.349066,
        'min_y': 0,
        'max_y': 0,
        'min_z': -0.523599,
        'max_z': 0.349066
    },
    'Shoulder_L':{
        'min_x': -0.349066,
        'max_x': 0.349066,
        'min_y': -0.0872665,
        'max_y': 0.349066,
        'min_z': -0.349066,
        'max_z': 0.349066
    },
    'Shoulder_R':{
        'min_x': -0.349066,
        'max_x': 0.349066,
        'min_y': -0.349066,
        'max_y': 0.0872665,
        'min_z': -0.349066,
        'max_z': 0.349066
    },
    'Foot_L':{
        'min_x': -0.837758,
        'max_x': 0.645772,
        'min_y': -0.0523599,
        'max_y': 0.0523599,
        'min_z': -0.261799,
        'max_z': 0.261799
    },
    'Foot_R':{
        'min_x': -0.837758,
        'max_x': 0.645772,
        'min_y': -0.0523599,
        'max_y': 0.0523599,
        'min_z': -0.261799,
        'max_z': 0.261799
    }
}

fingers = [
    'Thumb', 
    'Index', 
    'Middle',
    'Ring', 
    'Little'
    ]

def apply_edit_bones():
    bpy.ops.object.posemode_toggle()   # This lines needed to "apply" bones from edit mode
    bpy.ops.object.editmode_toggle()   # or else constraints won't appear for some reason


def setup_ik():
    apply_edit_bones()

    pose_bones = bpy.context.object.pose.bones
    for bone_name, params in ik_config.items():
        
        bone = get_pose_bone(bone_name)
        if bone is None: continue

        constraint = unique_constraint(bone, 'IK')   
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


def add_finger_constraitns():
    apply_edit_bones()
    for finger, num, side in product(fingers, [2, 3], ['L', 'R']):
        bone = get_pose_bone(f'{finger}{num}_{side}')
        if bone is None: continue
        constraint = unique_constraint(bone, 'COPY_ROTATION')
        constraint.target = bpy.context.object
        constraint.subtarget = bone.parent.name
        constraint.mix_mode = 'ADD'
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        constraint.use_y = False
        if finger == 'Thumb':
            constraint.use_x = False
        else:
            constraint.use_z = False

def add_rotation_limits():
    apply_edit_bones()
    for bone_name, params in rotation_limits.items():
        if bone_name == '<fingers>':
            for finger, num, side in product(fingers, [1], ['L', 'R']):
                if finger == 'Thumb': continue
                bone = get_pose_bone(f'{finger}{num}_{side}')
                if bone is None: continue
                constraint = unique_constraint(bone, 'LIMIT_ROTATION')
                constraint.owner_space = 'LOCAL'
                constraint.use_transform_limit = True
                for p_name, p_value in params.items():
                    setattr(constraint, p_name, p_value)
                    axis = p_name.split('_')[1]
                    setattr(constraint, f'use_limit_{axis}', True)
        bone = get_pose_bone(bone_name)
        if bone is None: continue
        constraint = unique_constraint(bone, 'LIMIT_ROTATION')
        constraint.owner_space = 'LOCAL'
        constraint.use_transform_limit = True
        for p_name, p_value in params.items():
            setattr(constraint, p_name, p_value)
            axis = p_name.split('_')[1]
            setattr(constraint, f'use_limit_{axis}', True)