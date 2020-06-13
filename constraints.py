def unique_constraint(bone, t):
    for constraint in bone.constraints:
        if constraint.type == t:
            return constraint
    constraint = bone.constraints.new(type=t)
    return constraint