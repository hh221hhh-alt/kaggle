"""Build the v2 imitation dataset from top-8 winners' replays.

Per turn (winner's perspective) one sample:
  X[40, F]   planet features (F=13, see feats())
  L[40]      did this planet launch this turn (clean-labeled launches only)
  T[40, 40]  ships sent source->target (intercept-geometry labeling, err<0.12)
  S[40]      fraction of source garrison launched this turn (0..1)

Covers 2P and 4P; global context (step, player count, standing) is broadcast
into per-planet features. Parallel over games.
Usage: owenv/bin/python make_dataset2.py [workers]
"""
import json, glob, math, os, sys
from multiprocessing import Pool

import torch

sys.path.insert(0, "/Users/haruka/kaggle")
from orbit_lite.adapter import single_obs_to_tensor
from orbit_lite.obs import parse_obs
from orbit_lite.movement import MovementConfig
from orbit_lite.movement_step import ensure_planet_movement
from orbit_lite.intercept_aim import intercept_angle
from fleet_resolve import incoming

N = 40
F = 17
CENTER = 50.0
ERRTOL = 0.12


def feats(obs_dict, player):
    planets = obs_dict["planets"]
    fleets = obs_dict.get("fleets", []) or []
    P = len(planets)
    x = torch.zeros(N, F)
    # global context
    step = float(obs_dict.get("step", 0)) / 500.0
    owners = {int(p[1]) for p in planets if int(p[1]) >= 0}
    npl = max(2, len(owners | {int(f[1]) for f in fleets}))
    tot = {}
    for p in planets:
        o = int(p[1])
        if o >= 0:
            tot[o] = tot.get(o, 0.0) + float(p[5])
    for f in fleets:
        tot[int(f[1])] = tot.get(int(f[1]), 0.0) + float(f[6])
    me = tot.get(player, 0.0)
    opp = max([v for k, v in tot.items() if k != player], default=0.0)
    standing = (me - opp) / max(1.0, me + opp)

    mine_xy = [(float(p[2]), float(p[3])) for p in planets if int(p[1]) == player]
    enemy_xy = [(float(p[2]), float(p[3])) for p in planets if int(p[1]) >= 0 and int(p[1]) != player]

    inc = incoming(obs_dict, horizon=30)
    for i, p in enumerate(planets):
        if i >= N:
            break
        o = int(p[1])
        px, py = float(p[2]), float(p[3])
        rad = float(p[4]); ships = float(p[5])
        prod = float(p[6]) if len(p) > 6 else 0.0
        dist_c = math.hypot(px - CENTER, py - CENTER)
        d = inc.get(p[0], None)
        if d is not None:
            in_f = d["by_owner"].get(player, 0.0)
            in_e = sum(v for k_, v in d["by_owner"].items() if k_ != player)
            eta_f = d["eta"].get(player, 30)
            eta_e = min((v for k_, v in d["eta"].items() if k_ != player), default=30)
        else:
            in_f = in_e = 0.0; eta_f = eta_e = 30
        d_en = min((math.hypot(ex - px, ey - py) for ex, ey in enemy_xy), default=100.0)
        d_my = min((math.hypot(mx - px, my_ - py) for mx, my_ in mine_xy
                    if (mx, my_) != (px, py)), default=100.0)
        x[i, 0] = 1.0 if o == player else (-1.0 if o >= 0 else 0.0)
        x[i, 1] = ships / 100.0
        x[i, 2] = prod / 10.0
        x[i, 3] = px / 100.0
        x[i, 4] = py / 100.0
        x[i, 5] = rad / 5.0
        x[i, 6] = 1.0 if (dist_c + rad) >= 50.0 else 0.0
        x[i, 7] = in_f / 100.0
        x[i, 8] = in_e / 100.0
        x[i, 9] = d_en / 100.0
        x[i, 10] = d_my / 100.0
        x[i, 11] = step
        x[i, 12] = standing if o == player else (npl - 2) / 2.0
        x[i, 13] = eta_e / 30.0
        x[i, 14] = eta_f / 30.0
        sign = 1.0 if o == player else (-1.0 if o >= 0 else 0.0)
        x[i, 15] = (ships * sign + in_f - in_e) / 100.0
        x[i, 16] = (in_e - ships) / 100.0 if o == player else 0.0
    return x


