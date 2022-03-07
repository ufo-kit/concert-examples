"""
exp is an Experiment instance that generates frames and does not fearure the ready_to_prepare_next_sample Event.
blocking_exp is an Experiment instance with the ready_to_prepare_next_sample Event and a sleep of 10s in the finish().

The directors director and blocking_director are connected to them.

"""

import concert

concert.require("0.30")

import logging
import asyncio

from concert.session.utils import ddoc, dstate, pdoc, code_of
from concert.experiments.addons import Consumer
from concert.devices.cameras.dummy import Camera
from concert.ext.viewers import PyplotImageViewer
from concert.storage import DirectoryWalker
from concert.base import Parameter
from concert.processes.experiments import Director as BaseDirector
from concert.experiments.base import Experiment as BaseExperiment, Acquisition

LOG = logging.getLogger(__name__)


class Experiment(BaseExperiment):
    num_frames = Parameter()

    def __init__(self, walker, camera):
        self._camera = camera
        self._num_frames = None
        acquisition = Acquisition("frames", self._produce_frames)
        super().__init__([acquisition], walker=walker)
        self.num_frames = 10

    async def _produce_frames(self):
        await self._camera.set_trigger_mode("AUTO")
        with self._camera.recording():
            for i in range(await self.get_num_frames()):
                yield await self._camera.grab()

    async def _get_num_frames(self):
        return self._num_frames

    async def _set_num_frames(self, number):
        self._num_frames = int(number)


class BlockingExperiment(Experiment):
    """
    An Experiment that waits in its finish-function but sets ready_to_prepare_next_sample.
    """

    def __init__(self, walker, camera):
        super().__init__(walker, camera)

    def finish(self):
        self.log.info("Finish start")
        self.ready_to_prepare_next_sample.set()
        # Do something that takes long, and does not interfere with the next iteration of a
        # Director.
        asyncio.sleep(10)
        self.log.info("Finish end")


class Director(BaseDirector):
    def __init__(self, experiment):
        super().__init__(experiment)

    async def _get_number_of_iterations(self) -> int:
        return 4

    async def _prepare_run(self, iteration: int):
        LOG.info("Preparing iteration %i" % iteration)
        await self._experiment.set_num_frames(iteration * 1)


camera = Camera()
viewer = PyplotImageViewer()
walker = DirectoryWalker()

exp = Experiment(walker, camera)
live_view_exp = Consumer(exp.acquisitions, viewer)

blocking_exp = BlockingExperiment(walker, camera)
live_view_blocking_exp = Consumer(exp.acquisitions, viewer)

director_exp = Director(exp)
director_blocking_exp = Director(blocking_exp)



