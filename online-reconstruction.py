"""# *online-reconstruction* demonstrates how to attach online reconstruction addon to an
experiment and how to set it up for absorption 3D reconstruction.

## Usage
    
    # region=[start, stop, step] region of vertical slice positions to reconstruct
    await main(region=None)

"""

import logging
import numpy as np
import concert
concert.require("0.31.0")

from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc, code_of
from concert.ext.viewers import PyQtGraphViewer
from concert.ext.ufo import GeneralBackprojectArgs, GeneralBackprojectManager
from concert.experiments.addons import Consumer, OnlineReconstruction
from concert.experiments.dummy import ImagingExperiment
from concert.progressbar import wrap_iterable


LOG = logging.getLogger(__name__)


class SmartImagingExperiment(ImagingExperiment):

    def take_darks(self):
        return self._produce_images(self.num_darks, mean=50, std=5)

    def take_flats(self):
        return self._produce_images(self.num_flats, mean=1000, std=30)

    async def take_radios(self):
        """Simulate an off-centered sphere with 80 % absorption."""
        thickness = np.zeros(self.shape)
        h, w = self.shape
        radius = min(h, w) // 4
        y, x = np.mgrid[-h // 2:h // 2, -w // 2:w // 2]
        valid = np.where(x ** 2 + y ** 2 < radius ** 2)
        thickness[valid] = 2 * np.sqrt(radius ** 2 - x[valid] ** 2 - y[valid] ** 2)
        mju = -np.log(0.2) / (2 * radius)  # 80 % absorpbion
        projection = (1000 * np.exp(-thickness * mju))

        for i in wrap_iterable(range(self.num_radios)):
            dx = int(np.sin(i / self.num_radios * np.pi) * 0.8 * radius)
            yield np.roll(np.random.poisson(projection).astype(self.dtype), dx, axis=1)


n = 512
live_viewer = await PyQtGraphViewer(show_refresh_rate=True, title='Projections')
slice_viewer = await PyQtGraphViewer(limits='auto', title='Slice')
args = GeneralBackprojectArgs([n // 2], [n // 2 + 0.5], n, overall_angle=np.pi)
args.absorptivity = True
args.fix_nan_and_inf = True
args.region = [-100.0, 101.0, 100.0]
manager = await GeneralBackprojectManager(args)
ex = await SmartImagingExperiment(100, 100, n, shape=(n, n), random='multi')
live = Consumer(ex.acquisitions, live_viewer)
reco = await OnlineReconstruction(ex, args, do_normalization=True, average_normalization=True)


async def main(region=None):
    if region is None:
        region = [-100.0, 101.0, 100.0]
    args.region = [float(value) for value in region]    # UFO needs floats
    await ex.run()
    await slice_viewer.show(reco.manager.volume[len(reco.manager.volume) // 2])
