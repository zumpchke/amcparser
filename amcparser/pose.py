from __future__ import print_function
import numpy as np
import sh
import tempfile
import visual
import visual_common


FLOOR_POS = (0, -0.001, 0)
FLOOR_LENGTH = 4
FLOOR_HEIGHT = 0.01
FLOOR_WIDTH = 4
FLOOR_COLOR = visual.color.orange



class Axes(object):
    """A set of orthogonal arrows to represent a coordinate system."""
    def __init__(self, xdir, ydir, zdir, scale, pos=(0, 0, 0), width=0.05):
        """
        TODO: Remove magic constants.
        """
        self.scale = scale
        #self.obj = visual.box(pos=self.pos, length=0.1, width=0.05, height=0.05,
        #               color=visual.color.orange)
        self.x = visual.arrow(pos=pos, shaftwidth=width,
                       color=visual.color.red)
        self.y = visual.arrow(pos=pos, shaftwidth=width,
                       color=visual.color.green)
        self.z = visual.arrow(pos=pos, shaftwidth=width,
                       color=visual.color.blue)
        self.update(xdir, ydir, zdir)

    def update(self, xdir, ydir, zdir, pos=(0, 0, 0)):
        assert len(xdir) == 3
        assert len(ydir) == 3
        assert len(zdir) == 3
        self.x.axis = [i * self.scale for i in xdir]
        self.y.axis = [i * self.scale for i in ydir]
        self.z.axis = [i * self.scale for i in zdir]
        self.x.pos = pos
        self.y.pos = pos
        self.z.pos = pos


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
            # XXX: Where is this 'display' function
            self.scene = visual_common.create_display.display(title=self.title, width=640, height=480,
                                 center=(0, 0, 0), forward=(-2, -2, -1))
        else:
            self.scene = scene

        self.window_id = None
        self.gif_frames = list()


        self._frameno = visual.label(pos=(-6, -0, 0), text='0')
        self._create_floor()
        self._axes = Axes([1.0, 0, 0], [0, 1, 0], [0, 0, 1], 0.5)

    def _create_floor(self):
        self.floor = visual.box(pos=FLOOR_POS, length=FLOOR_LENGTH,
                                height=FLOOR_HEIGHT, width=FLOOR_WIDTH,
                                color=FLOOR_COLOR)

    def _handle_dfs(self, bone, parent, frame, transform_stack):
        # Calculate new direction and position
        direction = (bone.xyz_data[frame, :] -
                     parent.xyz_data[frame, :]).tolist()
        pos = parent.xyz_data[frame, :].tolist()

        # FIXME: Seems inefficient.
        xdir = np.asarray(transform_stack[-1][0, :]).tolist()[0]
        ydir = np.asarray(transform_stack[-1][1, :]).tolist()[0]
        zdir = np.asarray(transform_stack[-1][2, :]).tolist()[0]

        if bone.name in self.bone_data:
            # Retrieve and update objects
            cyl, s, ax = self.bone_data[bone.name]
            cyl.pos = pos
            cyl.axis = direction
            s.pos = bone.xyz_data[frame, :].tolist()
            ax.update(xdir, ydir, zdir, pos)
        else:
            # Create and save objects.
            cyl = visual.cylinder(pos=pos, axis=direction,
                           radius=Pose.cyl_radius)

            s = visual.sphere(pos=bone.xyz_data[frame, :].tolist(),
                       radius=Pose.sphere_radius)

            axes = Axes(xdir, ydir, zdir, 0.3, pos=pos, width=0.01)
            self.bone_data[bone.name] = (cyl, s, axes)

    def _handle_end_frame(self, frame):
        self._frameno.text = str(frame)
        visual.rate(1.0 / self.motion.interval)

    def _handle_end_frame_gif(self, frame):
        self._end_frame(frame)
        if not frame % 5:
            return

        if not self.window_id:
            self.window_id = sh.grep(sh.xwininfo('-root', '-tree'),
                                     self.title).strip().split(' ')[0]

        cmd = sh.Command('import')
        # TODO: Might be faster to use a RAMdisk
        tmp = tempfile.NamedTemporaryFile(suffix='.gif')
        cmd('-window', self.window_id, tmp.name)
        self.gif_frames.append(tmp)

    def to_gif(self, filename, start, end):
        """Extremely slow method to go from vpython -> GIF.

        Linux only... ?
        """
        self.motion.register_dfs_cb(self._handle_dfs)
        self.motion.register_dfs_end(self._handle_end_frame_gif)
        self.motion.traverse(self.skeleton.root, start, end)
        commands = ['-delay', '1x80', '-loop', '0']
        commands.extend(map(lambda x: x.name, self.gif_frames))
        commands.append(filename)
        sh.convert(commands)
        self.gif_frames = []

    def plot(self, start, end, loop=False):
        self.motion.register_dfs_cb(self._handle_dfs)
        self.motion.register_dfs_end(self._handle_end_frame)
        self.motion.traverse(self.skeleton.root, start, end)
        if loop:
            return self.plot(start, end, loop)
