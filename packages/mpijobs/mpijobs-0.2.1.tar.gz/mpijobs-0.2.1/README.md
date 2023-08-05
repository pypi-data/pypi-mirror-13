# Mpijobs

A Python3 library for running many jobs on multiple processes, using
MPI.

## Example

The following example runs 3 jobs. For each of them, a message is
printed on the screen.

`````python
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
`````

The program must be run using ``mpirun`` (or an equivalent program,
depending on your MPI library):

    mpirun -n 3 python3 example.py

The output is the following (actual ranks and times might vary):

    Hi, I am Stephen (process 2)
    Hi, I am Alice (process 1)
    Hi, I am Bob (process 1)
    strings computed by the processes = [ALICE, STEPHEN, BOB]
    elapsed_time = [0:00:01.001056, 0:00:01.001088, 0:00:01.001041]

## Copyright

See the COPYRIGHT.md file.
