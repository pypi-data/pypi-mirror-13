# coding: utf-8
# -----------------------------------------------------------------------------
# Copyright (c) 2015-2016 Tiago Baptista
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

"""
A simulation framework for complex systems modeling and analysis.
"""

from __future__ import division
from .__version__ import __version__

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.transforms import Affine2D
from matplotlib import animation
from matplotlib import verbose
import numpy as np
import pyglet

try:
    from io import BytesIO as StringIO
except ImportError:
    from cStringIO import StringIO


class Simulator(object):
    def __init__(self, width=500, height=500, use_mpl=True):
        self.width = width
        self.height = height
        self.use_mpl = use_mpl
        if use_mpl:
            self.dpi = 80
            self.figure = plt.figure(figsize=(width/self.dpi, height/self.dpi),
                                     dpi=self.dpi)
            self._create_canvas()

    def step(self, delta=0):
        assert False, "Not implemented!"

    def reset(self):
        assert False, "Not implemented!"

    def draw(self):
        assert False, "Not implemented!"

    def _create_canvas(self):
        self.canvas = FigureCanvas(self.figure)
        data = StringIO()
        self.canvas.print_raw(data, dpi=self.dpi)
        self.image = pyglet.image.ImageData(self.width, self.height,
                                            'RGBA', data.getvalue(),
                                            -4 * self.width)

    def update_image(self):
        data = StringIO()
        self.canvas.print_raw(data, dpi=self.dpi)
        self.image.set_data('RGBA', -4 * self.width, data.getvalue())


class PyafaiSimulator(Simulator):
    def __init__(self, world, width=500, height=500):
        if not hasattr(world, 'width'):
            world.width = width

        if not hasattr(world, 'height'):
            world.height = height

        super(PyafaiSimulator, self).__init__(world.width, world.height, use_mpl=False)

        self.world = world
        self.world.paused = False
        pyglet.clock.unschedule(self.world._start_schedule)

    def step(self, delta=0):
        self.world.update(delta)

    def draw(self):
        self.world.draw()
        self.world.draw_objects()


class Display(pyglet.window.Window):
    def __init__(self, width=500, height=500, interval=0.05, multi_sampling=True, **kwargs):
        if multi_sampling:
            # Enable multi sampling if available on the hardware
            platform = pyglet.window.get_platform()
            display = platform.get_default_display()
            screen = display.get_default_screen()
            template = pyglet.gl.Config(sample_buffers=1, samples=4,
                                        double_buffer=True)
            try:
                config = screen.get_best_config(template)
            except pyglet.window.NoSuchConfigException:
                template = pyglet.gl.Config()
                config = screen.get_best_config(template)

            super(Display, self).__init__(width, height, 'Complex Systems (paused)', config=config, **kwargs)
        else:
            super(Display, self).__init__(width, height, caption='Complex Systems (paused)', **kwargs)

        self.paused = True
        self.show_fps = False
        self.real_time = True
        self._recording = False
        self._movie_filename = 'simcx_movie.mp4'
        self._movie_writer = None
        self._interval = interval
        self._sims = []
        self._pos = []

        self._fps_display = pyglet.clock.ClockDisplay()

        pyglet.clock.schedule_interval(self._update, self._interval)

    def add_simulator(self, sim, x=0, y=0):
        if sim not in self._sims:
            self._sims.append(sim)
            self._pos.append((x, y))

            self._resize_window()

    def start_recording(self, filename, fps=None, bitrate=1800):
        if self._movie_writer is None:
            if fps is None:
                fps = 1 // self._interval

            self._movie_writer = FFMpegWriter(fps=fps, bitrate=bitrate)
            self._movie_writer.setup(self, filename)
            self._movie_writer.grab_frame()
            self._recording = True
            print("Recording started...")
        else:
            print("A movie is already being recorded for this Display.")

    def on_draw(self):
        # clear window
        self.clear()

        # draw sims
        for i in range(len(self._sims)):
            sim = self._sims[i]
            if sim.use_mpl:
                sim.image.blit(*self._pos[i])
            else:
                pyglet.gl.glPushMatrix()
                pyglet.gl.glTranslatef(self._pos[i][0], self._pos[i][1], 0)
                sim.draw()
                pyglet.gl.glPopMatrix()

        # show fps
        if self.show_fps:
            self._fps_display.draw()

    def on_close(self):
        if self._movie_writer is not None:
            self._movie_writer.finish()

        super(Display, self).on_close()

    def on_key_press(self, symbol, modifiers):
        super(Display, self).on_key_press(symbol, modifiers)

        if symbol == pyglet.window.key.S:
            if self.paused:
                self._step_simulation(self._interval)

        elif symbol == pyglet.window.key.R:
            if pyglet.window.key.MOD_ALT & modifiers:
                self.start_recording(self._movie_filename)
            else:
                if self.paused:
                    self._reset_simulation()

        elif symbol == pyglet.window.key.SPACE:
            if self.paused:
                self.paused = False
                self.set_caption(self.caption.replace(" (paused)", ""))
            else:
                self.paused = True
                self.set_caption(self.caption + " (paused)")
        elif symbol == pyglet.window.key.F:
            self.show_fps = not self.show_fps

    def _draw_gui(self):
        pass

    def _update(self, dt):
        if not self.paused:
            self._step_simulation(dt)

    def _step_simulation(self, dt=None):
        if not self.real_time:
            dt = self._interval

        for sim in self._sims:
            sim.step(dt)
            if sim.use_mpl:
                sim.draw()
                sim.update_image()
        if self._recording:
            self._movie_writer.grab_frame()

    def _reset_simulation(self):
        for sim in self._sims:
            sim.reset()

    def _resize_window(self):
        max_x = 0
        max_y = 0
        for i in range(len(self._sims)):
            if self._pos[i][0] + self._sims[i].width > max_x:
                max_x = self._pos[i][0] + self._sims[i].width
            if self._pos[i][1] + self._sims[i].height > max_y:
                max_y = self._pos[i][1] + self._sims[i].height

        if max_x != self.width or max_y != self.height:
            self.set_size(max_x, max_y)
            self.clear()


