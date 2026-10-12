"""Bounded parallel comparative solves; thread budgets sum to host CPU count."""
import argparse, concurrent.futures, itertools, json, os, subprocess
from pathlib import Path

def run(job):
    rack, clock, ratio, threads = job
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS=str(threads), OMP_NUM_THREADS=str(threads))
    log = Path(rack) / f'campaign-{clock:g}-{ratio:g}.log'
    command = [str(Path('venv/bin/python').absolute()), 'solve.py', rack, '--clock', str(clock), '--rz', str(ratio)]
    with log.open('w') as out:
        try:
            result = subprocess.run(command, env=env, stdout=out, stderr=subprocess.STDOUT, timeout=240)
            return dict(rack=rack, clock=clock, ratio=ratio, exit_code=result.returncode, log=str(log))
        except subprocess.TimeoutExpired:
            return dict(rack=rack, clock=clock, ratio=ratio, exit_code='timeout', log=str(log))

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--racks', nargs='+', default=['HX05C', 'HX05B', 'HX05A'])
    p.add_argument('--clocks', nargs='+', type=float, default=list(range(0, 180, 15)))
    p.add_argument('--ratios', nargs='+', type=float, default=[.35, .65, .9])
    p.add_argument('--workers', type=int, default=8)
    p.add_argument('--threads', type=int, default=5)
    a = p.parse_args()
    jobs = [(*q, a.threads) for q in itertools.product(a.racks, a.clocks, a.ratios)]
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:
        for result in pool.map(run, jobs):
            results.append(result)
            print(json.dumps(result), flush=True)
    Path('campaign-status.json').write_text(json.dumps(results, indent=2) + '\n')
    raise SystemExit(any(q['exit_code'] != 0 for q in results))
