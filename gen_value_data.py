"""Phase 1 (value net): generate self-play games and label every position with
the eventual game outcome (+1 win / -1 loss) from that player's perspective.

Opponents are a mix of exp48 and its variants so the value net sees a broad
range of realistic positions (not just one play style). Runs games in parallel.
Usage: owenv/bin/python gen_value_data.py [n_games] [workers]
"""
import sys, math, random
from multiprocessing import Pool

N = 40
F = 7
CENTER = 50.0
# opponent pool (files in cwd). exp48 weighted heaviest.
POOL = ["main.py", "main.py", "main.py", "main_C.py", "main_A.py"]


def feats(obs, player):
    planets = obs["planets"]
    P = len(planets)
    out = [0.0] * (N * F)
    for i, p in enumerate(planets):
        if i >= N:
            break
        owner = int(p[1])
        own = 1.0 if owner == player else (-1.0 if owner >= 0 else 0.0)
        x = float(p[2]); y = float(p[3]); rad = float(p[4])
        ships = float(p[5]); prod = float(p[6]) if len(p) > 6 else 0.0
        dist = math.hypot(x - CENTER, y - CENTER)
        static = 1.0 if (dist + rad) >= 50.0 else 0.0
        b = i * F
        out[b+0] = own
        out[b+1] = ships / 100.0
        out[b+2] = prod / 10.0
        out[b+3] = x / 100.0
        out[b+4] = y / 100.0
        out[b+5] = rad / 5.0
        out[b+6] = static
    return out


def _play(args):
    seed, a, b = args
    from kaggle_environments import make
    env = make("orbit_wars", configuration={"seed": seed})
    env.run([a, b])
    final = env.steps[-1]
    r0 = final[0].reward if final[0].reward is not None else 0
    r1 = final[1].reward if final[1].reward is not None else 0
    rew = [1 if r0 > r1 else (-1 if r0 < r1 else 0),
           1 if r1 > r0 else (-1 if r1 < r0 else 0)]
    samples = []
    # subsample every other step to limit size; record both perspectives
    for t, step in enumerate(env.steps):
        if t % 2 != 0:
            continue
        for pl in (0, 1):
            obs = step[pl]["observation"]
            if not obs.get("planets"):
                continue
            lbl = rew[pl]
            if lbl == 0:
                continue
            samples.append((feats(obs, pl), float(lbl)))
    return samples


def main():
    n_games = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    rng = random.Random(0)
    jobs = []
    for i in range(n_games):
        seed = 100 + i
        a = rng.choice(POOL); b = rng.choice(POOL)
        jobs.append((seed, a, b))
    all_samples = []
    done = 0
    with Pool(workers) as pool:
        for res in pool.imap_unordered(_play, jobs):
            all_samples.extend(res); done += 1
            if done % 50 == 0:
                print(f"{done}/{n_games} games, {len(all_samples)} samples", flush=True)
    import torch
    X = torch.tensor([s[0] for s in all_samples], dtype=torch.float32).view(-1, N, F)
    Y = torch.tensor([s[1] for s in all_samples], dtype=torch.float32)
    torch.save({"X": X, "Y": Y}, "value_data.pt")
    print(f"SAVED value_data.pt  X={tuple(X.shape)}  Y={tuple(Y.shape)}  "
          f"win_frac={(Y>0).float().mean().item():.2f}")


if __name__ == "__main__":
    main()
