import numpy as np
from scheduling import greedy_assignment, population_makespan


def solve_pso(instance, seed, swarm_size=40, iterations=120,
              inertia=0.72, c1=1.45, c2=1.45, velocity_limit=2.5):
    rng = np.random.default_rng(seed)
    n, m = instance.jobs, instance.machines
    position = rng.uniform(-1, 1, size=(swarm_size, n, m))
    velocity = rng.uniform(-0.25, 0.25, size=position.shape)
    position[0] = -1
    position[0, np.arange(n), greedy_assignment(instance)] = 1
    velocity[0] = 0
    assignments = position.argmax(axis=2).astype(np.int32)
    scores = population_makespan(instance, assignments)
    personal_position, personal_value = position.copy(), scores.copy()
    winner = int(scores.argmin())
    global_position = position[winner].copy()
    best_assignment, best_value = assignments[winner].copy(), int(scores[winner])
    history = [best_value]
    for _ in range(iterations):
        cognitive = c1 * rng.random(position.shape) * (personal_position - position)
        social = c2 * rng.random(position.shape) * (global_position[None, :, :] - position)
        velocity = np.clip(inertia * velocity + cognitive + social, -velocity_limit, velocity_limit)
        position = np.clip(position + velocity, -4, 4)
        assignments = position.argmax(axis=2).astype(np.int32)
        scores = population_makespan(instance, assignments)
        improved = scores < personal_value
        personal_value[improved] = scores[improved]
        personal_position[improved] = position[improved]
        winner = int(scores.argmin())
        if scores[winner] < best_value:
            best_value = int(scores[winner])
            best_assignment = assignments[winner].copy()
            global_position = position[winner].copy()
        history.append(best_value)
    return best_assignment, best_value, history
