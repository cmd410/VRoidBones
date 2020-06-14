import bpy

def unique_constraint(bone, t):
    for constraint in bone.constraints:
        if constraint.type == t:
            return constraint
    constraint = bone.constraints.new(type=t)
    return constraint


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