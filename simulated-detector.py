__doc__ = "This session demonstrates the simulated camera."

import numpy as np
import matplotlib.pyplot as plt
from concert.quantities import q
from concert.session import pdoc
from concert.devices.cameras.dummy import Camera
from concert.processes.scan import Scanner


# Create a camera with noisy background
camera = Camera(background=np.random.random((640, 480)))


def plot_exposure_scan(min_exposure=1*q.ms, max_exposure=500*q.ms):
    """
    Plot the mean value of the detector image for exposure times between
    *min_exposure* and *max_exposure*.

    Returns: a tuple with exposure times and corresponding mean values.
    """

    def get_mean_frame_value():
        return np.mean(camera.grab())

    scanner = Scanner(camera['exposure-time'], get_mean_frame_value,
                      min_exposure, max_exposure)

    camera.start_recording()
    x, y = scanner.run().result()
    camera.stop_recording()
    plt.plot(x, y)
    return x, y


def show_camera_frame(exposure_time=5*q.ms):
    """Show the frame as produced by the camera given *exposure_time*"""
    camera.exposure_time = exposure_time
    camera.start_recording()
    frame = camera.grab()
    camera.stop_recording()
    plt.imshow(frame)
