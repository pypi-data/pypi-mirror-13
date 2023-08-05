# This program uses status message notifications to submit jobs to
# discoro processes.

import asyncoro.disasyncoro as asyncoro
import asyncoro.discoro as discoro
from asyncoro.discoro_schedulers import RemoteCoroScheduler

# this generator function is sent to remote server to run
# coroutines there
def rcoro_proc(n, coro=None):
    yield coro.sleep(n)


def client_proc(computation, njobs, coro=None):
    # use RemoteCoroScheduler to schedule/submit coroutines; scheduler must be
    # created before computation is scheduled (next step below)
    rcoro_scheduler = RemoteCoroScheduler(computation)
    # schedule computation (if scheduler is shared, this waits until
    # prior computations are finished)
    if (yield computation.schedule()):
        raise Exception('Failed to schedule computation')

    # create njobs remote coroutines
    for n in range(njobs):
        rcoro = yield rcoro_scheduler.schedule(rcoro_proc, random.uniform(5, 10))

    # scheduler will wait until all remote coroutines finish
    yield rcoro_scheduler.finish(close=True)


if __name__ == '__main__':
    import logging, random
    asyncoro.logger.setLevel(logging.DEBUG)
    # if scheduler is not already running (on a node as a program),
    # start it (private scheduler):
    discoro.Scheduler()
    computation = discoro.Computation([rcoro_proc])
    # run 10 jobs
    asyncoro.Coro(client_proc, computation, 10).value()
