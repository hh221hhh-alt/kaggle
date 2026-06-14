"""Overnight NES fine-tune of the clone, directly maximising performance vs
exp48 (the ladder crowd). BC weights as init; perturb ONLY the head params
(launch/q/k/size/dist_w + th) — the trunk's representation stays fixed.

Fitness per candidate: G games vs main.py (seeds x both sides);
score = wins + 0.5 * mean final ship-share margin (smooth signal).
Rank-based NES update; champion re-evaluated and checkpointed every gen.
Usage: owenv/bin/python es_tune.py [hours]
"""
import io, json, sys, time, random
from multiprocessing import Pool

import torch

sys.path.insert(0, "/Users/haruka/kaggle")
from train_tf import TFClone

HEAD_KEYS = ("launch.", "size.", "dist_w")   # ~195 behavioural params (target head frozen)
SIGMA = 0.05
LR = 0.1
NPAIR = 8              # 16 perturbed candidates per generation
GAMES = 8              # per candidate (4 seeds x both sides)
WORKERS = 5


def head_vector(sd):
    return torch.cat([sd[k].flatten() for k in sd if k.startswith(HEAD_KEYS)])


def set_heads(sd, vec):
    sd = {k: v.clone() for k, v in sd.items()}
    i = 0
    for k in sd:
        if k.startswith(HEAD_KEYS):
            n = sd[k].numel()
            sd[k] = vec[i:i + n].view_as(sd[k])
            i += n
    return sd


def _play(args):
    blob, th, seed, cand_first = args
    import es_agent
    from kaggle_environments import make
    sd = torch.load(io.BytesIO(blob), weights_only=True)
    cand = es_agent.make_agent(sd, th)
    agents = [cand, "main.py"] if cand_first else ["main.py", cand]
    ci = 0 if cand_first else 1
    env = make("orbit_wars", configuration={"seed": seed})
    env.run(agents)
    f = env.steps[-1]
    rc = f[ci].reward if f[ci].reward is not None else -1
    ro = f[1 - ci].reward if f[1 - ci].reward is not None else -1
    # final ship share margin (smooth)
    obs = f[ci]["observation"]
    tot = {}
    for p in obs["planets"]:
        if int(p[1]) >= 0:
            tot[int(p[1])] = tot.get(int(p[1]), 0.0) + float(p[5])
    for fl in obs.get("fleets", []) or []:
        tot[int(fl[1])] = tot.get(int(fl[1]), 0.0) + float(fl[6])
    me = tot.get(int(obs["player"]), 0.0)
    opp = max((v for k, v in tot.items() if k != int(obs["player"])), default=0.0)
    share = (me - opp) / max(1.0, me + opp)
    win = 1.0 if rc > ro else 0.0
    return win + 0.5 * share


def evaluate(pool, sd, th, seeds):
    blob_io = io.BytesIO(); torch.save(sd, blob_io); blob = blob_io.getvalue()
    jobs = []
    for s in seeds:
        jobs.append((blob, th, s, True))
        jobs.append((blob, th, s, False))
    res = pool.map(_play, jobs)
    return sum(res) / len(res)


def main():
    hours = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
    ck = torch.load("orbit_tf_top8.pth", map_location="cpu", weights_only=True)
    base_sd = ck["state"]; th = float(ck["th"])
    theta = head_vector(base_sd)
    print(f"ES: tuning {theta.numel()} head params, th={th}", flush=True)
    g = torch.Generator().manual_seed(0)
    t0 = time.time()
    pool = Pool(WORKERS)
    best_score = evaluate(pool, base_sd, th, [101, 202, 303])
    print(f"gen0 champion score {best_score:.3f}", flush=True)
    torch.save({"state": base_sd, "th": th}, "orbit_es_best.pth")
    gen = 0
    CONFIRM = [11, 22, 33, 44, 55, 66]   # fixed seeds for head-to-head confirmation
    while time.time() - t0 < hours * 3600:
        gen += 1
        # sample candidates around the current champion
        eps = [SIGMA * torch.randn(theta.numel(), generator=g) for _ in range(2 * NPAIR)]
        cands = [theta + e for e in eps]
        seeds = [random.randint(0, 10 ** 6) for _ in range(GAMES // 2)]
        scores = [evaluate(pool, set_heads(base_sd, c), th, seeds) for c in cands]
        scores_t = torch.tensor(scores)
        bi = int(scores_t.argmax())
        # ELITIST: only adopt if the best candidate confirms BETTER than the champion
        # on the SAME fresh confirmation seeds (robust to fitness noise)
        cand_c = evaluate(pool, set_heads(base_sd, cands[bi]), th, CONFIRM)
        champ_c = evaluate(pool, set_heads(base_sd, theta), th, CONFIRM)
        mark = ""
        if cand_c > champ_c + 0.02:
            theta = cands[bi]
            best_score = cand_c
            torch.save({"state": set_heads(base_sd, theta), "th": th}, "orbit_es_best.pth")
            mark = "  <-- ADOPTED new champion"
        print(f"gen{gen}: pop_max {scores_t.max():.3f} cand_confirm {cand_c:.3f} "
              f"champ_confirm {champ_c:.3f}{mark}", flush=True)
    pool.close()
    print(f"DONE {gen} generations, best {best_score:.3f}", flush=True)


if __name__ == "__main__":
    main()
