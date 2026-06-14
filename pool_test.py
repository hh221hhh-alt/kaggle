"""Fast diverse-pool win-rate test.
Usage: owenv/bin/python pool_test.py CANDIDATE.py [n_per_opp] [workers]
Plays CANDIDATE vs each pool opponent on both sides, reports per-opponent and
average win%. Disciplined: small game count, capped workers.
"""
import sys
from multiprocessing import Pool

POOL = ["main_old.py", "producer.py", "main_new.py"]


def _play(args):
    cand, opp, seed, cand_p0 = args
    from kaggle_environments import make
    agents = [cand, opp] if cand_p0 else [opp, cand]
    env = make("orbit_wars", configuration={"seed": seed})
    env.run(agents)
    f = env.steps[-1]
    ci = 0 if cand_p0 else 1
    rc, ro = f[ci].reward, f[1 - ci].reward
    return (opp, 1 if rc > ro else (-1 if rc < ro else 0))


def main():
    cand = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    pool = [o for o in POOL if o != cand]
    jobs = []
    for opp in pool:
        for i in range(n):
            sd = 42 + 1000 * i
            jobs.append((cand, opp, sd, True))
            jobs.append((cand, opp, sd, False))
    with Pool(w) as p:
        res = p.map(_play, jobs)
    print(f"=== {cand} vs pool ({n*2} games/opp) ===")
    tot_w = tot = 0
    for opp in pool:
        r = [x[1] for x in res if x[0] == opp]
        wn = r.count(1); ls = r.count(-1); ti = r.count(0)
        tot_w += wn; tot += len(r)
        print(f"  vs {opp:<14} {wn}-{ls}-{ti}  ({100*wn/len(r):.0f}%)")
    print(f"  OVERALL win% = {100*tot_w/tot:.0f}%  ({tot_w}/{tot})")


if __name__ == "__main__":
    main()
