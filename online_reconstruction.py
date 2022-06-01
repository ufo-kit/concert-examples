"""# *online-reconstruction* demonstrates how to attach online reconstruction addon to an
experiment and how to set it up for absorption 3D reconstruction.

## Usage
    
    # region=[start, stop, step] region of vertical slice positions to reconstruct
    await main(region=None)

"""

import logging
import numpy as np
import os
import shutil
import time
import concert
concert.require("0.31.0")

from concert.quantities import q
from concert.session.utils import ddoc, dstate, pdoc, code_of
from concert.devices.cameras.uca import Camera
from concert.ext.viewers import PyQtGraphViewer, PyplotImageViewer
from concert.ext.ufo import QuantifiedArgs, GeneralBackprojectManager
from concert.experiments.addons import Consumer, ImageWriter, OnlineReconstruction
from concert.experiments.dummy import ImagingExperiment
from concert.experiments.proxies.local import Consumer as LocalConsumer
from concert.storage import DirectoryWalker
from concert.progressbar import wrap_iterable


LOG = logging.getLogger(__name__)
concert.config.PROGRESS_BAR = False


class SmartImagingExperiment(ImagingExperiment):

    async def __ainit__(self, num_darks, num_flats, num_radios, shape=(1024, 1024), walker=None,
                        random=False, dtype=np.ushort, separate_scans=True, name_fmt='scan_{:>04}',
                        make_sphere=True, camera=None):
        await super().__ainit__(num_darks, num_flats, num_radios, shape=shape, walker=walker,
                                random=random, dtype=dtype, separate_scans=separate_scans,
                                name_fmt=name_fmt)
        self.make_sphere = make_sphere
        self.camera = camera

    async def _produce_with_camera(self, num):
        async with self.camera.recording():
            for i in range(num):
                yield await self.camera.grab()

    def take_darks(self):
        if self.camera:
            return self._produce_with_camera(self.num_darks)
        else:
            return self._produce_images(self.num_darks, mean=50, std=5)

    def take_flats(self):
        if self.camera:
            return self._produce_with_camera(self.num_flats)
        else:
            return self._produce_images(self.num_flats, mean=1000, std=30)

    async def _produce_sphere(self):
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

    def take_radios(self):
        if self.camera:
            return self._produce_with_camera(self.num_radios)
        if self.make_sphere:
            return self._produce_sphere()
        else:
            return self._produce_images(self.num_radios)


n = 512

# camera = await Camera('net')
# await camera.set_fill_data(False)
# await camera.set_roi_width(n * q.px)
# await camera.set_roi_height(n * q.px)
# await camera.set_frame_rate(1e6 / q.s)

live_viewer = await PyQtGraphViewer(show_refresh_rate=True, title='Projections')
slice_viewer = await PyQtGraphViewer(limits='auto', title='Slice')
# manager = await GeneralBackprojectManager(args)
ex = await SmartImagingExperiment(100, 100, n, shape=(n, n), random='multi')
live = await Consumer(ex.acquisitions, await LocalConsumer(live_viewer))
reco = await OnlineReconstruction(ex, do_normalization=True, average_normalization=True)
args = reco.args
await args.set_center_position_x([n // 2] * q.pixel)
await args.set_center_position_z([n // 2 + 0.5] * q.pixel)
await args.set_number(n)
await args.set_overall_angle(np.pi * q.rad)
await args.set_absorptivity(True)
await args.set_fix_nan_and_inf(True)
await args.set_region([-100.0, 101.0, 100.0])


async def main(region=None, live_preview=True, write_path=None, online_reco=False,
               viewer=live_viewer):
    """Run the example and output the experiment data to a dummy walker.
    Also show the images in a live preview addon.
    """
    if live_preview:
        live = await Consumer(ex.acquisitions, await LocalConsumer(viewer))
    if write_path:
        walker = DirectoryWalker(root=write_path, bytes_per_file=2 ** 40)
        writer = await ImageWriter(ex.acquisitions, walker)

    # There is some initialization involved so let's not re-create the reconstruction all the time
    if online_reco:
        await reco.attach()
    else:
        await reco.detach()

    if region is None:
        region = [-100.0, 101.0, 100.0]
    await args.set_region([float(value) for value in region])    # UFO needs floats

    try:
        st = time.perf_counter()
        await ex.run()
        duration = time.perf_counter() - st
        num_images = ex.num_radios + ex.num_flats + ex.num_darks
        if ex.camera:
            bpp = (await ex.camera.get_sensor_bitdepth()).magnitude
        else:
            bpp = np.iinfo(ex.dtype).bits
        image_size = n ** 2 * bpp // 8
        mb = image_size * num_images / 2 ** 20
        print(f'Duration: {duration:.2f} s, data size: {mb:.2f} MB, throughput: {mb / duration:.2f} MB/s')

        if online_reco:
            await slice_viewer.show(await reco.get_slice(z=0))
            # volume = await reco.get_volume()
            # await slice_viewer.show(volume[len(volume) // 2])
    finally:
        if live_preview:
            await live.detach()
        if write_path:
            await writer.detach()
            for acq in ex.acquisitions:
                to_delete = os.path.join(write_path, acq.name)
                print(f'Deleting {to_delete}')
                shutil.rmtree(to_delete)
