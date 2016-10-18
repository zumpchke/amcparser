from . import skeleton_path
import numpy as np
from numpy.testing import assert_allclose
from amcparser import Skeleton


def test_root_position():
    sk = Skeleton(skeleton_path)
    zeros = np.array([0, 0, 0])
    assert_allclose(sk.get_bone('root').position, zeros)


def test_bone_direction():
    sk = Skeleton(skeleton_path)
    assert sk.get_bone('MiddleSpineJoint').direction[1] == 1


def test_root_children():
    sk = Skeleton(skeleton_path)
    bone_iter = sk.get_bone('root')
    assert len(bone_iter.child) == 3

def test_iter_bones():
    sk = Skeleton(skeleton_path)
    bone_iter = sk.iter_bones('root')
    bones = [b for b in bone_iter]
    assert len(bones) == 1
    bone_iter = sk.iter_bones('MiddleSpineJoint')
    bones = [b for b in bone_iter]
    assert len(bones) == 4


def test_hierarchy():
    sk = Skeleton(skeleton_path)
    wrist_bone = sk.get_bone('LeftWristJoint')
    bone = wrist_bone
    bones = list()
    while bone.name != 'root':
        bones.append(bone.name)
        bone = bone.parent
    assert bones == ['LeftWristJoint', 'LeftForearmTwistJoint',
                     'LeftElbowJoint', 'LeftShoulderJoint',
                     'LeftClavicleJoint', 'LeftClavicleJoint_dum',
                     'UpperSpineJoint', 'MiddleSpineJoint',
                     'LowerSpineJoint', 'LowerSpineJoint_dum']


def test_dump_str():
    sk = Skeleton(skeleton_path)
    sk.dump_str(sk.root)
