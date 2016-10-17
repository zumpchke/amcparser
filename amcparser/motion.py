from __future__ import print_function
import cgkit.asfamc
import numpy as np

from .math_utils import rotation_matrix


class SkelMotion(cgkit.asfamc.AMCReader):
    """Handle the corresponding motion file for a skeleton description (amc)"""
    def __init__(self, skeleton, filename, interval):
        if filename:
            cgkit.asfamc.AMCReader.__init__(self, filename)
        self.skeleton = skeleton
        self.data = dict()
        self.size = 0
        self.interval = interval

        if filename:
            self.read()

    def onFrame(self, framenr, data):
        """On each frame, save data."""
        for bone, bdata in data:
            if bone not in self.data:
                self.data[bone] = list()
            self.data[bone].append(bdata)
        self.size = framenr

    def get_position(self, bone, start, end):
        """Get displacement of single bone relative to root bone.
        
        # Arguments
            start: start of frame range
            end: end of range
        """

        if not hasattr(bone, '__iter__'):
            bone = [bone]


        if end < 0:
            end = self.size + end + 1

        if start < 0 or end < start:
            raise ValueError('incorrect params to function')

        order = [b for b in self.skeleton.iter_bones(bone)]
        order.reverse()
        assert order[0].name == 'root'
        assert order[0].is_root

        maxlen = end - start
        xyz = np.zeros((maxlen, 3))

        # For every frame
        for i in range(start, end):
            transmat = list()

            # Add root translation
            root_pos = (np.array(self.data['root'][i][0:3]) *
                        self.skeleton.scale)
            xyz[i, :] = root_pos

            root_angle = np.array(self.data['root'][i][3:])
            root_matrix = rotation_matrix(self.skeleton.root,
                                          root_angle[0],
                                          root_angle[1],
                                          root_angle[2])

            transmat.append(root_matrix)

            # For every bone in list
            for bone in order[1:]:
                if bone.name in self.data:

                    # We only store rotation for other bones,
                    # but the values might just have zeros.
                    assert len(self.data[bone.name][i]) <= 6

                    # If we have more than three values, assume
                    # the first three and translation and are thus zero.
                    if len(self.data[bone.name][i]) > 3:
                        start = 3
                    else:
                        start = 0

                    bone_rotation = np.array(self.data[bone.name][i][start:])
                    L = rotation_matrix(bone,
                                        bone_rotation[0],
                                        bone_rotation[1],
                                        bone_rotation[2])
                    bone.global_transform.append(L * transmat[-1])
                    transmat.append(bone.global_transform[-1])
                else:
                    L = rotation_matrix(bone, 0, 0, 0)
                    bone.global_transform.append(L * transmat[-1])
                    transmat.append(bone.global_transform[-1])

                V = bone.vector * transmat[-1]
                xyz[i, :] = xyz[i, :] + V

        return xyz
