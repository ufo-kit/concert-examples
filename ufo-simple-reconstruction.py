"""---\nThis session demonstrates reconstruction with the UFO data
processing framework.

Usage:
    await main()
"""

import asyncio
import concert
concert.require("0.30")

try:
    import gi
    gi.require_version('Ufo', '0.0')
    from gi.repository import Ufo
except ImportError as e:
    print(str(e))

import numpy as np
from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc
from concert.ext.ufo import PluginManager, InjectProcess
from concert.ext.viewers import PyplotImageViewer


viewer = PyplotImageViewer(title='Sinogram', fast=False)
slice_viewer = PyplotImageViewer(title='Slice', fast=False)


async def reconstruct(sino):
    pm = PluginManager()

    fft = pm.get_task('fft', dimensions=1)
    ifft = pm.get_task('ifft', dimensions=1)
    fltr = pm.get_task('filter')
    bp = pm.get_task('backproject')

    graph = Ufo.TaskGraph()
    graph.connect_nodes(fft, fltr)
    graph.connect_nodes(fltr, ifft)
    graph.connect_nodes(ifft, bp)

    with InjectProcess(graph, get_output=True) as process:
        await process.insert(sino)
        return await process.result(leave_index=0)


async def main():
    sino = np.random.normal(size=(1024, 1024)).astype(np.float32)
    sino[:, 760:770] = 5
    slc = await reconstruct(sino)
    await viewer.show(sino)
    await slice_viewer.show(slc)
