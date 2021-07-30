"""# *scan* shows scanning of camera's exposure time.

## Usage
    await run(producer, line, acc)

## Notes
"""

import asyncio
import logging
from inspect import iscoroutinefunction
import concert
concert.require("0.30.0")

from concert.coroutines.base import broadcast
from concert.coroutines.sinks import Accumulate
from concert.quantities import q
from concert.session.utils import cdoc, ddoc, dstate, pdoc, code_of
from concert.devices.cameras.dummy import Camera
from concert.ext.viewers import PyplotViewer, PyQtGraphViewer
from concert.processes.common import ascan

LOG = logging.getLogger(__name__)
# Disable progress bar in order not to interfere with printing
concert.config.PROGRESS_BAR = False


async def feedback():
    """Our feedback just returns image mean."""
    # Let's pretend this is a serious operation which takes a while
    await asyncio.sleep(1)
    image = await camera.grab()
    # Also show the current image
    await viewer.show(image)

    return image.mean()


async def run(producer, line, accumulator):
    coros = broadcast(producer, line, accumulator)
    await asyncio.gather(*coros)

    return accumulator.items


viewer = PyQtGraphViewer()
# The last image will be quite bright
viewer.limits = 0, 10000
# Plot image mean
line = PyplotViewer(style='-o')
# Dummy camera
camera = Camera()
# For scan results collection
acc = Accumulate()
# Let's create a scan so that it can be directly plugged into *run*
producer = ascan(camera['exposure_time'], 1 * q.ms, 100 * q.ms, 10 * q.ms, feedback=feedback)
