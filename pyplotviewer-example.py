"""---\nSession showing image and curve viewing functionality."""

import concert
concert.require("0.6")

import numpy as np
from concert.quantities import q
from concert.coroutines.base import coroutine
from concert.session.utils import ddoc, dstate, pdoc
from concert.devices.cameras.dummy import Camera
from concert.ext.viewers import PyplotViewer, PyplotImageViewer


camera = Camera()
camera.frame_rate = 10 * q.count / q.s
frame_viewer = PyplotImageViewer(title="Live Preview")
curve_viewer = PyplotViewer(title="Mean Value")


def acquire(consumer):
    """Acquire frames with different exposure time."""
    for exp_time in np.linspace(0.001, 10, 100) * q.ms:
        camera.exposure_time = exp_time
        consumer.send(camera.grab())


@coroutine
def consume_frame():
    """Display each frame and it's mean."""
    while True:
        frame = yield
        frame_viewer.show(frame)
        curve_viewer.plot(camera.exposure_time, np.mean(frame))


def run():
    """Run the example."""
    curve_viewer.clear()
    acquire(consume_frame())