class FFMpegWriter(animation.FFMpegWriter):
    @property
    def frame_size(self):
        """A tuple (width,height) in pixels of a movie frame."""
        return self.display.width, self.display.height

    def setup(self, display, outfile):
        """
        Perform setup for writing the movie file.
        display: `simcx.Display` instance
            The Display instance whose framebuffer we want to use.
        outfile: string
            The filename of the resulting movie file
        """
        self.outfile = outfile
        self.display = display

        # Run here so that grab_frame() can write the data to a pipe. This
        # eliminates the need for temp files.
        self._run()

    def grab_frame(self, **savefig_kwargs):
        """
        Grab the image information from the display and save as a movie frame.
        The keyword arguments are not being used in the subclass.
        """
        verbose.report('MovieWriter.grab_frame: Grabbing frame.',
                       level='debug')
        try:
            image = pyglet.image.get_buffer_manager().get_color_buffer().get_image_data()
            self._frame_sink().write(image.get_data('RGBA', -4 * self.display.width))

        except RuntimeError:
            out, err = self._proc.communicate()
            verbose.report('MovieWriter -- Error '
                           'running proc:\n%s\n%s' % (out,
                                                      err), level='helpful')
            raise


def run():
    pyglet.app.run()


class Trajectory(Simulator):
    """Class to build and display the trajectory of a 1D, linear, first-order,
    autonomous system."""

    def __init__(self, func, initial_states, func_string='', grid=False,
                 **kwargs):
        super(Trajectory, self).__init__(**kwargs)

        self._state = [x for x in initial_states]
        self._func = func
        self._trajectories = [[x] for x in initial_states]
        self._time = [0]

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Trajectory ' + func_string)
        self.ax.set_xlabel('Time $t$')
        self.ax.set_ylabel('$x_t$')
        self._lines = []
        for i in range(len(self._trajectories)):
            line, = self.ax.plot(self._time, self._trajectories[i],
                                 label=str(self._state[i]))
            self._lines.append(line)

        self.ax.legend()

        if grid:
            self.ax.grid()

        self.update_image()

    def step(self, delta=0):
        for i in range(len(self._state)):
            self._state[i] = self._func(self._state[i])
            self._trajectories[i].append(self._state[i])

        self._time.append(self._time[-1] + 1)

    def draw(self):
        for i in range(len(self._lines)):
            self._lines[i].set_data(self._time, self._trajectories[i])
        self.ax.relim()
        self.ax.autoscale_view()


class TrajectoryDiff(Simulator):
    """Class to build and display the difference between the trajectories of a
    1D dynamic system, using two initial seeds."""

    def __init__(self, func, seed1, seed2, func_string='', grid=False,
                 **kwargs):
        super(TrajectoryDiff, self).__init__(**kwargs)

        self._state = [seed1, seed2]
        self._func = func
        self._trajectory = [abs(seed1 - seed2)]
        self._time = [0]

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Trajectory Difference for ' + func_string)
        self.ax.set_xlabel('Time $t$')
        self.ax.set_ylabel('$x_t$')
        self._line, = self.ax.plot(self._time, self._trajectory, label='$x1_0=' + str(seed1) + '$ and $x2_0=' + str(seed2) + '$')
        self.ax.legend()

        if grid:
            self.ax.grid()

        self.update_image()

    def step(self, delta=0):
        for i in range(len(self._state)):
            self._state[i] = self._func(self._state[i])

        self._trajectory.append(abs(self._state[0] - self._state[1]))

        self._time.append(self._time[-1] + 1)

    def draw(self):
        self._line.set_data(self._time, self._trajectory)
        self.ax.relim()
        self.ax.autoscale_view()


