from . import skeleton_path, m_walking_path
from numpy.testing import assert_allclose
from amcparser import Skeleton, SkelMotion


def test_motion_root():
    sk = Skeleton(skeleton_path)
    skm = SkelMotion(sk, m_walking_path, (1.0 / 120.0))
    skm.traverse('root', 0, 10)
    root_pos = sk.root.xyz_data
    assert_allclose(root_pos[0, :], map(float, skm.data['root'][0][0:3]))
    assert_allclose(root_pos[9, :], map(float, skm.data['root'][9][0:3]))


def test_motion_bone():
    sk = Skeleton(skeleton_path)
    skm = SkelMotion(sk, m_walking_path, (1.0 / 120.0))
    skm.traverse('LeftToesJoint', 0, -1)
    bone_pos = sk.get_bone('LeftToesJoint').xyz_data
    assert bone_pos.shape[0] == 1741
