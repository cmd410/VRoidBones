import bpy
from .constraints import unique_constraint

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
    pose_bones = bpy.context.object.pose.bones
    for bone_name, params in ik_config.items():
        
        bone = None
        if bone_name in pose_bones:
            bone = pose_bones[bone_name]
        else:
            name, side = bone_name.split('_')
            for b in pose_bones:
                if b.name.endswith(f'_{side}_{name}'):
                    bone = b
                    break
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
