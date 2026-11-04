import argparse
import csv
import hashlib
import json
import platform
import statistics
import time
import tracemalloc
from pathlib import Path

import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from scheduling import generate_instance, greedy_assignment, makespan, machine_loads, lower_bound
from algorithms import solve_ga, solve_pso, solve_aco

ROOT = Path(__file__).resolve().parent
SIZES = {'small': (30, 4, 1101), 'medium': (100, 8, 2201), 'large': (300, 12, 3301)}
SOLVERS = {'GA': solve_ga, 'PSO': solve_pso, 'ACO': solve_aco}
COLORS = {'Greedy': '#6c757d', 'GA': '#235789', 'PSO': '#c77d15', 'ACO': '#33836b'}


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def memory_peak(function, *args, **kwargs):
    tracemalloc.start()
    try:
        function(*args, **kwargs)
        return tracemalloc.get_traced_memory()[1] / 1024
    finally:
        tracemalloc.stop()


def target_iteration(history, bound):
    return next((i for i, value in enumerate(history) if value <= 1.01 * bound), None)


def greedy_result(instance):
    assignment = greedy_assignment(instance)
    return assignment, makespan(instance, assignment)


def summarize(raw, instances):
    rows = []
    for size in SIZES:
        problems = [row for row in instances if row['size'] == size]
        greedy_gaps = [100 * (r['greedy_cmax'] - r['lower_bound']) / r['lower_bound'] for r in problems]
        rows.append({'size': size, 'algorithm': 'Greedy',
                     'mean_cmax': statistics.mean(r['greedy_cmax'] for r in problems),
                     'mean_gap_lb_pct': statistics.mean(greedy_gaps), 'within_instance_std': 0,
                     'mean_time_s': statistics.mean(r['greedy_time_s'] for r in problems),
                     'mean_peak_kib': statistics.mean(r['greedy_peak_kib'] for r in problems),
                     'hits_bound': f"{sum(r['greedy_cmax']==r['lower_bound'] for r in problems)}/3",
                     'target_hits': '-', 'mean_target_iteration': None})
        for algorithm in SOLVERS:
            selected = [r for r in raw if r['size'] == size and r['algorithm'] == algorithm]
            deviations = []
            for problem in problems:
                gaps = [r['gap_lb_pct'] for r in selected if r['instance_id'] == problem['instance_id']]
                deviations.append(statistics.stdev(gaps) if len(gaps) > 1 else 0)
            reached = [r['target_iteration'] for r in selected if r['target_reached']]
            rows.append({'size': size, 'algorithm': algorithm,
                         'mean_cmax': statistics.mean(r['cmax'] for r in selected),
                         'mean_gap_lb_pct': statistics.mean(r['gap_lb_pct'] for r in selected),
                         'within_instance_std': statistics.mean(deviations),
                         'mean_time_s': statistics.mean(r['time_s'] for r in selected),
                         'mean_peak_kib': statistics.mean(r[algorithm+'_peak_kib'] for r in problems),
                         'hits_bound': f"{sum(r['cmax']==r['lower_bound'] for r in selected)}/{len(selected)}",
                         'target_hits': f'{len(reached)}/{len(selected)}',
                         'mean_target_iteration': statistics.mean(reached) if reached else None})
    return rows


def plots(output, raw, instances, histories, assignments, problems):
    algorithms = list(SOLVERS)
    figure, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    for ax, size in zip(axes, SIZES):
        for algorithm in algorithms:
            indices = [i for i, row in enumerate(raw) if row['size'] == size and row['algorithm'] == algorithm]
            curves = [100 * (histories[i] - raw[i]['lower_bound']) / raw[i]['lower_bound'] for i in indices]
            ax.plot(np.mean(curves, axis=0), label=algorithm, color=COLORS[algorithm])
        ax.axhline(1, color='gray', ls=':', lw=1, label='1% target')
        ax.set_title(size.capitalize())
        ax.set_xlabel('Iteration')
        ax.grid(alpha=.25)
    axes[0].set_ylabel('Mean gap above lower bound (%)')
    axes[0].legend(fontsize=8)
    figure.tight_layout()
    figure.savefig(output/'convergence.png', dpi=190)
    plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(12, 3.7))
    for ax, size in zip(axes, SIZES):
        groups = [[row['gap_lb_pct'] for row in raw if row['size']==size and row['algorithm']==a] for a in algorithms]
        ax.boxplot(groups, tick_labels=algorithms)
        ax.set_title(size.capitalize())
        ax.grid(alpha=.25)
    axes[0].set_ylabel('Gap above lower bound (%)')
    figure.tight_layout()
    figure.savefig(output/'stability.png', dpi=190)
    plt.close(figure)

    summary = summarize(raw, instances)
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4))
    x = np.arange(3)
    for k, algorithm in enumerate(['Greedy'] + algorithms):
        selected = [next(row for row in summary if row['size']==s and row['algorithm']==algorithm) for s in SIZES]
        axes[0].bar(x + (k-1.5)*.2, [r['mean_time_s'] for r in selected], .2, label=algorithm, color=COLORS[algorithm])
        axes[1].bar(x + (k-1.5)*.2, [r['mean_peak_kib'] for r in selected], .2, label=algorithm, color=COLORS[algorithm])
    for ax in axes:
        ax.set_xticks(x, [s.capitalize() for s in SIZES])
        ax.set_yscale('log')
        ax.grid(axis='y',alpha=.25)
    axes[0].set_ylabel('Mean time (s)')
    axes[1].set_ylabel('Mean traced peak (KiB)')
    axes[0].legend(fontsize=8)
    figure.tight_layout()
    figure.savefig(output/'resources.png', dpi=190)
    plt.close(figure)

    first_large = next(row for row in instances if row['size']=='large')
    instance = problems[first_large['instance_id']]
    figure, axes = plt.subplots(2, 2, figsize=(10, 6.3))
    for ax, algorithm in zip(axes.flat, ['Greedy']+algorithms):
        if algorithm == 'Greedy':
            assignment = greedy_assignment(instance)
        else:
            candidates = [i for i,row in enumerate(raw) if row['instance_id']==instance.name and row['algorithm']==algorithm]
            winner = min(candidates, key=lambda i:raw[i]['cmax'])
            assignment = assignments[winner]
        loads = machine_loads(instance, assignment)
        ax.bar(np.arange(instance.machines), loads, color=COLORS[algorithm])
        ax.axhline(loads.max(),color='black',ls='--',lw=.8)
        ax.set_title(f'{algorithm}: Cmax = {loads.max()}')
        ax.set_xlabel('Machine')
        ax.set_ylabel('Load')
    figure.tight_layout()
    figure.savefig(output/'machine_loads.png', dpi=190)
    plt.close(figure)


