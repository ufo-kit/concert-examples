"""---\nSession showing image viewing functionality."""

import concert
concert.require("0.6")

import time
import numpy as np
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc
from concert.ext.viewers import PyplotImageViewer


def show_random(num=100):
    viewer = PyplotImageViewer()
    for i in range(num):
        viewer.show(np.random.random(size=(256, 256)))
        time.sleep(0.1)
    viewer.terminate()
