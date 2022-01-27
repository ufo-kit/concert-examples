"""# *focus* session manual

## Usage
    await main()

## Notes
"""

import logging
from inspect import iscoroutinefunction
import concert
concert.require("0.30.0")

from concert.devices.motors.dummy import LinearMotor
from concert.ext.viewers import PyplotImageViewer
from concert.processes.common import focus
from concert.tests.util.focus import BlurringCamera, FOCUS_POSITION
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc, code_of

LOG = logging.getLogger(__name__)


motor = LinearMotor()
camera = BlurringCamera(motor)
viewer = PyplotImageViewer(limits='auto', fast=False)


async def main():
    await focus(camera, motor, frame_callback=viewer.show)
    print(f'Motor position: {await motor.get_position()}, should be: {FOCUS_POSITION}')