def run_experiment(repeats, output):
    output.mkdir(parents=True, exist_ok=True)
    settings = json.loads((ROOT/'settings.json').read_text())
    raw, instances, data = [], [], []
    histories, assignments, problems = [], [], {}
    for size_index, (size, (jobs, machines, first_seed)) in enumerate(SIZES.items()):
        for case in range(3):
            instance_id = f'{size}_{case+1}'
            instance = generate_instance(jobs, machines, first_seed+case, instance_id)
            problems[instance_id] = instance
            bound, lp_value = lower_bound(instance)
            greedy = greedy_assignment(instance)
            greedy_value = makespan(instance, greedy)
            assert bound <= greedy_value
            measurements = []
            for _ in range(repeats):
                started = time.perf_counter()
                greedy_result(instance)
                measurements.append(time.perf_counter()-started)
            description = {'instance_id':instance_id, 'size':size, 'instance':case+1,
                           'jobs':jobs, 'machines':machines, 'instance_seed':first_seed+case,
                           'lp_value':lp_value, 'lower_bound':bound, 'greedy_cmax':greedy_value,
                           'greedy_time_s':statistics.mean(measurements),
                           'greedy_peak_kib':memory_peak(greedy_result, instance)}
            for job in range(jobs):
                for machine in range(machines):
                    data.append({'instance_id':instance_id,'job':job,'machine':machine,
                                 'processing_time':int(instance.processing_times[job,machine])})
            for algorithm, solver in SOLVERS.items():
                for repetition in range(repeats):
                    seed = 10000 + size_index*10000 + case*100 + repetition
                    started = time.perf_counter()
                    assignment, value, history = solver(instance, seed=seed, **settings[algorithm])
                    elapsed = time.perf_counter()-started
                    assert value == makespan(instance, assignment) and bound <= value <= greedy_value
                    assert len(history)==121 and history[-1]==value and np.all(np.diff(history)<=0)
                    reached = target_iteration(history,bound)
                    raw.append({'instance_id':instance_id,'size':size,'algorithm':algorithm,
                                'run':repetition+1,'seed':seed,'cmax':value,'lower_bound':bound,
                                'gap_lb_pct':100*(value-bound)/bound,'time_s':elapsed,
                                'evaluations':4840,'target_reached':reached is not None,'target_iteration':reached})
                    histories.append(np.asarray(history,dtype=np.int64))
                    assignments.append(assignment.astype(np.int16))
                description[algorithm+'_peak_kib'] = memory_peak(solver,instance,seed=10000+size_index*10000+case*100,**settings[algorithm])
            instances.append(description)
            print(instance_id, 'lower bound', bound, 'greedy',greedy_value,flush=True)
    summary = summarize(raw,instances)
    write_csv(output/'all_runs.csv',raw)
    write_csv(output/'instances.csv',instances)
    write_csv(output/'summary.csv',summary)
    write_csv(output/'processing_times.csv',data)
    np.savez_compressed(output/'histories.npz',history=np.asarray(histories))
    np.savez_compressed(output/'assignments.npz',**{f'run_{i}':a for i,a in enumerate(assignments)})
    plots(output,raw,instances,histories,assignments,problems)
    sources = {str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(ROOT.rglob('*.py'))}
    for name in ['settings.json','requirements.txt']:
        sources[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    metadata={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
              'matplotlib':matplotlib.__version__,'system':platform.platform(),'processor':platform.processor(),
              'runs_per_instance':repeats,'source_sha256':sources}
    (output/'environment.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print('Finished',len(raw),'runs.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--runs',type=int,default=20)
    parser.add_argument('--output',type=Path,default=ROOT/'results')
    args=parser.parse_args()
    if args.runs < 1:
        parser.error('--runs must be positive')
    run_experiment(args.runs,args.output.resolve())
