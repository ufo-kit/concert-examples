"""# *focus* session manual

## Usage
    await main()

## Notes
"""

import asyncio
import logging
from inspect import iscoroutinefunction
import concert
concert.require("0.30.0")

from concert.devices.motors.dummy import LinearMotor
from concert.ext.viewers import PyplotImageViewer, PyplotViewer
from concert.processes.common import focus
from concert.tests.util.focus import BlurringCamera, FOCUS_POSITION
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc, code_of

LOG = logging.getLogger(__name__)


motor = LinearMotor()
motor.position = 0 * q.mm
motor.motion_velocity = 5 * q.mm / q.s
camera = BlurringCamera(motor)
viewer = PyplotImageViewer(limits='auto', fast=False)
line = PyplotViewer('-o')


async def main():
    await focus(camera, motor, frame_callback=viewer.show, plot_callback=line.show,
                opt_kwargs={'initial_step': 5 * q.mm, 'epsilon': 1e-2 * q.mm})
    print(f'Motor position: {await motor.get_position()}, should be: {FOCUS_POSITION}')
