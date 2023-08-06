#!/usr/bin/python

#General modules
import argparse as ag
from collections import OrderedDict as OD


from affbio.utils import init_mpi, init_logging, finish_logging, dummy
from affbio.structures import load_pdb_coords, calc_rmsd_matrix
from affbio.prepare import prepare_cluster_matrix, calc_median, set_preference
from affbio.aff_cluster import aff_cluster, print_stat
from affbio.misc import render_b_factor, cluster_to_trj


def get_args(choices):
    """Parse cli arguments"""

    parser = ag.ArgumentParser(
        description='Parallel ffitiny propagation for biomolecules')

    parser.add_argument('-m',
                        required=True,
                        dest='Sfn',
                        metavar='FILE.hdf5',
                        help='HDF5 file for all matrices')

    parser.add_argument('--tier',
                        dest='tier',
                        metavar='TIER',
                        type=int,
                        default=1,
                        help='Round of clusterization')

    parser.add_argument('-t', '--task',
                        nargs='+',
                        required=True,
                        choices=choices,
                        metavar='TASK',
                        help='Task to do. Available options \
                        are: %s' % ", ".join(choices))

    parser.add_argument('-o', '--output',
                        dest='output',
                        metavar='OUTPUT',
                        help='For "render" ans "cluster_to_trj" tasks \
                        name of output PNG image of mutiframe PDB file')

    parser.add_argument('--debug',
                        action='store_true',
                        help='Perform profiling')

    parser.add_argument('--verbose',
                        action='store_true',
                        help='Be verbose')

    load_pdb = parser.add_argument_group('load_pdb')

    load_pdb.add_argument('-f',
                          nargs='*',
                          type=str,
                          dest='pdb_list',
                          metavar='FILE',
                          help='PDB files')

    load_pdb.add_argument('-s',
                          type=str,
                          dest='topology',
                          help='Topology PDB file')

    preference = parser.add_argument_group('calculate_preference')

    preference.add_argument('--factor',
                            type=float,
                            dest='factor',
                            metavar='FACTOR',
                            default=1.0,
                            help='Multiplier for median')
    preference.add_argument('--preference',
                            type=float,
                            dest='preference',
                            metavar='PREFERENCE',
                            help='Override computed preference')

    aff = parser.add_argument_group('aff_cluster')

    aff.add_argument('--conv_iter',
                     type=int,
                     dest='conv_iter',
                     metavar='ITERATIONS',
                     default=15,
                     help='Iterations to converge')

    aff.add_argument('--max_iter',
                     type=int,
                     dest='max_iter',
                     metavar='ITERATIONS',
                     default=2000,
                     help='Maximum iterations')

    aff.add_argument('--damping',
                     type=float,
                     dest='damping',
                     metavar='DAMPING',
                     default=0.95,
                     help='Damping factor')

    stat = parser.add_argument_group('print_stat')

    stat.add_argument('--merged_labels',
                      action='store_true',
                      dest='merged',
                      help='In case of tiers > 1 print labels merged \
                        according to hierarchy')

    render = parser.add_argument_group('render')

    render.add_argument('--draw_nums',
                        action='store_true',
                        help='Draw numerical labels')

    render.add_argument('--noclear',
                        dest='clear',
                        action='store_false',
                        help='Do not clear intermidiate files')

    render.add_argument('--width',
                        nargs='?', type=int, default=640,
                        help='Width of individual image')

    render.add_argument('--height',
                        nargs='?', type=int, default=480,
                        help='Height of individual image')

    render.add_argument('--moltype',
                        nargs='?', type=str, default="general",
                        choices=["general", "origami"],
                        help='Height of individual image')

    export = parser.add_argument_group('cluter_to_trj')

    export.add_argument('-i, --index',
                        metavar='INDEX',
                        type=int,
                        dest='index',
                        help='Index of cluster to be exported')

    args = parser.parse_args()

    args_dict = vars(args)

    return args_dict


def main_tasks():

    tasks = OD([
        ('load_pdb', load_pdb_coords),
        ('calc_rmsd', calc_rmsd_matrix),
        ('prepare_matrix', prepare_cluster_matrix),
        ('calc_median', calc_median),
        ('set_preference', set_preference),
        ('aff_cluster', aff_cluster),
        ('print_stat', print_stat)])

    return tasks


def misc_tasks():
    tasks = OD([
        ('cluster_to_trj', cluster_to_trj),
        ('render_results', render_b_factor)])
    return tasks


def wrapper_tasks():
    tasks = OD([
        ('cluster', dummy),
        ('all', dummy)])
    return tasks


def run_tasks(tasks, args):

    comm, NPROCS, rank = args['mpi']

    if len(tasks) == 1:
        tsk = tasks[0]

        if tsk == 'all':
            tasks = main_tasks().keys() + misc_tasks().keys()

        elif tsk == 'cluster':
            tasks = main_tasks().keys()

    for t in tasks:
        run_task(t, args)
        comm.Barrier()


def run_task(task, args):

    comm, NPROCS, rank = args['mpi']

    #Init logging
    if rank == 0:
        t0 = init_logging(task, args['verbose'])

        if args['debug'] is True:

            import cProfile
            import pstats
            import StringIO

            pr = cProfile.Profile()
            pr.enable()

    tasks = main_tasks()
    tasks.update(misc_tasks())
    fn = tasks[task]
    fn(**args)

    if rank == 0:
        finish_logging(task, t0, args['verbose'])

        if args['debug'] is True:
            pr.disable()
            s = StringIO.StringIO()
            sortby = 'tottime'
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            print s.getvalue()

    comm.Barrier()


def run():
    mpi = init_mpi()

    comm, NPROCS, rank = mpi

    args = None
    is_exit = False

    if rank == 0:
        try:
            tasks = main_tasks().keys() + misc_tasks().keys() + \
                wrapper_tasks().keys()
            args = get_args(tasks)
        except SystemExit:
            is_exit = True
    is_exit = comm.bcast(is_exit)

    if is_exit:
        exit(0)

    args = comm.bcast(args)

    args['mpi'] = mpi

    run_tasks(args['task'], args)


if __name__ == "__main__" and __package__ is None:
    run()
