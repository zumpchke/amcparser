import numpy as np
import cgkit.asfamc


class Bone(object):
    def __init__(self, name):
        self.name = name

        self.is_root = False
        self.parent = None
        self.child = list()

        self.axis = None
        self.dof = None
        self.local_transform = None

        self.global_transform = list()
        self.length = None
        self.direction = None
        self.offset = None

        self.position = None
        self.orientation = None

    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        self.child.append(child)

    def __str__(self):
        return "Bone: {0}".format(self.name)

    def __repr__(self):
        return self.__str__()


class Skeleton(cgkit.asfamc.ASFReader):
    def __init__(self, filename, scale=1.0):
        cgkit.asfamc.ASFReader.__init__(self, filename)
        self.filename = filename
        self.name = None
        self.root = None
        self.bones = dict()
        self.scale = scale
        self.read()

    def onRoot(self, data):
        root_bone = self._add_bone('root')
        root_bone.is_root = True
        root_bone.position = list(map(float, data['position']))
        root_bone.position = np.array(root_bone.position) * self.scale
        root_bone.orientation = np.array(data['orientation'])
        root_bone.axis = np.array(data['orientation'])
        self.root = root_bone

    def onBonedata(self, bones):
        for bonedata in bones:
            self._add_bone(bonedata['name'][0])
            self._set_bone_data(self.bones[bonedata['name'][0]], bonedata)

    def onName(self, name):
        self.name = name

    def onHierarchy(self, links):
        # Create tree hierarchy
        for link in links:
            # Create root bone
            if link[0] == "Hips" or link[0] == "hips" or link[0] == "hip":
                parent_bone = self.bones['root']
            else:
                parent_bone = self._add_bone(link[0])

            # Add all children to graph structure
            for child_name in link[1]:
                child_bone = self._add_bone(child_name)
                child_bone.set_parent(parent_bone)
                parent_bone.add_child(child_bone)

    def _set_bone_data(self, bone, bonedata):
        bone.length = float(bonedata['length'][0]) * self.scale
        bone.direction = np.array(list(map(float, bonedata['direction'])))

        bone.vector = bone.length * bone.direction

        bone.axis = bonedata['axis']

    def _add_bone(self, bone_name):
        if bone_name not in self.bones:
            self.bones[bone_name] = Bone(bone_name)
        return self.bones[bone_name]

    def dump_str(self, bone, level=0):
        print '\t' * level, bone
        level += 1
        for child in bone.child:
            self.dump_str(child, level)

    #def get_bones_until_root(self, bone_names):
    #    """Handle the case with mocap files from multiple sources
    #    where the requested bone has aliases like LeftWrist, lwrist, etc."""
    #    bones = list()
    #    bone_name = None

    #    for b in bone_names:
    #        if b in self.bones:
    #            bone_name = b

    #    if not bone_name:
    #        raise ValueError('bone %s not found' % bone_name)

    #    my_bone = self.bones[bone_name]
    #    while my_bone is not None:
    #        bones.append(my_bone)
    #        my_bone = my_bone.parent

    #    return bones, bone_name

    def get_bone(self, bone_name):
        return self.bones[bone_name]
