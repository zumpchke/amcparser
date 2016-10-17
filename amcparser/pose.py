from . import Skeleton, SkelMotion
import visual
from visual import *


FLOOR_POS = (0, -0.001, 0)
FLOOR_LENGTH = 4
FLOOR_HEIGHT = 0.01
FLOOR_WIDTH = 4


class Axes(object):
    """A set of orthogonal arrows to represent a coordinate system."""
    def __init__(self, scale):
        self.scale = scale
        self.pos = (0, 0.05, 0)
        self.obj = box(pos=self.pos, length=0.1, width=0.05, height=0.05,
                       color=color.orange)
        self.x = arrow(pos=self.pos, axis=(0.5, 0, 0), shaftwidth=0.01,
                       color=color.red)
        self.x_label = label(pos=(0.6, 0, 0), text='X', height=8)
        self.y = arrow(pos=self.pos, axis=(0, 0.5, 0), shaftwidth=0.01,
                       color=color.green)
        self.y_label = label(pos=(0.0, 0.6, 0), text='Y', height=8)
        self.z = arrow(pos=self.pos, axis=(0, 0, 0.5), shaftwidth=0.01,
                       color=color.blue)
        self.z_label = label(pos=(0.0, 0.0, 0.6), text='Z', height=8)


class Pose(object):
    bone_radius = 0.05
    sphere_radius = 0.03
    cyl_radius = 0.01

    def __init__(self, skeleton, motion, scene=None):
        self.skeleton = skeleton
        self.motion = motion

        if not scene:
            self.scene = display(title='amcparser', width=640, height=480)
        else:
            self.scene = scene

        self._create_floor()
        self._axes = Axes(1.0)

    def _create_floor(self):
        """
        Create floor
        """
        self.floor = visual.box(pos=FLOOR_POS, length=FLOOR_LENGTH,
                                height=FLOOR_HEIGHT, width=FLOOR_WIDTH,
                                color=visual.color.white)

    def plot(self):
        pass
