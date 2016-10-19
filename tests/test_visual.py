from . import skeleton_path, m_walking_path
from amcparser import Pose, Skeleton, SkelMotion


def test_pose():
    sk = Skeleton(skeleton_path)
    skm = SkelMotion(sk, m_walking_path, (1.0 / 120.0))
    p = Pose(sk, skm)
    p.plot(0, 1000)
