""""---\nThis session demonstrates the simulated camera."""

import concert
concert.require("0.10.0")

import numpy as np
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc
from concert.devices.cameras.dummy import Camera
from concert.processes.common import scan
from concert.async import resolve
from concert.coroutines.base import broadcast, inject
from concert.coroutines.sinks import Accumulate
from concert.ext.viewers import PyplotViewer, PyplotImageViewer
from concert.helpers import Region


# Create a camera with noisy background
camera = Camera(background=np.random.random((640, 480)))


def get_exposure_result(region):
    def get_mean_frame_value():
        return np.mean(camera.grab())

    return scan(get_mean_frame_value, region)


def plot_exposure_scan(min_exposure=1*q.ms, max_exposure=500*q.ms, num_points=10):
    """
    Plot the mean value of the detector image for exposure times between
    *min_exposure* and *max_exposure*, use *num_points* data points.

    Returns: a tuple with exposure times and corresponding mean values.
    """
    accum = Accumulate()
    region = Region(camera['exposure_time'], np.linspace(min_exposure, max_exposure, num_points))

    with camera.recording():
        inject(resolve(get_exposure_result(region)), broadcast(PyplotViewer(style='-o')(), accum()))

    return zip(*accum.items)


def show_camera_frame(exposure_time=5*q.ms):
    """Show the frame as produced by the camera given *exposure_time*"""
    camera.exposure_time = exposure_time
    camera.start_recording()
    frame = camera.grab()
    camera.stop_recording()
    PyplotImageViewer().show(frame)
