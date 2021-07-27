"""---\nDemonstrating Concert capabilities.

Usage:
    print(ring)
    print(motor)
    print(camera)
"""

import concert
concert.require("0.30")

import numpy as np
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc, code_of
from concert.devices.cameras.dummy import Camera
from concert.devices.motors.dummy import LinearMotor
from concert.devices.storagerings.dummy import StorageRing


ring = StorageRing()
motor = LinearMotor()
camera = Camera()
