"""---\nBenchmark coroutines performance.

Usage:
    benchmark()
"""
import concert
concert.require("0.31")

import timeit

N_SETS = 1000
N_RUNS = 3

setup_futures = """
import asyncio
from concert.quantities import q
from concert.devices.motors.dummy import LinearMotor

m = asyncio.get_event_loop().run_until_complete(LinearMotor())

async def set_position():
    coros = [m.set_position(0 * q.mm) for i in range({})]
    await asyncio.gather(*coros)

def test_set_position():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_position())
""".format(N_SETS)

setup_raw = """
import asyncio
from concert.quantities import q
from concert.devices.motors.dummy import LinearMotor

m = asyncio.get_event_loop().run_until_complete(LinearMotor())

def test_set_position():
    for i in range({}):
        m.position = 0 * q.mm
""".format(N_SETS)


def benchmark():
    futures_time = timeit.timeit('test_set_position()', setup=setup_futures, number=N_RUNS)
    raw_time = timeit.timeit('test_set_position()', setup=setup_raw, number=N_RUNS)

    print("Futures: {:.2f} ops/s".format(N_SETS * N_RUNS / futures_time))
    print("Raw: {:.2f} ops/s".format(N_SETS * N_RUNS / raw_time))


if __name__ == '__main__':
    benchmark()
