from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class SchedulingInstance:
    name: str
    processing_times: np.ndarray

    def __post_init__(self):
        p = self.processing_times
        if p.ndim != 2 or min(p.shape) < 1 or np.any(p <= 0) or p.dtype.kind not in 'iu':
            raise ValueError('Processing times must be a nonempty matrix of positive integers')

    @property
    def jobs(self):
        return self.processing_times.shape[0]

    @property
    def machines(self):
        return self.processing_times.shape[1]


def generate_instance(jobs, machines, seed, name):
    rng = np.random.default_rng(seed)
    work = rng.integers(20, 201, size=jobs)
    speed = rng.uniform(0.70, 1.50, size=machines)
    noise = rng.uniform(0.85, 1.15, size=(jobs, machines))
    times = np.ceil(work[:, None] / speed[None, :] * noise).astype(np.int32)
    return SchedulingInstance(name, times)


def machine_loads(instance, assignment):
    a = np.asarray(assignment)
    if a.shape != (instance.jobs,) or a.dtype.kind not in 'iu':
        raise ValueError('One integer machine index is required for every job')
    if np.any(a < 0) or np.any(a >= instance.machines):
        raise ValueError('Machine index outside its range')
    loads = np.zeros(instance.machines, dtype=np.int64)
    np.add.at(loads, a, instance.processing_times[np.arange(instance.jobs), a])
    return loads


def makespan(instance, assignment):
    return int(machine_loads(instance, assignment).max())


def population_makespan(instance, assignments):
    a = np.asarray(assignments)
    if a.ndim != 2 or a.shape[1] != instance.jobs or a.dtype.kind not in 'iu':
        raise ValueError('Invalid assignment population')
    if np.any(a < 0) or np.any(a >= instance.machines):
        raise ValueError('Machine index outside its range')
    loads = np.zeros((len(a), instance.machines), dtype=np.int64)
    times = instance.processing_times[np.arange(instance.jobs)[None, :], a]
    np.add.at(loads, (np.arange(len(a))[:, None], a), times)
    return loads.max(axis=1)


def greedy_assignment(instance):
    times = instance.processing_times
    order = np.lexsort((np.arange(instance.jobs), -times.min(axis=1)))
    loads = np.zeros(instance.machines, dtype=np.int64)
    assignment = np.empty(instance.jobs, dtype=np.int32)
    for job in order:
        machine = int(np.argmin(loads + times[job]))
        assignment[job] = machine
        loads[machine] += times[job, machine]
    return assignment


def lower_bound(instance):
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    n, m = instance.jobs, instance.machines
    variables = n * m + 1
    columns = np.arange(n*m)
    equality = coo_matrix((np.ones(n*m), (np.repeat(np.arange(n), m), columns)), shape=(n, variables))
    machine_rows = np.tile(np.arange(m), n)
    inequality = coo_matrix((np.r_[instance.processing_times.ravel(), -np.ones(m)],
                            (np.r_[machine_rows, np.arange(m)], np.r_[columns, np.full(m, n*m)])),
                           shape=(m, variables))
    objective = np.zeros(variables)
    objective[-1] = 1
    result = linprog(objective, A_ub=inequality, b_ub=np.zeros(m),
                     A_eq=equality, b_eq=np.ones(n), bounds=(0, None), method='highs')
    if not result.success:
        raise RuntimeError(result.message)
    indivisible_job_bound = int(instance.processing_times.min(axis=1).max())
    bound = max(indivisible_job_bound, int(np.ceil(result.fun - 1e-7)))
    return bound, float(result.fun)
