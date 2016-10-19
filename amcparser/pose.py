from __future__ import print_function
import os
import sh
import tempfile
import visual
from visual import *


FLOOR_POS = (0, -0.001, 0)
FLOOR_LENGTH = 4
FLOOR_HEIGHT = 0.01
FLOOR_WIDTH = 4
FLOOR_COLOR = visual.color.orange


class Axes(object):
    """A set of orthogonal arrows to represent a coordinate system."""
    def __init__(self, scale):
        """
        TODO: Remove magic constants.
        """
        self.scale = scale
        self.pos = (0, 0, 0)
        self.obj = box(pos=self.pos, length=0.1, width=0.05, height=0.05,
                       color=color.orange)
        self.x = arrow(pos=self.pos, axis=(0.5, 0, 0), shaftwidth=0.05,
                       color=color.red)
        self.y = arrow(pos=self.pos, axis=(0, 0.5, 0), shaftwidth=0.05,
                       color=color.green)
        self.z = arrow(pos=self.pos, axis=(0, 0, 0.5), shaftwidth=0.05,
                       color=color.blue)


class Pose(object):
    """Animate the motion data."""
    bone_radius = 0.05
    sphere_radius = 0.03
    cyl_radius = 0.01

    def __init__(self, skeleton, motion, scene=None):
        self.skeleton = skeleton
        self.motion = motion
        self.bone_data = dict()
        self.framerate = None
        self.title = 'amcparser %s' % (self.motion.filename)

        if not scene:
            self.scene = display(title=self.title, width=640, height=480,
                                 center=(0, 0, 0), forward=(-2, -2, -1))
        else:
            self.scene = scene

        self.window_id = None
        self.gif_frames = list()


        self._frameno = label(pos=(-6, -0, 0), text='0')
        self._create_floor()
        self._axes = Axes(1.0)

    def _create_floor(self):
        self.floor = visual.box(pos=FLOOR_POS, length=FLOOR_LENGTH,
                                height=FLOOR_HEIGHT, width=FLOOR_WIDTH,
                                color=FLOOR_COLOR)

    def _handle_dfs(self, bone, parent, frame):
        # Calculate new direction and position
        direction = (bone.xyz_data[frame, :] -
                     parent.xyz_data[frame, :]).tolist()
        pos = parent.xyz_data[frame, :].tolist()
        if bone.name in self.bone_data:
            # Retrieve and update objects
            cyl, s = self.bone_data[bone.name]
            cyl.pos = pos
            cyl.axis = direction
            s.pos = bone.xyz_data[frame, :].tolist()
        else:
            # Create and save objects.
            cyl = cylinder(pos=pos, axis=direction,
                           radius=Pose.cyl_radius)

            s = sphere(pos=bone.xyz_data[frame, :].tolist(),
                       radius=Pose.sphere_radius)
            self.bone_data[bone.name] = (cyl, s)

    def _end_frame(self, frame):
        self._frameno.text = str(frame)
        rate(1.0 / self.motion.interval)

    def _end_frame_gif(self, frame):
        self._end_frame(frame)
        if not frame % 5:
            return

        if not self.window_id:
            self.window_id = sh.grep(sh.xwininfo('-root', '-tree'),
                                     self.title).strip().split(' ')[0]

        cmd = sh.Command('import')
        # TODO: Might be faster to use a ramdisk
        tmp = tempfile.NamedTemporaryFile(suffix='.gif')
        cmd('-window', self.window_id, tmp.name)
        self.gif_frames.append(tmp)

    def to_gif(self, filename, start, end):
        """Extremely slow method to go from vpython -> GIF."""
        self.motion.register_dfs_cb(self._handle_dfs)
        self.motion.register_dfs_end(self._end_frame_gif)
        self.motion.traverse(self.skeleton.root, start, end)
        commands = ['-delay', '1x80', '-loop', '0']
        commands.extend(map(lambda x: x.name, self.gif_frames))
        commands.append(filename)
        sh.convert(commands)
        self.gif_frames = []

    def plot(self, start, end):
        self.motion.register_dfs_cb(self._handle_dfs)
        self.motion.register_dfs_end(self._end_frame)
        self.motion.traverse(self.skeleton.root, start, end)
