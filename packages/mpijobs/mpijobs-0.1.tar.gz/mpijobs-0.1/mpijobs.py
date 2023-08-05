#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

'''Run jobs on many processes using MPI

This module uses mpi4py to run "jobs" (i.e., procedures) on different
MPI processes. It requires the programmer to implement a descendant of
the ``Job`` class which implements the ``run`` method. The programmer
then must manually call ``run_master`` or ``run_slave``, depending on
the rank of the MPI process. The function ``run_master`` should be
called only once, passing as argument a list of ``Job`` objects. The
``run_slave`` must be run by all the other MPI Processes.

Only slave processes will actually run the jobs. The purpose of the
master process is simply to submit jobs to any slave which can accept
it (i.e., it is not running another job at the same time). This means
that, for ``n`` MPI processes, only ``n-1`` will actually run the
jobs.

'''

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
        return ('<Job({status}, {running_time})>'
                .format(status=self.status,
                        running_time=self.running_time.total_seconds()))

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

    def __init__(self, rank, request):
        self.rank = rank
        self.request = request

    def __repr__(self):
        return ('<_RankedRequest(rank={rank}, request={request})>'
                .format(rank=self.rank,
                        request=self.request))


def run_master(comm, rank, job_list, log_flag=False):
    '''Event loop for the master MPI process.

    This function must be called by the MPI process that will play the
    master's part. Other processes must use ``run_slave`` as their
    event loop.

    ``comm`` is the MPI communicator to use. ``rank`` is the rank of
    the current process. ``job_list`` is a list of instances of
    ``Job`` (or, more likely, a descendent). ``log_flag``, when true,
    causes log messages to be produced via calls to the ``logging``
    module.

    '''

    slave_requests = [_RankedRequest(rank=slave_rank,
                                     request=comm.irecv(dest=slave_rank))
                      for slave_rank in range(1, comm.Get_size())]

    pending_job_list = job_list
    log.info('{0} jobs to run'.format(len(pending_job_list)))
    while pending_job_list:
        for cur_idx in range(len(slave_requests)):
            ready, result = slave_requests[cur_idx].request.test()
            if ready:
                # Tell the slave what to do
                if pending_job_list:
                    new_job = pending_job_list.pop()
                    new_job.status = JobStatus.running
                else:
                    new_job = None # No more jobs to submit to slaves
                comm.send(obj=new_job, dest=slave_requests[cur_idx].rank)

                if log_flag:
                    log.info('job sent to process #{0}, still {1} jobs left'
                             .format(slave_requests[cur_idx].rank,
                                     len(pending_job_list)))

                # Be ready to get the next question from the slave
                new_request = comm.irecv(dest=slave_requests[cur_idx].rank)
                slave_requests[cur_idx].request = new_request

    # Close all pending communications
    for req in slave_requests:
        req.request.Cancel()

    # Send to all the slaves an empty job, telling them to quit
    for rank in range(1, comm.Get_size()):
        comm.send(None, dest=rank)

    if log_flag:
        log.info('the master has completed its operations.')


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


def run_event_loop(comm, job_list, master_rank=0, log_flag=False):
    '''Run the main event loop.

    The ``comm`` parameter specifies the MPI communicator to use
    (usually ``COMM_WORLD``). The ``job_list`` parameter is a list of
    ``Job`` objects that must be ran by the MPI processes. The
    ``master_rank`` parameter specifies which MPI process will play
    the master's part. The ``log_flag`` parameter, if ``True``, print
    progress updates via the ``logging`` library.
    '''

    assert master_rank < comm.size, \
      "the rank of the master must be less than the " \
      "number of MPI processes actually running"

    if comm.rank == master_rank:
        run_master(comm, comm.rank, job_list, log_flag)
    else:
        run_slave(comm, comm.rank)
