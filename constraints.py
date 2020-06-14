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
    fingers = [
        'Thumb', 
        'Index', 
        'Middle',
        'Ring', 
        'Little'
        ]
    
    apply_edit_bones()
    for finger, num, side in product(fingers, [2, 3], ['L', 'R']):
        bone = get_pose_bone(f'{finger}{num}_{side}')
        if bone is None: continue
        constraint = unique_constraint(bone, 'COPY_ROTATION')
        constraint.target = bpy.context.object
        constraint.subtarget = get_pose_bone(f'{finger}{num - 1}_{side}').name
        constraint.mix_mode = 'ADD'
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        constraint.use_y = False
        if finger == 'Thumb':
            constraint.use_x = False
        else:
            constraint.use_z = False