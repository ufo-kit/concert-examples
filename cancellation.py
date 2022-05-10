"""# *cancellation* session manual

## Usage

    t_1, t_2 = move_two()
    # hit ctrl-k
    print(t_1.cancelled(), t_2.cancelled())
    print(motor_1.state, motor_2.state)

    t_1, t_2 = move_two()
    t_3 = motor_3.set_position(100 * q.mm)
    await t_3
    # hit ctrl-c
    print(t_1.cancelled(), t_2.cancelled(), t_3.cancelled())
    print(motor_1.state, motor_2.state, motor_3.state)

## Notes
"""

import logging
from inspect import iscoroutinefunction
import concert
concert.require("0.31")

from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc, code_of
from concert.devices.motors.dummy import LinearMotor

LOG = logging.getLogger(__name__)


class CleanMotor(LinearMotor):
    async def _emergency_stop(self):
        print('cleanup...')


motor_1 = await CleanMotor()
motor_2 = await LinearMotor()
motor_3 = await LinearMotor()
await motor_1.set_motion_velocity(1 * q.mm / q.s)
await motor_2.set_motion_velocity(1 * q.mm / q.s)
await motor_3.set_motion_velocity(1 * q.mm / q.s)


def move_two():
    return (
        motor_1.set_position(100 * q.mm),
        motor_2.set_position(100 * q.mm)
    )
