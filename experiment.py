"""---\nCall main() to simulate a data acquisition."""

import concert
concert.require("0.11.0")

import logging
from functools import partial
from concert.session.utils import ddoc, dstate, pdoc, code_of
from concert.experiments.base import Acquisition, Experiment
from concert.experiments.addons import Consumer
from concert.coroutines.base import coroutine
from concert.devices.cameras.dummy import Camera
from concert.ext.viewers import PyplotImageViewer

LOG = logging.getLogger(__name__)


camera = Camera()
viewer = PyplotImageViewer()


def produce(num_frames):
    for i in range(num_frames):
        yield camera.grab()


@coroutine
def consume():
    i = 1

    while True:
        yield
        LOG.info("Got frame number {}".format(i))
        i += 1


darks = Acquisition("darks", partial(produce, 1), consumers=[consume])
flats = Acquisition("flats", partial(produce, 2), consumers=[consume])
radios = Acquisition("radios", partial(produce, 20), consumers=[consume])
acquisitions = [darks, flats, radios]


def main():
    """Run the example and output the experiment data to a dummy walker.
    Also show the images in a live preview addon.
    """
    exper = Experiment(acquisitions)
    Consumer(exper.acquisitions, viewer)
    exper.run().join()
