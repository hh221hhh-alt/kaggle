"""Flat Monte-Carlo planner (2P, fail-fast).

Sidesteps the position-evaluator wall: instead of scoring a position, we play
each candidate move to (near-)terminal with a fast randomised playout policy
on both sides, many times, and keep the candidate with the best WIN rate. The
"evaluator" is the actual game outcome, not a heuristic.
"""
from __future__ import annotations
import os, sys, math, time, random

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import torch
import main as EXP48
import sim

T_PLAYOUT = 90       # rollout horizon (turns)
N_ROLL = 6           # rollouts per candidate
EPS = 0.15           # playout exploration
TIME_BUDGET = 0.85
_PC = {"v": None}
_opp_mem = EXP48.ProducerLiteMemory()
_my_mem = EXP48.ProducerLiteMemory()
_rng = random.Random(12345)


def _exp48_move(obs, player, mem):
    ot = EXP48.single_obs_to_tensor(obs, player_id=player)
    if _PC["v"] is None:
        _PC["v"] = EXP48.largest_initial_player_count(ot)
    step = int(ot["step"].reshape(-1)[0].item())
    cfg = EXP48._apply_phase_config(EXP48._config_for(_PC["v"]), step)
    with torch.no_grad():
        row = EXP48.run_turn(ot, config=cfg, player_count=_PC["v"], memory=mem)
    return EXP48.sparse_action_row_to_moves(row, obs, player_id=player)


def _clone(st0):
    return {
        "planets": [list(p) for p in st0["planets"]],
        "fleets": [list(f) for f in st0["fleets"]],
        "initial_planets": st0["initial_planets"],
        "comets": [dict(c, planet_ids=list(c["planet_ids"])) for c in st0["comets"]],
        "comet_planet_ids": list(st0["comet_planet_ids"]),
        "angular_velocity": st0["angular_velocity"],
        "step": st0["step"], "next_fleet_id": st0["next_fleet_id"],
    }


def _playout_move(st, player):
    planets = st["planets"]
    owned = [p for p in planets if int(p[1]) == player and p[5] > 4]
    if not owned:
        return []
    others = [p for p in planets if int(p[1]) != player]
    if not others:
        return []
    mv = []
    for s in owned:
        if _rng.random() < EPS:
            continue
        send = int(s[5] * 0.6)
        if send < 3:
            continue
        cap = [q for q in others if q[5] < send]
        if not cap:
            continue
        t = min(cap, key=lambda q: (q[2] - s[2]) ** 2 + (q[3] - s[3]) ** 2)
        ang = math.atan2(t[3] - s[3], t[2] - s[2])
        mv.append([int(s[0]), ang, send])
    return mv


def _rollout_win(st0, me, opp, my_move, opp_move):
    st = _clone(st0)
    sim.step(st, {me: my_move, opp: opp_move})
    for _ in range(T_PLAYOUT - 1):
        a = _playout_move(st, me); b = _playout_move(st, opp)
        sim.step(st, {me: a, opp: b})
    return 1.0 if sim.margin(st, me) > 0 else 0.0


def _owned(planets, me, comet):
    return [p for p in planets if int(p[1]) == me and int(p[0]) not in comet]


def _nonowned(planets, me, comet):
    return [p for p in planets if int(p[0]) not in comet and int(p[1]) != me]


def _cap_nearest(planets, me, comet):
    mv = []
    tg = _nonowned(planets, me, comet)
    for s in _owned(planets, me, comet):
        have = int(float(s[5]))
        if have < 4:
            continue
        for t in sorted(tg, key=lambda t: (float(t[2]) - float(s[2])) ** 2 + (float(t[3]) - float(s[3])) ** 2):
            need = int(float(t[5])) + 2
            if need <= have:
                mv.append([int(s[0]), math.atan2(float(t[3]) - float(s[3]), float(t[2]) - float(s[2])), need]); break
    return mv


def agent(obs):
    t0 = time.time()
    player = int(obs["player"] if isinstance(obs, dict) else obs.player)
    planets = obs["planets"] if isinstance(obs, dict) else obs.planets
    step = int(obs.get("step", 0) if isinstance(obs, dict) else getattr(obs, "step", 0))
    if step == 0:
        _PC["v"] = None; _opp_mem.reset(); _my_mem.reset()
    comet = set(int(c) for c in ((obs.get("comet_planet_ids") if isinstance(obs, dict)
                                  else getattr(obs, "comet_planet_ids", [])) or []))
    opp = 1 - player
    opp_move = _exp48_move(obs, opp, _opp_mem)
    c_exp48 = _exp48_move(obs, player, _my_mem)
    candidates = {"exp48": c_exp48, "noop": [], "capture": _cap_nearest(planets, player, comet)}

    st0 = sim.state_from_obs(obs)
    best_w, best_mv = None, c_exp48
    for name, mv in candidates.items():
        if time.time() - t0 > TIME_BUDGET and name != "exp48":
            continue
        wins = 0.0
        for _ in range(N_ROLL):
            wins += _rollout_win(st0, player, opp, mv, opp_move)
        w = wins / N_ROLL
        if best_w is None or w > best_w:
            best_w, best_mv = w, mv
    return best_mv
