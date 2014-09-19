"""Call main() to simulate a data acquisition."""

import concert
concert.require("0.10.0")

import logging
from functools import partial
from concert.session.utils import ddoc, dstate, pdoc
from concert.session.utils import code_of
from concert.experiments.base import Acquisition
from concert.experiments.base import Experiment
from concert.experiments.addons import Consumer
from concert.coroutines.base import coroutine
from concert.devices.cameras.dummy import Camera
from concert.storage import DummyWalker
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


darks = Acquisition("darks", partial(produce, 1), consumer_callers=[consume])
flats = Acquisition("flats", partial(produce, 2), consumer_callers=[consume])
radios = Acquisition("radios", partial(produce, 20), consumer_callers=[consume])
acquisitions = [darks, flats, radios]


def main():
    """Run the example and output the experiment data to a dummy walker. Also show the images in a
    live preview addon.
    """
    exper = Experiment(acquisitions, DummyWalker())
    addon = Consumer(exper.acquisitions, viewer)
    exper.attach(addon)
    exper.run().join()
