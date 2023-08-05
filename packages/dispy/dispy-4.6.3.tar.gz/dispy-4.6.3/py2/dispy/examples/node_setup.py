# Example program that uses 'setup' and 'cleanup' functions to
# initialize/de-initialize global variables on each node before
# computations are executed. Computations use data in global variables
# instead of reading input for each job.

# Under Windows global variables must be serializable, so modules
# can't be global variables: See
# https://docs.python.org/2/library/multiprocessing.html#windows for
# details. This example is implemented to load 'hashlib' module in
# computation (for each job). When executing in posix (Linux, OS X and
# other Unix variants), 'hashlib' can be declared global variable and
# module loaded in 'setup' (and deleted in 'cleanup').

# executed on each node before any jobs are scheduled
def setup(data_file):
    # read data in file to global variable
    global data, algorithms
    import hashlib
    data = open(data_file).read()
    if sys.version_info.major >= 3:
        data = data.encode()
        algorithms = list(hashlib.algorithms_guaranteed)
    else:
        algorithms = list(hashlib.algorithms)
# it should return 0 to indicate successful initialization
    return 0

# executed on each node when compuation is closed
def cleanup():
    global data, algorithms
    del data, algorithms

# job computation
def compute(n):
    import hashlib
    # 'data' and 'algorithms' global variables are initialized in 'setup'
    alg = algorithms[n % len(algorithms)]
    csum = getattr(hashlib, alg)()
    csum.update(data)
    return (alg, csum.hexdigest())

if __name__ == '__main__':
    import dispy, sys, functools
    data_file = sys.argv[1] if len(sys.argv) > 1 else sys.argv[0]
    cluster = dispy.JobCluster(compute, depends=[data_file],
                               setup=functools.partial(setup, data_file), cleanup=cleanup)
    jobs = []
    for n in range(10):
        job = cluster.submit(n)
        job.id = n
        jobs.append(job)

    for job in jobs:
        job()
        if job.status == dispy.DispyJob.Finished:
            print('%s: %s : %s' % (job.id, job.result[0], job.result[1]))
        else:
            print(job.exception)
    cluster.stats()
    cluster.close()
