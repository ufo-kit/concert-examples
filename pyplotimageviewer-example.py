"""Session showing image viewing functionality."""
import time
import numpy as np
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc
from concert.ext.viewers import PyplotImageViewer


__doc__ = "This is session pyplotviewer-example"


def show_random(num=100):
    viewer = PyplotImageViewer()
    for i in range(num):
        viewer.show(np.random.random(size=(256, 256)))
        time.sleep(0.1)
    viewer.terminate()
