from functools import partial
import logging
import concert
concert.require("0.7.0")

from concert.session.utils import ddoc, dstate, pdoc
from concert.session.utils import code_of
from concert.experiments.base import Acquisition
from concert.experiments.imaging import Experiment
from concert.coroutines import coroutine
from concert.devices.cameras.dummy import Camera

__doc__ = "This is session exper"

LOG = logging.getLogger(__name__)


camera = Camera()


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
radios = Acquisition("radios", partial(produce, 3), consumer_callers=[consume])
acquisitions = [darks, flats, radios]


def run(directory):
    """Run the example and output the experiment data to *directory*."""
    exper = Experiment(acquisitions, directory, log=LOG)
    exper.run().join()
