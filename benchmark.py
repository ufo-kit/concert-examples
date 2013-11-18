import timeit

N_SETS = 1000
N_RUNS = 3

setup = """
from concert.quantities import q
from concert.helpers import wait
from concert.devices.motors.dummy import Motor

m = Motor()

def test_set_position():
    futures = [m.set_position(0 * q.mm) for i in range({})]
    wait(futures)
""".format(N_SETS)


def benchmark():
    time = timeit.timeit('test_set_position()', setup=setup, number=N_RUNS)
    print("Throughput: {:.2f} ops/s".format(N_SETS * N_RUNS / time))


if __name__ == '__main__':
    benchmark()
