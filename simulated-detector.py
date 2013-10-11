__doc__ = "This session demonstrates the simulated camera."

import numpy as np
import matplotlib.pyplot as plt
from concert.quantities import q
from concert.session.utils import pdoc
from concert.devices.cameras.dummy import Camera
from concert.processes import scan


# Create a camera with noisy background
camera = Camera(background=np.random.random((640, 480)))


def get_exposure_result(min_exposure, max_exposure):
    def get_mean_frame_value():
        return np.mean(camera.grab())

    return scan(camera['exposure-time'], get_mean_frame_value,
                min_exposure, max_exposure)


def plot_exposure_scan(min_exposure=1*q.ms, max_exposure=500*q.ms):
    """
    Plot the mean value of the detector image for exposure times between
    *min_exposure* and *max_exposure*.

    Returns: a tuple with exposure times and corresponding mean values.
    """
    scanner = get_exposure_scanner(min_exposure, max_exposure)
    camera.start_recording()
    x, y = get_exposure_result(min_exposure, max_exposure).result()
    camera.stop_recording()
    plt.plot(x, y)
    return x, y


def save_exposure_scan(filename, min_exposure=1*q.ms, max_exposure=500*q.ms):
    """
    Run an exposure scan and save the result as a NeXus compliant file. This
    requires that libnexus and NexPy are installed.
    """
    try:
        from concert.ext.nexus import get_scan_result

        scanner = get_exposure_scanner(min_exposure, max_exposure)
        camera.start_recording()
        data = get_scan_result(scanner).result()
        camera.stop_recording()
        data.save(filename)
    except ImportError:
        print("You have to install NexPy first")


def show_camera_frame(exposure_time=5*q.ms):
    """Show the frame as produced by the camera given *exposure_time*"""
    camera.exposure_time = exposure_time
    camera.start_recording()
    frame = camera.grab()
    camera.stop_recording()
    plt.imshow(frame)
