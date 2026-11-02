import numpy as np
from scheduling import greedy_assignment, population_makespan


def solve_aco(instance, seed, ants=40, iterations=120, alpha=1.0, beta=2.2, evaporation=0.2):
    rng = np.random.default_rng(seed)
    n, m = instance.jobs, instance.machines
    times = instance.processing_times
    order = np.lexsort((np.arange(n), -times.min(axis=1)))
    pheromone = np.ones((n, m), dtype=float)
    rows = np.arange(ants)
    best_assignment, best_value = None, np.iinfo(np.int64).max
    history = []
    for iteration in range(iterations + 1):
        assignments = np.empty((ants, n), dtype=np.int32)
        loads = np.zeros((ants, m), dtype=np.int64)
        for job in order:
            projected = loads + times[job][None, :]
            attraction = pheromone[job][None, :]**alpha / projected.astype(float)**beta
            probability = attraction / attraction.sum(axis=1, keepdims=True)
            cumulative = probability.cumsum(axis=1)
            cumulative[:, -1] = 1
            machine = (cumulative < rng.random(ants)[:, None]).sum(axis=1)
            assignments[:, job] = machine
            loads[rows, machine] += times[job, machine]
        if iteration == 0:
            assignments[0] = greedy_assignment(instance)
        scores = population_makespan(instance, assignments)
        winner = int(scores.argmin())
        current = int(scores[winner])
        if current < best_value:
            best_value = current
            best_assignment = assignments[winner].copy()
        pheromone *= 1 - evaporation
        pheromone[np.arange(n), assignments[winner]] += 1.0 / current
        pheromone[np.arange(n), best_assignment] += 1.5 / best_value
        pheromone = np.maximum(pheromone, 1e-6)
        history.append(best_value)
    return best_assignment, best_value, history
