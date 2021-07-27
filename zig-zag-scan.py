"""---\nThis session shows how to implement a simple zig-zag scan using
two motors for horizontal (x_motor) and vertical movement (z_motor) as well as
a detector. The result is an image composed of all scanned tiles.

Usage:
    result = await zig_zag_scan()
"""

import concert
concert.require('0.30')

import numpy as np
import scipy.misc
import matplotlib.pyplot as plt
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc
from concert.devices.cameras.dummy import Camera
from concert.devices.motors.dummy import LinearMotor
from concert.ext.viewers import PyplotImageViewer


# Create a camera with noisy background
camera = Camera(background=scipy.misc.ascent())

# Assume motors' zero coordinate is left and up respectively
x_motor = LinearMotor()
z_motor = LinearMotor()

viewer = PyplotImageViewer()


async def zig_zag_scan(num_images_horizontally=2, num_images_vertically=2,
                       pixel_size=5*q.micrometer):
    await x_motor.set_position(0 * q.micrometer)
    await z_motor.set_position(0 * q.micrometer)

    width = pixel_size * (await camera.get_roi_width())
    height = pixel_size * (await camera.get_roi_height())
    delta = +width
    final_image = None

    for i in range(num_images_vertically):
        image_row = None

        for j in range(num_images_horizontally):
            await x_motor.move(delta)
            frame = np.copy(await camera.grab())

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

        await z_f

    await viewer.show(final_image)

    return final_image
