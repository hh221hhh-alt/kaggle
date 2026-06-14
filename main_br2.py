"""Best-Response planner v2 — FAITHFUL evaluator.

v1 failed (0-20) because a do-nothing settle mis-evaluated positions (rewarded
passivity, undervalued exp48's investments). v2 fixes the evaluator: after our
candidate move + the opponent's predicted move, we roll the position forward a
few turns with BOTH sides playing exp48, then score the margin. The simulator
is exact, so this asks the right question -- "if I play THIS now and then we
both play like the crowd, am I ahead?"  Time-guarded; falls back to exp48.
"""
from __future__ import annotations
import os, sys, math, time

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import torch
import main as EXP48
import sim

K_ROLL = 4
TIME_BUDGET = 0.80
_PC = {"v": None}
_opp_mem = EXP48.ProducerLiteMemory()
_my_mem = EXP48.ProducerLiteMemory()


def _exp48_move(obs, player, mem):
    ot = EXP48.single_obs_to_tensor(obs, player_id=player)
    if _PC["v"] is None:
        _PC["v"] = EXP48.largest_initial_player_count(ot)
    step = int(ot["step"].reshape(-1)[0].item())
    cfg = EXP48._apply_phase_config(EXP48._config_for(_PC["v"]), step)
    with torch.no_grad():
        row = EXP48.run_turn(ot, config=cfg, player_count=_PC["v"], memory=mem)
    return EXP48.sparse_action_row_to_moves(row, obs, player_id=player)


def _state_to_obs(st, player):
    return {
        "player": player,
        "planets": [list(p) for p in st["planets"]],
        "fleets": [list(f) for f in st["fleets"]],
        "initial_planets": st["initial_planets"],
        "comets": st["comets"],
        "comet_planet_ids": list(st["comet_planet_ids"]),
        "angular_velocity": st["angular_velocity"],
        "step": st["step"],
        "next_fleet_id": st["next_fleet_id"],
        "remainingOverageTime": 60.0,
    }


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


def _owned(planets, me, comet):
    return [p for p in planets if int(p[1]) == me and int(p[0]) not in comet]


def _nonowned(planets, me, comet, neutral_only=False):
    out = []
    for p in planets:
        if int(p[0]) in comet:
            continue
        o = int(p[1])
        if neutral_only:
            if o < 0:
                out.append(p)
        elif o != me:
            out.append(p)
    return out


def _aim(s, t):
    return math.atan2(float(t[3]) - float(s[3]), float(t[2]) - float(s[2]))


def _cap_nearest(planets, me, comet, neutral_only=False):
    moves = []
    tgts = _nonowned(planets, me, comet, neutral_only)
    for s in _owned(planets, me, comet):
        have = int(float(s[5]))
        if have < 4:
            continue
        for t in sorted(tgts, key=lambda t: (float(t[2]) - float(s[2])) ** 2 + (float(t[3]) - float(s[3])) ** 2):
            need = int(float(t[5])) + 2
            if need <= have:
                moves.append([int(s[0]), _aim(s, t), need]); break
    return moves


def _allin(planets, me, comet):
    moves = []
    tgts = _nonowned(planets, me, comet)
    for s in _owned(planets, me, comet):
        have = int(float(s[5]))
        if have < 6 or not tgts:
            continue
        t = min(tgts, key=lambda t: (float(t[2]) - float(s[2])) ** 2 + (float(t[3]) - float(s[3])) ** 2)
        moves.append([int(s[0]), _aim(s, t), int(have * 0.8)])
    return moves


def _rollout(st0, me, opp, my_move, opp_move, t0):
    st = _clone(st0)
    sim.step(st, {me: my_move, opp: opp_move})
    mem_a = EXP48.ProducerLiteMemory(); mem_b = EXP48.ProducerLiteMemory()
    for _ in range(K_ROLL - 1):
        if time.time() - t0 > TIME_BUDGET:
            break
        oa = _state_to_obs(st, me); ob = _state_to_obs(st, opp)
        ma = _exp48_move(oa, me, mem_a); mb = _exp48_move(ob, opp, mem_b)
        sim.step(st, {me: ma, opp: mb})
    return sim.margin(st, me)


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

    candidates = {
        "exp48": c_exp48,
        "noop": [],
        "capture": _cap_nearest(planets, player, comet),
        "allin": _allin(planets, player, comet),
    }
    st0 = sim.state_from_obs(obs)
    best_v, best_mv = None, c_exp48
    for name, mv in candidates.items():
        if time.time() - t0 > TIME_BUDGET and name != "exp48":
            continue
        v = _rollout(st0, player, opp, mv, opp_move, t0)
        if best_v is None or v > best_v:
            best_v, best_mv = v, mv
    return best_mv
