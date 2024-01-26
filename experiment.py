"""---\nSimulate a data acquisition.

In this simple example we demonstrate the functionality of a bare-metal
`Experiment` type. `Experiment` deals with a collection of `Acquisition` and
calls their `acquire` method. `Acquisition` can be local or remote. In this
example we are working with local `Acquisition` which is basically a coroutine
function that describes, how the data to be acquired is produced.

Subsequently, we attach a `Consumer` addon to each `Acquisition`. In this case
our `Consumer` is a `PyQtGraphViewer` object to display the dummy data.

It is essential that we call `start_recording` on the camera device before
running the experiment. The default state of the `Camera` device is `standby`.
Calling `start_recording` transitions the state to `recording` and eventually to
`readout` which makes grabbing frames prossible.

Usage:
    await camera.start_recording()
    await exp.run()
"""

import concert
concert.require("0.31")

import logging
from typing import Generator
from functools import partial
import numpy as np
from concert.session.utils import ddoc, dstate, pdoc, code_of
from concert.experiments.base import Acquisition, Experiment
from concert.experiments.addons.local import Consumer
from concert.devices.cameras.dummy import Camera
from concert.ext.viewers import PyQtGraphViewer

# Instantiate a dummy camera device which simulates dummy poisson noise
# as frames. It is essential that we call the `start_recording` method
# on the camera object to ensure that the camera state is `standby` before
# running the experiment.
camera = await Camera()
viewer = await PyQtGraphViewer()

async def produce(num_frames: int) -> Generator[np.ndarray, None, None]:
    """Generates dummy data using the camera device"""
    for i in range(num_frames):
        yield await camera.grab()

darks = await Acquisition("darks", np.ndarray, partial(produce, 1))
flats = await Acquisition("flats", np.ndarray, partial(produce, 2))
radios = await Acquisition("radios", np.ndarray, partial(produce, 20))
acquisitions = [darks, flats, radios]

exp = await Experiment(acquisitions)
await Consumer(viewer, exp.acquisitions)
