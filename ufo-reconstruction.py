__doc__ = """This session demonstrates reconstruction with the UFO data
processing framework."""

import numpy as np
from gi.repository import Ufo
from concert.quantities import q
from concert.ext.ufo import PluginManager, InjectProcess
from concert.devices.cameras.dummy import Camera


def acquire(camera, num_frames):
    camera.start_recording()

    for i in xrange(num_frames):
        yield camera.grab()


def reconstruct_from(camera):
    pm = PluginManager()

    fft = pm.get_task('fft', dimensions=1)
    ifft = pm.get_task('ifft', dimensions=1)
    fltr = pm.get_task('filter')
    bp = pm.get_task('backproject')
    writer = pm.get_task('writer')

    graph = Ufo.TaskGraph()
    graph.connect_nodes(fft, fltr)
    graph.connect_nodes(fltr, ifft)
    graph.connect_nodes(ifft, bp)
    graph.connect_nodes(bp, writer)

    with InjectProcess(graph) as process:
        for frame in acquire(camera, 10):
            process.push(frame)


if __name__ == '__main__':
    camera = Camera()
    camera.frame_rate = 10 * q.count / q.s
    reconstruct_from(camera)
