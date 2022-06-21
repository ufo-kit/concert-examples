"""---\nThis is session uca-check.

Usage:
    check('mock')
"""

import asyncio
import concert
concert.require("0.31")

import sys
import inspect
import numpy as np
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc
from concert.devices.cameras.uca import Camera

try:
    from clint.textui import colored
    _clint_available = True
except ImportError:
    _clint_available = False


async def acquire_frame(camera):
    async with camera.recording():
        return await camera.grab()


async def test_bit_depth_consistency(camera):
    await camera.set_exposure_time(1 * q.s)
    frame = await acquire_frame(camera)

    bits = await camera.get_sensor_bitdepth()
    success = np.mean(frame) < 2 ** bits.magnitude
    return (success, "higher values than possible")


async def test_exposure_time_consistency(camera):
    await camera.set_exposure_time(1 * q.ms)
    first = await acquire_frame(camera)

    await camera.set_exposure_time(100 * q.ms)
    second = await acquire_frame(camera)

    success = np.mean(first) < np.mean(second)
    return (success, "mean image value is lower than expected")


async def test_roi_result(camera):
    await camera.set_roi_width(512 * q.px)
    await camera.set_roi_height(1024 * q.px)
    frame = await acquire_frame(camera)

    return (frame.shape == (1024, 512), "image has a different size")


async def check(camera_name):
    camera = await Camera(camera_name)
    await camera.set_trigger_source(camera.trigger_sources.AUTO)

    module = sys.modules[__name__]

    for name, obj in inspect.getmembers(module, inspect.iscoroutinefunction):
        if name.startswith('test_'):
            success, message = await obj(camera)
            message = '' if success else message

            if _clint_available:
                fmt = '{:<16}'
                status = (colored.green(fmt.format('[OK]')) if success else
                          colored.red(fmt.format('[FAIL]')))
                print("{} {:<40}{}".format(status, name, message))
            else:
                status = '[OK]' if success else '[FAIL]'
                print("{:<6} {:<40}{}".format(status, name, message))


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(check("mock"))
