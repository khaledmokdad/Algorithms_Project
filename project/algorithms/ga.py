import numpy as np
from scheduling import greedy_assignment, population_makespan


def solve_ga(instance, seed, population_size=40, generations=120,
             crossover_rate=0.9, mutation_rate=0.025, tournament_size=3, elite_count=2):
    rng = np.random.default_rng(seed)
    n, m = instance.jobs, instance.machines
    population = rng.integers(0, m, size=(population_size, n), dtype=np.int32)
    population[0] = greedy_assignment(instance)
    scores = population_makespan(instance, population)
    best = int(np.argmin(scores))
    best_solution, best_value = population[best].copy(), int(scores[best])
    history = [best_value]
    for _ in range(generations):
        ranking = np.lexsort((np.arange(population_size), scores))
        children = [population[i].copy() for i in ranking[:elite_count]]
        while len(children) < population_size:
            parents = []
            for _ in range(2):
                candidates = rng.integers(0, population_size, size=tournament_size)
                parents.append(population[candidates[np.argmin(scores[candidates])]])
            if rng.random() < crossover_rate:
                mask = rng.random(n) < 0.5
                offspring = [np.where(mask, parents[0], parents[1]), np.where(mask, parents[1], parents[0])]
            else:
                offspring = [parents[0].copy(), parents[1].copy()]
            for child in offspring:
                change = rng.random(n) < mutation_rate
                if m > 1:
                    child[change] = (child[change] + rng.integers(1, m, size=int(change.sum()))) % m
                children.append(child)
                if len(children) == population_size:
                    break
        population = np.asarray(children, dtype=np.int32)
        scores = population_makespan(instance, population)
        best = int(np.argmin(scores))
        if scores[best] < best_value:
            best_solution, best_value = population[best].copy(), int(scores[best])
        history.append(best_value)
    return best_solution, best_value, history
