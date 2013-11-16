__doc__ = "This session demonstrates online reconstruction preview faked " + \
    "by a FileCamera"

import os
import time
import logging
from concert.ext.viewers import PyplotViewer
from concert.coroutines import backprojector, ImageAverager
from concert.helpers import inject, broadcast
from concert.devices.cameras.dummy import FileCamera
from concert.quantities import q
from concert.experiments.imaging import flat_correct


LOG = logging.getLogger(__name__)


def readout_images(camera, num_frames=None):
    i = 0

    while True:
        image = camera.grab()
        if image is None or num_frames is not None and num_frames == i:
            break

        yield image

        i += 1
        LOG.info("Produced image {}".format(i))


def acquire_images(camera, num_images):
    sleep_time = (num_images / camera.frame_rate).to_base_units().magnitude
    camera.start_recording()
    time.sleep(sleep_time)
    camera.stop_recording()


def take_images(folder, num_images):
    camera = get_camera(folder)
    acquire_images(camera, num_images)
    for image in readout_images(camera):
        yield image


def get_camera(folder):
    camera = FileCamera(folder)
    camera.frame_rate = 1000000 * q.count / q.s
    camera.trigger_mode = camera.TRIGGER_AUTO
    camera.roi_y = 10

    return camera


def reconstruct(folder, num_projs, center, slice_num,
                nth_proj=2, nth_column=4):
    """
    *folder* is the toplevel folder with structure::

        folder/darks
        folder/flats
        folder/radios

    *num_projs* is the number of projections which the reconstruction
    and radiographs preview accept, *center* is the center of rotation,
    *slice_num* is the slice row number which we want to reconstruct,
    *nth_proj* means that the reconstruction takes only every n-th
    projection into account, *nth_column* the same for slice spatial
    dimensions.
    """
    # Image preview
    radio_viewer = PyplotViewer()
    slice_viewer = PyplotViewer()

    try:
        # Average incoming images (useful for flats and darks)
        averager = ImageAverager()

        # Take darks
        inject(take_images(os.path.join(folder, "darks"), 1 * q.count),
               averager.average_images())
        dark = averager.average

        # Take flats
        inject(take_images(os.path.join(folder, "flats"), 1 * q.count),
               averager.average_images())
        flat = averager.average

        backproject_generator = backprojector(slice_num, center,
                                              num_projs=num_projs,
                                              nth_column=nth_column,
                                              nth_projection=nth_proj,
                                              consumer=slice_viewer(
                                                  num_projs / nth_proj),
                                              fast=True)

        # Workflow:
        #
        # images -- flat_correction -- view radiographs
        #                           \
        #                            reconstruct one slice -- view slice
        inject(
            take_images(os.path.join(folder, "radios"), num_projs * q.count),
            flat_correct(broadcast(backproject_generator,
                                   radio_viewer(num_projs)), dark, flat))
    except KeyboardInterrupt:
        radio_viewer.terminate()
        slice_viewer.terminate()


if __name__ == '__main__':
    # This should work anywhere where the folder is accessible
    # Preconfigured so you can see something right away
    reconstruct("/mnt/fast/ufo/scan16", 995, 985.5, 800)
