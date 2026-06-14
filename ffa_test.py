"""4-player FFA: 2x candidate vs 2x baseline in the same game.
Reports candidate-camp win rate (who places 1st by final ship score)."""
import sys
from multiprocessing import Pool
def _play(args):
    cand, base, seed, cand_first = args
    from kaggle_environments import make
    order = [cand, base, cand, base] if cand_first else [base, cand, base, cand]
    cand_idx = {0,2} if cand_first else {1,3}
    env = make("orbit_wars", configuration={"seed": seed})
    env.run(order)
    f = env.steps[-1]
    rewards = [f[i].reward if f[i].reward is not None else -1 for i in range(4)]
    mx = max(rewards)
    winners = [i for i in range(4) if rewards[i]==mx]
    # camp credit: did a candidate-seat win?
    cand_win = any(i in cand_idx for i in winners)
    base_win = any(i not in cand_idx for i in winners)
    if cand_win and not base_win: return 1
    if base_win and not cand_win: return -1
    return 0
def main():
    cand, base = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv)>3 else 6
    w = int(sys.argv[4]) if len(sys.argv)>4 else 4
    jobs=[]
    for i in range(n):
        sd=42+1000*i
        jobs.append((cand,base,sd,True)); jobs.append((cand,base,sd,False))
    with Pool(w) as p: res=p.map(_play, jobs)
    wn=res.count(1); ls=res.count(-1); ti=res.count(0)
    print(f"4P: {cand} camp vs {base} camp: {wn}-{ls}-{ti} -> cand camp {100*wn/max(1,wn+ls):.0f}% of decided")
if __name__=="__main__": main()
