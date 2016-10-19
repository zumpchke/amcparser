from __future__ import print_function
import cgkit.asfamc
import numpy as np
from tqdm import tqdm

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

        self.dfs_cb = None
        self.dfs_end = None
        self._init_bone_data()

    def _init_bone_data(self):
        for bone in self.skeleton.bones.values():
            bone.xyz_data = np.zeros((self.size, 3))
        self.skeleton.root.xyz_data = np.zeros((self.size, 3))

    def onFrame(self, framenr, data):
        """Parsing: On each frame, save data."""
        for bone, bdata in data:
            if bone not in self.data:
                self.data[bone] = list()
            self.data[bone].append(bdata)
        self.size = framenr

    def _calc_root_matrix(self, frame):
        root_pos = (np.array(self.data['root'][frame][0:3]) *
                    self.skeleton.scale)
        root_angle = np.array(self.data['root'][frame][3:])
        root_matrix = rotation_matrix(self.skeleton.root, root_angle[0],
                                      root_angle[1], root_angle[2])
        return root_pos, root_matrix

    def _calc_bone_matrix(self, bone, frame):
        if bone.name in self.data:
            assert len(self.data[bone.name][frame]) <= 6
            if len(self.data[bone.name][frame]) > 3:
                start = 3
            else:
                start = 0
            bone_rotation = np.array(self.data[bone.name][frame][start:])
            L = rotation_matrix(bone, bone_rotation[0], bone_rotation[1],
                                bone_rotation[2])
        else:
            # Handle dummy bones which contain don't change angle
            # in their local coordinate system per frame.
            L = rotation_matrix(bone, 0, 0, 0)
        return L

    def _dfs(self, bone, frame, parent=None, stack=None):
        if bone == self.skeleton.root:
            pos, mat = self._calc_root_matrix(frame)
            self.skeleton.root.xyz_data[frame] = pos
            stack.append(mat)
        else:
            stack.append(self._calc_bone_matrix(bone, frame) * stack[-1])
            bone.xyz_data[frame, :] = (parent.xyz_data[frame, :] +
                                       (bone.vector * stack[-1]))
            if self.dfs_cb:
                self.dfs_cb(bone, parent, frame)

        for i in bone.child:
            self._dfs(i, frame, parent=bone, stack=stack)

        stack.pop()

    def register_dfs_cb(self, dfs_cb):
        """Called after the calculation of the position of a bone in graph."""
        self.dfs_cb = dfs_cb

    def register_dfs_end(self, dfs_end):
        """Called after a traversal of the skeleton graph for a single frame.
        """
        self.dfs_end = dfs_end

    def traverse(self, bone, start, end):
        if end < 0:
            end = self.size + end + 1

        if start < 0 or end < start:
            raise ValueError('incorrect params to function')

        for i in tqdm(range(start, end)):
            self._dfs(self.skeleton.root, i, stack=list())
            if self.dfs_end:
                self.dfs_end(i)
