"""---\nSession showing image and curve viewing functionality.

Usage:
    await run()
"""

import asyncio
import concert
concert.require("0.31")

import numpy as np
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc
from concert.devices.cameras.dummy import Camera
from concert.ext.viewers import PyplotViewer, PyplotImageViewer


camera = await Camera()
await camera.set_frame_rate(10 * q.count / q.s)
frame_viewer = await PyplotImageViewer(title="Live Preview", limits=(0, 2000))
curve_viewer = await PyplotViewer(title="Mean Value")


async def acquire():
    """Acquire frames with different exposure time."""
    for exp_time in np.linspace(0.001, 10, 100) * q.ms:
        await camera.set_exposure_time(exp_time)
        yield await camera.grab()


async def consume_frame(producer):
    """Display each frame and it's mean."""
    async for frame in producer:
        await frame_viewer.show(frame)
        await curve_viewer.show((await camera.get_exposure_time(), np.mean(frame)))


async def run():
    """Run the example."""
    curve_viewer.reset()
    await consume_frame(acquire())
