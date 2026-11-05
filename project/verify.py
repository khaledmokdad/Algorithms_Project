import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scheduling import generate_instance, greedy_assignment, lower_bound
from algorithms import solve_ga, solve_pso, solve_aco

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT/'results'
SOLVERS = {'GA':solve_ga,'PSO':solve_pso,'ACO':solve_aco}


def read(name):
    with (RESULTS/name).open(encoding='utf-8',newline='') as stream:
        return list(csv.DictReader(stream))


def scalar_value(instance, assignment):
    loads = [0]*instance.machines
    for job, machine in enumerate(assignment):
        assert 0 <= int(machine) < instance.machines
        loads[int(machine)] += int(instance.processing_times[job,int(machine)])
    return max(loads)


def verify(rerun=False):
    metadata=json.loads((RESULTS/'environment.json').read_text())
    settings=json.loads((ROOT/'settings.json').read_text())
    for name,digest in metadata['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    raw, instances, summary = read('all_runs.csv'),read('instances.csv'),read('summary.csv')
    assert len(raw)==9*3*metadata['runs_per_instance'] and len(instances)==9 and len(summary)==12
    assert len({(r['instance_id'],r['algorithm'],r['seed']) for r in raw})==len(raw)
    problems={}
    for row in instances:
        p=generate_instance(int(row['jobs']),int(row['machines']),int(row['instance_seed']),row['instance_id'])
        bound, lp=lower_bound(p)
        assert bound==int(row['lower_bound']) and abs(lp-float(row['lp_value']))<1e-6
        assert scalar_value(p,greedy_assignment(p))==int(row['greedy_cmax'])
        problems[p.name]=p
    data=read('processing_times.csv')
    assert len(data)==sum(p.jobs*p.machines for p in problems.values())
    for row in data:
        assert int(row['processing_time'])==problems[row['instance_id']].processing_times[int(row['job']),int(row['machine'])]
    histories=np.load(RESULTS/'histories.npz')['history']
    assert histories.shape==(len(raw),121)
    with np.load(RESULTS/'assignments.npz') as assignments:
        for index,row in enumerate(raw):
            problem=problems[row['instance_id']]
            assignment=assignments[f'run_{index}']
            assert len(assignment)==problem.jobs and assignment.dtype.kind in 'iu'
            value=scalar_value(problem,assignment)
            bound=int(row['lower_bound'])
            assert value==int(row['cmax']) and value>=bound
            assert abs(float(row['gap_lb_pct'])-100*(value-bound)/bound)<1e-9
            trace=histories[index]
            assert trace[-1]==value and np.all(np.diff(trace)<=0) and np.all(trace>=bound)
            reached=next((i for i,v in enumerate(trace) if v<=1.01*bound),None)
            assert row['target_reached']==str(reached is not None)
            assert row['target_iteration']==(str(reached) if reached is not None else '')
            assert int(row['evaluations'])==4840
            if rerun and int(row['run'])==1:
                _, repeated, history=SOLVERS[row['algorithm']](problem,int(row['seed']),**settings[row['algorithm']])
                assert repeated==value and np.array_equal(history,trace)
    for row in summary:
        size,algorithm=row['size'],row['algorithm']
        ins=[r for r in instances if r['size']==size]
        if algorithm=='Greedy':
            gaps=[100*(int(r['greedy_cmax'])-int(r['lower_bound']))/int(r['lower_bound']) for r in ins]
            expected={'mean_cmax':np.mean([int(r['greedy_cmax']) for r in ins]),
                      'mean_gap_lb_pct':np.mean(gaps),'within_instance_std':0,
                      'mean_time_s':np.mean([float(r['greedy_time_s']) for r in ins]),
                      'mean_peak_kib':np.mean([float(r['greedy_peak_kib']) for r in ins])}
            assert row['hits_bound']==f"{sum(int(r['greedy_cmax'])==int(r['lower_bound']) for r in ins)}/3"
        else:
            rr=[r for r in raw if r['size']==size and r['algorithm']==algorithm]
            deviations=[]
            for instance in ins:
                values=[float(r['gap_lb_pct']) for r in rr if r['instance_id']==instance['instance_id']]
                deviations.append(float(np.std(values,ddof=1)) if len(values)>1 else 0)
            expected={'mean_cmax':np.mean([int(r['cmax']) for r in rr]),
                      'mean_gap_lb_pct':np.mean([float(r['gap_lb_pct']) for r in rr]),
                      'within_instance_std':np.mean(deviations),
                      'mean_time_s':np.mean([float(r['time_s']) for r in rr]),
                      'mean_peak_kib':np.mean([float(r[algorithm+'_peak_kib']) for r in ins])}
            reached=[int(r['target_iteration']) for r in rr if r['target_reached']=='True']
            assert row['hits_bound']==f"{sum(int(r['cmax'])==int(r['lower_bound']) for r in rr)}/{len(rr)}"
            assert row['target_hits']==f'{len(reached)}/{len(rr)}'
            if reached:
                assert abs(float(row['mean_target_iteration'])-np.mean(reached))<1e-8
            else:
                assert row['mean_target_iteration']==''
        for key,value in expected.items():
            assert abs(float(row[key])-value)<1e-8,key
    print(f'Verified {len(raw)} assignments, histories, bounds and summary rows.')
    if rerun: print('The first run was reproduced for all 27 solver-instance combinations.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--rerun',action='store_true')
    verify(parser.parse_args().rerun)