class Cobweb(Simulator):
    """ Class to build and display the cobwed diagram of a 1D system."""

    def __init__(self, func, initial_states, min, max, func_string='',
                 legend=True, **kwargs):
        super(Cobweb, self).__init__(**kwargs)

        self._func = func
        self._t = 0
        self._states = [x for x in initial_states]
        self._cobx = [[x, x] for x in initial_states]
        self._coby = [[0, self._func(x)] for x in initial_states]
        self._x = np.linspace(min, max, 1000)
        func_vec = np.vectorize(self._func)
        self._y = func_vec(self._x)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('t = 0')
        self.ax.set_xlabel('$x$')
        self.ax.set_ylabel('$f(x)$')

        # PLot function
        self.ax.plot(self._x, self._y, label='$f(x)=$' + func_string)

        # Plot f(x) = x
        self.ax.plot(self._x, self._x, ':k', label='$f(x)=x$')

        # Create initial cobweb plots
        self._cobweb_lines = []
        for i in range(len(initial_states)):
            line, = self.ax.plot(self._cobx[i], self._coby[i], label='$x_0=' + str(self._states[i]) + '$')
            self._cobweb_lines.append(line)
            self._states[i] = self._func(self._states[i])

        if legend:
            self.ax.legend()

        self.update_image()

    def step(self, delta=0):
        for i in range(len(self._states)):
            self._cobx[i].append(self._states[i])
            self._coby[i].append(self._states[i])
            self._cobx[i].append(self._states[i])
            self._states[i] = self._func(self._states[i])
            self._coby[i].append(self._states[i])

        self._t += 1

    def draw(self):
        for i in range(len(self._cobweb_lines)):
            self._cobweb_lines[i].set_data(self._cobx[i], self._coby[i])

        self.ax.set_title('t = ' + str(self._t))


class BifurcationDiagram(Simulator):
    def __init__(self, x_0, start=1000, end_samples=250, dr=0.01,
                 start_r=0, end_r=4.0):
        super(BifurcationDiagram, self).__init__()

        self._start = start
        self._end = end_samples
        self._dr = dr
        self._start_r = start_r
        self._end_r = end_r
        self._r = start_r
        self._x_0 = x_0
        self._x = set()
        self._y = set()

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Bifurcation Diagram for the Logistic equation')
        self.ax.set_xlabel('r (' + str(start_r) + ')')
        self.ax.set_ylabel('Final Value(s)')
        self.ax.set_xlim(start_r, end_r)
        self.ax.set_ylim(0, 1)

        self.update_image()

    @staticmethod
    def logistic(r, x):
        return r * x * (1 - x)

    def step(self, delta=0):
        if self._r <= self._end_r:
            r = self._r
            x = self._x_0
            for t in range(self._start):
                x = BifurcationDiagram.logistic(r, x)
            self._y = set()
            for t in range(self._end):
                x = BifurcationDiagram.logistic(r, x)
                self._y.add(x)
            self._x = [r] * len(self._y)
            self._y = list(self._y)
            self._r += self._dr

    def draw(self):
        self.ax.scatter(self._x, self._y, s=0.5, c='black')
        self.ax.set_xlabel('r (' + str(self._r-self._dr) + ')')


class IFS(Simulator):
    """A random Iterated Function System simulator."""

    def __init__(self, transforms, probs,
                 width=500, height=500, step_size=100):
        super(IFS, self).__init__(width, height, use_mpl=False)

        self._discard = 10
        self._step_size = step_size
        self._transforms = transforms[:]
        self._n = len(transforms)
        self._probs = probs[:]
        self._screen_transform = Affine2D().scale(width, height)

        self._point = np.array((0.0, 0.0))

        for i in range(self._discard):
            self.step(0, False)

        self.batch = pyglet.graphics.Batch()

    def get_random_transform(self):
        i = np.random.choice(self._n, p=self._probs)
        return self._transforms[i]

    def step(self, delta=0, plot=True):
        for i in range(self._step_size):
            self._point = self.get_random_transform().transform_point(self._point)
            if plot:
                p = self._screen_transform.transform_point(self._point)
                self.batch.add(1, pyglet.gl.GL_POINTS, None, ('v2f', p),
                               ('c3B', (255, 255, 255)))

    def draw(self):
        self.batch.draw()

