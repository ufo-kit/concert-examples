""""---\nThis session demonstrates the simulated camera.

Usage:
    await plot_exposure_scan()
    await show_camera_frame()
"""

import concert
concert.require("0.31")

import numpy as np
from concert.coroutines.base import broadcast
from concert.quantities import q
from concert.processes.common import ascan
from concert.session.utils import ddoc, dstate, pdoc
from concert.devices.cameras.dummy import Camera
from concert.processes.common import scan
from concert.coroutines.sinks import Accumulate
from concert.ext.viewers import PyplotViewer, PyplotImageViewer


# Create a camera with noisy background
camera = await Camera(background=np.random.random((640, 480)))
viewer = await PyplotImageViewer(fast=False)


async def plot_exposure_scan(min_exposure=1*q.ms, max_exposure=500*q.ms, step=50*q.ms):
    """
    Plot the mean value of the detector image for exposure times between
    *min_exposure* and *max_exposure* and use *step*.
    """
    async def get_mean_frame_value():
        return np.mean(await camera.grab())

    async def do_scan():
        async with camera.recording():
            async for item in ascan(camera['exposure_time'], min_exposure, max_exposure, step,
                                    get_mean_frame_value, go_back=True):
                yield item

    line = await PyplotViewer(style='-o')
    await line(do_scan(), force=True)


async def show_camera_frame(exposure_time=5*q.ms):
    """Show the frame as produced by the camera given *exposure_time*"""
    await camera.set_exposure_time(exposure_time)
    async with camera.recording():
        frame = await camera.grab()
    await viewer.show(frame)
