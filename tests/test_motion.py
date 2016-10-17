from . import skeleton_path, m_walking_path
from numpy.testing import assert_allclose
from amcparser import Skeleton, SkelMotion


def test_motion_root():
    sk = Skeleton(skeleton_path)
    skm = SkelMotion(sk, m_walking_path, (1.0 / 120.0))
    root_pos = skm.get_position('root', 0, 10)
    assert root_pos.shape[0] == 10
    assert_allclose(root_pos[0, :], map(float, skm.data['root'][0][0:3]))
    assert_allclose(root_pos[9, :], map(float, skm.data['root'][9][0:3]))


def test_motion_middlespinejoint():
    sk = Skeleton(skeleton_path)
    skm = SkelMotion(sk, m_walking_path, (1.0 / 120.0))
    msj_pos = skm.get_position('LeftFingersJoint', 0, -1)
    assert msj_pos.shape[0] == 1741
