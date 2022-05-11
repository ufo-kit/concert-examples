"""# *scan* shows a Gaussian profile as a function of camera's exposure time.

## Usage
    await run(producer, line, acc)

## Notes
"""

import asyncio
import logging
import math
from inspect import iscoroutinefunction
import concert
concert.require("0.31")

from concert.coroutines.base import broadcast
from concert.coroutines.sinks import Accumulate
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc, code_of
from concert.devices.cameras.dummy import Camera
from concert.ext.viewers import PyplotViewer, PyQtGraphViewer
from concert.processes.common import ascan

LOG = logging.getLogger(__name__)
# Disable progress bar in order not to interfere with printing
concert.config.PROGRESS_BAR = False


async def feedback():
    """Our feedback just returns image mean."""
    # Let's pretend this is a serious operation which takes a while
    await asyncio.sleep(0.2)
    image = await camera.grab()
    # Also show the current image
    await viewer.show(image)

    return math.exp(-(image.mean() - 4600) ** 2 / (2 * 1500 ** 2))


async def run(producer, line, accumulator):
    coros = broadcast(producer, line, accumulator)
    await asyncio.gather(*coros)

    return accumulator.items


viewer = await PyQtGraphViewer()
# The last image will be quite bright
await viewer.set_limits((0, 10000))
# Plot image mean
line = await PyplotViewer(style='-o', force=True)
# Dummy camera
camera = await Camera()
# For scan results collection
acc = Accumulate()
# Let's create a scan so that it can be directly plugged into *run*
producer = ascan(camera['exposure_time'], 1 * q.ms, 100 * q.ms, 2.5 * q.ms, feedback=feedback)
