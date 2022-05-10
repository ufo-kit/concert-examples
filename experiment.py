"""---\nSimulate a data acquisition.

Usage:
    await main()
"""

import concert
concert.require("0.31")

import logging
from functools import partial
from concert.session.utils import ddoc, dstate, pdoc, code_of
from concert.experiments.base import Acquisition, Experiment
from concert.experiments.addons import Consumer
from concert.devices.cameras.dummy import Camera
from concert.ext.viewers import PyplotImageViewer

LOG = logging.getLogger(__name__)


camera = await Camera()
viewer = await PyplotImageViewer()


async def produce(num_frames):
    for i in range(num_frames):
        yield await camera.grab()


async def consume(producer):
    i = 1

    async for item in producer:
        LOG.info("Got frame number {}".format(i))
        i += 1


darks = await Acquisition("darks", partial(produce, 1), consumers=[consume])
flats = await Acquisition("flats", partial(produce, 2), consumers=[consume])
radios = await Acquisition("radios", partial(produce, 20), consumers=[consume])
acquisitions = [darks, flats, radios]


async def main():
    """Run the example and output the experiment data to a dummy walker.
    Also show the images in a live preview addon.
    """
    exper = await Experiment(acquisitions)
    Consumer(exper.acquisitions, viewer)
    await exper.run()
