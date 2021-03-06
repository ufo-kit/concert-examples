"""---\nThis is session uca-check."""

import concert
concert.require("0.10.0")

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


def acquire_frame(camera):
    camera.start_recording()
    frame = camera.grab()
    camera.stop_recording()
    return frame


def test_bit_depth_consistency(camera):
    camera.exposure_time = 1 * q.s
    frame = acquire_frame(camera)

    bits = camera.sensor_bitdepth
    success = np.mean(frame) < 2**bits.magnitude
    return (success, "higher values than possible")


def test_exposure_time_consistency(camera):
    camera.exposure_time = 1 * q.ms
    first = acquire_frame(camera)

    camera.exposure_time = 100 * q.ms
    second = acquire_frame(camera)

    success = np.mean(first) < np.mean(second)
    return (success, "mean image value is lower than expected")


def test_roi_result(camera):
    camera.roi_width = 512 * q.count
    camera.roi_height = 1024 * q.count
    frame = acquire_frame(camera)

    return (frame.shape == (1024, 512), "image has a different size")


def check(camera_name):
    camera = Camera(camera_name)
    camera.trigger_source = camera.trigger_sources.AUTO

    module = sys.modules[__name__]

    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if name.startswith('test_'):
            success, message = obj(camera)
            message = '' if success else message

            if _clint_available:
                status = colored.green('[OK]') if success else colored.red('[FAIL]')
                print("{:<16} {:<40}{}".format(status, name, message))
            else:
                status = '[OK]' if success else '[FAIL]'
                print("{:<6} {:<40}{}".format(status, name, message))


if __name__ == '__main__':
    check("mock")
