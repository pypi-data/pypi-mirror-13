#General modules
import time

#MPI parallelism
from mpi4py import MPI


def dummy(*args, **kwargs):
    pass


def init_mpi():
    #Get MPI info
    comm = MPI.COMM_WORLD
    #Get number of processes
    NPROCS = comm.size
    #Get rank
    rank = comm.rank

    return (comm, NPROCS, rank)


def master(fn):
    comm, NPROCS, rank = init_mpi()

    if rank == 0:
        return fn
    else:
        return dummy


class Bunch(object):
    def __init__(self, adict):
        self.__dict__.update(adict)


def task(N, NPROCS, rank):
    l = N / NPROCS
    b = rank * l
    return (b, b + l)


def init_logging(task, verbose=False):
    if verbose:

        print 'Starting task: %s' % task

    #Get current time
    t0 = time.time()

    return t0


def finish_logging(task, t0, verbose=False):
    if verbose:
        print "Task: %s execution time is %f" % (task, time.time() - t0)