def label_game(args):
    fp, agent_index, n_agents = args
    out = []
    try:
        rep = json.load(open(fp))
    except Exception:
        return out
    steps = rep["steps"]
    mv_cache = None
    # CRITICAL: the action recorded at steps[t+1] was decided on the obs at
    # steps[t] (kaggle convention). Pair obs[t] with action[t+1].
    for t in range(len(steps) - 1):
        s = steps[t]
        try:
            a = steps[t + 1][agent_index].get("action") or []
            od = s[agent_index]["observation"]
            pid = int(od["player"])
            if not od.get("planets"):
                continue
            X = feats(od, pid)
            L = torch.zeros(N)
            T = torch.zeros(N, N)
            S = torch.zeros(N)
            if a:
                ot = single_obs_to_tensor(od, player_id=pid)
                obs = parse_obs(ot)
                P = obs.P
                if P >= 2:
                    mv = ensure_planet_movement(
                        obs_tensors=ot,
                        expected_cfg=MovementConfig(movement_horizon=18, drift_epsilon=1e-3,
                                                    track_fleets=True, player_count=n_agents,
                                                    max_tracked_fleets=128),
                        cached_movement=None)
                    pids = ot["planets"][..., 0].long().tolist()
                    id2slot = {p: i for i, p in enumerate(pids)}
                    tgt = torch.arange(P)
                    garrison = {i: float(od["planets"][i][5])
                                for i in range(min(len(od["planets"]), N))}
                    for (src_id, ang, ships) in a:
                        si = id2slot.get(int(src_id))
                        if si is None or si >= N:
                            continue
                        sizes = torch.full((1, P), float(ships))
                        aim = intercept_angle(mv, torch.tensor([[si]]), tgt.view(1, P), sizes,
                                              active=torch.ones(1, P, dtype=torch.bool))
                        d = torch.remainder(aim["angle"].view(P) - float(ang) + math.pi,
                                            2 * math.pi) - math.pi
                        d = d.abs(); d[~aim["viable"].view(P)] = 99
                        best = int(d.argmin())
                        if float(d[best]) < ERRTOL and best < N:
                            L[si] = 1.0
                            T[si, best] += float(ships)
                            g = garrison.get(si, 0.0)
                            if g > 0:
                                S[si] = min(1.0, S[si] + float(ships) / g)
            out.append((X, L, T, S))
        except Exception:
            continue
    return out


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    team_filter = sys.argv[2] if len(sys.argv) > 2 else None
    out_name = sys.argv[3] if len(sys.argv) > 3 else "top8_dataset.pt"
    index = json.load(open("replays/top8/index.json"))
    jobs = []
    for m in index:
        if not m["won"]:
            continue
        if team_filter and team_filter not in m["team"]:
            continue
        fp = f"replays/top8/{m['episode_id']}.json"
        if os.path.exists(fp):
            jobs.append((fp, m["agent_index"], m["n_agents"]))
    print(f"games to label: {len(jobs)}", flush=True)
    Xs, Ls, Ts, Ss = [], [], [], []
    done = 0
    with Pool(workers) as pool:
        for res in pool.imap_unordered(label_game, jobs):
            for (X, L, T, S) in res:
                Xs.append(X); Ls.append(L); Ts.append(T); Ss.append(S)
            done += 1
            if done % 25 == 0:
                print(f"{done}/{len(jobs)} games, {len(Xs)} samples", flush=True)
    d = {"X": torch.stack(Xs), "L": torch.stack(Ls), "T": torch.stack(Ts), "S": torch.stack(Ss)}
    torch.save(d, out_name)
    print(f"SAVED {out_name} X={tuple(d['X'].shape)}", flush=True)


if __name__ == "__main__":
    main()
