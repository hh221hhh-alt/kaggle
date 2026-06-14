"""A/B two orbit_wars agents over swapped seeds. Usage:
    owenv/bin/python ab.py AGENT_A.py AGENT_B.py [n_seeds]
Reports A's win rate (A and B each play both sides of each seed)."""
import sys
from kaggle_environments import make

A, B = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 8
seeds = [42 + 1000 * i for i in range(N)]
w = l = t = 0
for sd in seeds:
    for a_p0 in (True, False):
        agents = [A, B] if a_p0 else [B, A]
        try:
            env = make("orbit_wars", configuration={"seed": sd})
            env.run(agents)
            f = env.steps[-1]
            ai = 0 if a_p0 else 1
            ra, rb = f[ai].reward, f[1 - ai].reward
            if ra > rb:
                w += 1; r = "WIN"
            elif ra < rb:
                l += 1; r = "LOSS"
            else:
                t += 1; r = "TIE"
            print(f"seed {sd:>5} A_p0={a_p0}: A {r:<4} turns {len(env.steps)}", flush=True)
        except Exception as e:
            print(f"seed {sd} ERR {repr(e)[:80]}", flush=True)
tot = w + l + t
print(f"\n=== A={A}  vs  B={B} ===")
print(f"A wins {w}, losses {l}, ties {t}  ->  {100*w/max(1,tot):.0f}% "
      f"(decided {100*w/max(1,w+l):.0f}%)  over {tot} games")
