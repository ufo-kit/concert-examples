import timeit

N_SETS = 1000
N_RUNS = 3

setup_futures = """
from concert.quantities import q
from concert.helpers import wait
from concert.devices.motors.dummy import Motor

m = Motor()

def test_set_position():
    futures = [m.set_position(0 * q.mm) for i in range({})]
    wait(futures)
""".format(N_SETS)

setup_raw = """
from concert.quantities import q
from concert.helpers import wait
from concert.devices.motors.dummy import Motor

m = Motor()

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
