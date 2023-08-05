#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from mpi4py import MPI
from time import sleep

import mpijobs

class MyJob(mpijobs.Job):
    def __init__(self,
                 params):
        super().__init__()
        self.params = params
        self.result_str = None

    def run(self, rank):
        print("Hi, I am {0} (process {1})".format(self.params, rank))

        # Pretend you're doing something useful
        sleep(1.0)

        # Perform a simple computation and save the result
        self.result_str = self.params.upper()

JOB_LIST = [MyJob(name) for name in ('Bob', 'Alice', 'Stephen')]
RESULTS = mpijobs.run_event_loop(MPI.COMM_WORLD, JOB_LIST)

if MPI.COMM_WORLD.rank == 0: # Only one process should print the results
    print("strings computed by the processes = [{0}]"
          .format(', '.join([x.result_str for x in RESULTS])))
    print("elapsed_time = [{0}]"
          .format(', '.join([str(x.running_time) for x in RESULTS])))
