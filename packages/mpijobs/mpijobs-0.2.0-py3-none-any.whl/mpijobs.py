#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

'''Run jobs on many processes using MPI

This module uses mpi4py to run "jobs" (i.e., procedures) on different
MPI processes. The primary purpose of this library is to allow the
execution of multiple, *independent* jobs on many processes in
distributed-memory systems. It would be quite a quirk (and far from
its intended usage) to make such jobs communicate among them: the
spirit of the library is more like a GNU Parallel-like library for
MPI-based, distributed-memory systems.

The library requires the programmer to implement a descendant of the
``Job`` class which implements the ``run`` method. The programmer then
must call ``run_event_loop``, in order to start the computation. When
all the jobs have been computed, the function returns the list of jobs
that have been submitted to the MPI processes.

Only slave processes run the jobs. The purpose of the master process
is simply to submit jobs to any slave which can accept it (i.e., it is
not running another job at the same time). This means that, for ``n``
MPI processes, only ``n-1`` will actually run the jobs.

'''

from version import __version__

from datetime import datetime, timedelta
from enum import Enum
from mpi4py import MPI

import logging as log

class JobStatus(Enum):
    'The running status of a job'

    finished = 1
    running = 2
    queued = 3


class Job:

    '''A task to be run by one of the MPI processes

    Redefine the `run` method in a descendant to do something
    useful.
    '''

    def __init__(self,
                 status=JobStatus.queued,
                 running_time=None):
        self.status = status
        self.running_time = running_time

    def __repr__(self):
        return ('<Job({status})>'
                .format(status=self.status))

    def run(self, rank):
        '''Run the current job

        Reimplement this function in descendants to provide the
        ability to actually do the tasks required by this job.

        The ``rank`` parameter is equal to the rank of the job within
        the MPI communicator being used by ``run_event_loop``.
        '''

        pass


# We cannot use "namedtuple" to define _RankedRequest, as it must be a
# mutable object (the ``request`` field changes during lifetime).
class _RankedRequest:
    '''A request sent from some MPI process to another.

    The request is "ranked" because the rank of the sender is
    memorized in the object.'''

    def __init__(self, rank, request, job):
        self.rank = rank
        self.request = request
        self.job = job

    def __repr__(self):
        return ('<_RankedRequest(rank={rank}, request={request})>'
                .format(rank=self.rank,
                        request=self.request))


def run_master(comm, rank, job_list, log_flag=False, callback=None):
    '''Event loop for the master MPI process.

    This function must be called by the MPI process that will play the
    master's part. Other processes must use ``run_slave`` as their
    event loop.

    ``comm`` is the MPI communicator to use. ``rank`` is the rank of
    the current process. ``job_list`` is a list of instances of
    ``Job`` (or, more likely, a descendent). ``log_flag``, when true,
    causes log messages to be produced via calls to the ``logging``
    module.

    If ``callback`` is not none, it must be a function accepting two
    parameters. Every time a new job is submitted, the callback will be
    called with its two arguments being (1) the list of pending jobs,
    and (2) the list of jobs that have been completed. (The union of the
    two lists gives the list of jobs in the ``job_list`` parameter,
    *minus* the jobs that are currently running.)

    '''

    slave_requests = [_RankedRequest(rank=slave_rank,
                                     request=comm.irecv(None, slave_rank),
                                     job=None)
                      for slave_rank in range(1, comm.Get_size())]

    pending_job_list = job_list
    results = []
    listening_slaves = len(slave_requests)
    if callback:
        callback(pending_job_list, results)

    if log_flag:
        log.info('{0} jobs to run'.format(len(pending_job_list)))

    while listening_slaves > 0:
        for cur_idx in range(len(slave_requests)):
            ready, result = slave_requests[cur_idx].request.test()
            if ready:
                if result:
                    results.append(result)

                # Tell the slave what to do
                if pending_job_list:
                    new_job = pending_job_list.pop()
                    new_job.status = JobStatus.running
                    slave_requests[cur_idx].job = new_job
                else:
                    new_job = None # No more jobs to submit to slaves
                    listening_slaves -= 1

                comm.send(obj=new_job, dest=slave_requests[cur_idx].rank)

                if log_flag:
                    log.info('job sent to process #{0}, still {1} jobs left'
                             .format(slave_requests[cur_idx].rank,
                                     len(pending_job_list)))

                if callback:
                    callback(pending_job_list, results)

                # Be ready to get the next question from the slave
                new_request = comm.irecv(None, slave_requests[cur_idx].rank)
                slave_requests[cur_idx].request = new_request

    # Close all pending communications
    for req in slave_requests:
        req.request.Cancel()

    # Send to all the slaves an empty job, telling them to quit
    for rank in range(1, comm.Get_size()):
        comm.send(None, dest=rank)

    if log_flag:
        log.info('the master has completed its operations.')

    return results


def run_slave(comm, rank):
    '''Event loop for a slave MPI process.

    This function must be called by all the MPI processes that are not
    the "master" (usually, any process with rank != 0).

    ``comm`` is the MPI communicator to use.
    ``rank`` is the rank of the current process.
    ``slave_params`` will be passed to the ``Job.run`` method.
    '''

    last_job = None
    while True:
        # Ask the master what to do
        comm.isend(last_job, dest=0)

        # Get the master's command
        job = comm.recv(source=0)
        if not job:
            return # The server sent "None": no jobs left, so quit

        # Do what the server told you
        start_time = datetime.now()

        job.run(comm.rank)

        end_time = datetime.now()
        job.status = JobStatus.finished
        job.running_time = end_time - start_time

        last_job = job


def run_event_loop(comm, job_list, master_rank=0, log_flag=False, callback=None):
    '''Run the main event loop.

    This function must be called by all the MPI process (both the
    master and the set of slaves). Regardless of the rank of the
    running MPI process, it will return the list of jobs computed by
    *all* the MPI processes.

    The ``comm`` parameter specifies the MPI communicator to use
    (usually ``COMM_WORLD``). The ``job_list`` parameter is a list of
    ``Job`` objects that must be ran by the MPI processes. The
    ``master_rank`` parameter specifies which MPI process will play
    the master's part. The ``log_flag`` parameter, if ``True``, print
    progress updates via the ``logging`` library.

    If ``callback`` is not none, it must be a function accepting two
    parameters. Every time a new job is submitted, the callback will be
    called with its two arguments being (1) the list of pending jobs,
    and (2) the list of jobs that have been completed. (The union of the
    two lists gives the list of jobs in the ``job_list`` parameter,
    *minus* the jobs that are currently running.)
    '''

    assert master_rank < comm.size, \
      "the rank of the master must be less than the " \
      "number of MPI processes actually running"

    if comm.rank == master_rank:
        results = run_master(comm, comm.rank, job_list, log_flag, callback)
    else:
        run_slave(comm, comm.rank)
        results = None

    return comm.bcast(results, root=master_rank)
