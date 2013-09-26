__doc__ = """---\nThis session shows how to implement a simple zig-zag scan using
two motors for horizontal (x_motor) and vertical movement (z_motor) as well as
a detector. The result is an image composed of all scanned tiles."""

import numpy as np
import scipy.misc
import matplotlib.pyplot as plt
from concert.quantities import q
from concert.devices.cameras.dummy import Camera
from concert.devices.motors.dummy import Motor
from concert.processes.scan import Scanner


# Create a camera with noisy background
camera = Camera(background=scipy.misc.lena())

# Assume motors' zero coordinate is left and up respectively
x_motor = Motor()
z_motor = Motor()


def zig_zag_scan(num_images_horizontally=2, num_images_vertically=2,
                 pixel_size=5*q.micrometer):
    x_motor.position = 0 * q.micrometer
    z_motor.position = 0 * q.micrometer

    width = pixel_size * camera.roi_width
    height = pixel_size * camera.roi_height
    delta = +width
    final_image = None

    for i in range(num_images_vertically):
        image_row = None

        for j in range(num_images_horizontally):
            x_motor.move(delta).wait()
            frame = np.copy(camera.grab())

            if image_row is None:
                image_row = frame
            else:
                image_row = np.hstack((image_row, frame))

        z_f = z_motor.move(height)

        # Move in the other direction
        delta *= -1

        # Add row to our final image
        if final_image is None:
            final_image = image_row
        else:
            final_image = np.vstack((final_image, image_row))

        z_f.wait()

    return final_image
