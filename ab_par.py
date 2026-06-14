"""Parallel A/B of two orbit_wars agents. Usage:
    owenv/bin/python ab_par.py A.py B.py [n_seeds] [workers]
Plays A and B on both sides of each seed, in parallel. Reports A's win rate
with a rough 95% CI so we can tell a real edge from noise.
"""
import sys
from multiprocessing import Pool


def _play(args):
    a, b, seed, a_p0 = args
    from kaggle_environments import make
    agents = [a, b] if a_p0 else [b, a]
    env = make("orbit_wars", configuration={"seed": seed})
    env.run(agents)
    f = env.steps[-1]
    ai = 0 if a_p0 else 1
    ra, rb = f[ai].reward, f[1 - ai].reward
    return 1 if ra > rb else (-1 if ra < rb else 0)


def main():
    A, B = sys.argv[1], sys.argv[2]
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    W = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    jobs = []
    for i in range(N):
        sd = 42 + 1000 * i
        jobs.append((A, B, sd, True))
        jobs.append((A, B, sd, False))
    with Pool(W) as pool:
        res = pool.map(_play, jobs)
    w = res.count(1); l = res.count(-1); t = res.count(0)
    tot = len(res)
    wr = w / max(1, tot)
    se = (wr * (1 - wr) / max(1, tot)) ** 0.5
    print(f"A={A} vs B={B}: {tot} games")
    print(f"A wins {w}, losses {l}, ties {t} -> {100*wr:.0f}% "
          f"(95% CI +-{196*se:.0f}%)  decided {100*w/max(1,w+l):.0f}%")


if __name__ == "__main__":
    main()
