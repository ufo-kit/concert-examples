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
concert.require("0.30.1")

from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc, code_of
from concert.devices.motors.dummy import LinearMotor

LOG = logging.getLogger(__name__)


motor_1 = LinearMotor()
motor_2 = LinearMotor()
motor_3 = LinearMotor()
motor_1.motion_velocity = 1 * q.mm / q.s
motor_2.motion_velocity = 1 * q.mm / q.s
motor_3.motion_velocity = 1 * q.mm / q.s


def move_two():
    return (
        motor_1.set_position(100 * q.mm),
        motor_2.set_position(100 * q.mm)
    )
