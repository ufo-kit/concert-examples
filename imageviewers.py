"""---\nSession showing image viewing functionality.

Usage:
    await show_random()
    await show_limits_behavior(viewer, limits='fixed')
"""

import asyncio
import concert
concert.require("0.31")

import numpy as np
from concert.coroutines.base import run_in_executor
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc
from concert.ext.viewers import PyplotImageViewer, PyQtGraphViewer


fast = await PyplotImageViewer(fast=True, title='Fast', show_refresh_rate=True)
slow = await PyplotImageViewer(fast=False, title='Slow', show_refresh_rate=True)
pyqt = await PyQtGraphViewer(title='PyQtGraph', show_refresh_rate=True)


async def show_random(num=100):
    for i in range(num):
        await pyqt.show(np.random.random(size=(256, 256)))
        await asyncio.sleep(0.1)


async def produce(num=10, shape=(256, 256), sleep_time=0.25 * q.s):
    def make_flat(mean):
        image = np.ones(shape) * mean
        # Make sure the default viewer color limits span the whole produced range
        image[0, 0] = num

        return image

    for i in range(num):
        future = run_in_executor(make_flat, i)
        yield (await future)
        await asyncio.sleep(sleep_time.to(q.s).magnitude)


async def show_limits_behavior(viewer, limits='stream'):
    """Show image series with ascending intensity and demonstrate the color limits influence on the
    displayed result.
    """
    allowed = ['auto', 'stream', 'fixed']
    if limits not in allowed:
        raise RuntimeError(f"limits argument must be one of `{allowed}'")

    await viewer['limits'].stash()
    try:
        if limits == 'fixed':
            limits = (0, 50)
        await viewer.set_limits(limits)
        await viewer(produce(num=100, sleep_time=0.04 * q.s), force=True)
    finally:
        await viewer['limits'].restore()
