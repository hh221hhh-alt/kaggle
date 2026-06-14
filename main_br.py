"""Simulation Best-Response planner (from-scratch, 2P minimal).

Not a Producer variant. Each turn we generate a few STRATEGICALLY DISTINCT
candidate move-sets, model the opponent as exp48 (run exp48 from the opponent's
perspective to predict their move), then use the perfect simulator to play
"my candidate + their predicted move" forward a few turns and keep whichever
maximises our ship margin. Because the ladder crowd IS Producer-family, picking
the best response to a Producer each turn is the whole idea.
"""
from __future__ import annotations
import os, sys, math

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import torch
import main as EXP48          # opponent model + one candidate
import sim

K_SETTLE = 9
_my_mem = EXP48.ProducerLiteMemory()
_opp_mem = EXP48.ProducerLiteMemory()
_PC = {"v": None}


def _exp48_move(obs, player, mem):
    ot = EXP48.single_obs_to_tensor(obs, player_id=player)
    if _PC["v"] is None:
        _PC["v"] = EXP48.largest_initial_player_count(ot)
    step = int(ot["step"].reshape(-1)[0].item())
    cfg = EXP48._apply_phase_config(EXP48._config_for(_PC["v"]), step)
    with torch.no_grad():
        row = EXP48.run_turn(ot, config=cfg, player_count=_PC["v"], memory=mem)
    return EXP48.sparse_action_row_to_moves(row, obs, player_id=player)


# ---- strategic candidate generators (heuristic; the sim is the judge) ----

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


def _cap_nearest(planets, me, comet, frac=1.0, neutral_only=False):
    """Each owned planet sends just-enough to crack its nearest reachable target."""
    moves = []
    tgts = _nonowned(planets, me, comet, neutral_only)
    for s in _owned(planets, me, comet):
        have = int(float(s[5]))
        if have < 4:
            continue
        cand = sorted(tgts, key=lambda t: (float(t[2]) - float(s[2])) ** 2 + (float(t[3]) - float(s[3])) ** 2)
        for t in cand:
            need = int(float(t[5])) + 2
            if need <= int(have * frac):
                moves.append([int(s[0]), _aim(s, t), need])
                break
    return moves


def _allin(planets, me, comet):
    """Every owned planet throws ~80% at its nearest enemy/neutral."""
    moves = []
    tgts = _nonowned(planets, me, comet)
    for s in _owned(planets, me, comet):
        have = int(float(s[5]))
        if have < 6 or not tgts:
            continue
        t = min(tgts, key=lambda t: (float(t[2]) - float(s[2])) ** 2 + (float(t[3]) - float(s[3])) ** 2)
        moves.append([int(s[0]), _aim(s, t), int(have * 0.8)])
    return moves


def agent(obs):
    player = int(obs["player"] if isinstance(obs, dict) else obs.player)
    planets = obs["planets"] if isinstance(obs, dict) else obs.planets
    step = int(obs.get("step", 0) if isinstance(obs, dict) else getattr(obs, "step", 0))
    if step == 0:
        _PC["v"] = None
        _my_mem.reset(); _opp_mem.reset()
    comet = set(int(c) for c in ((obs.get("comet_planet_ids") if isinstance(obs, dict)
                                  else getattr(obs, "comet_planet_ids", [])) or []))

    opp = 1 - player
    # predicted opponent move (exp48 from their perspective) + our exp48 move
    opp_move = _exp48_move(obs, opp, _opp_mem)
    c_exp48 = _exp48_move(obs, player, _my_mem)

    candidates = {
        "noop": [],
        "exp48": c_exp48,
        "capture": _cap_nearest(planets, player, comet, frac=1.0),
        "allin": _allin(planets, player, comet),
        "expand": _cap_nearest(planets, player, comet, frac=1.0, neutral_only=True),
    }

    st0 = sim.state_from_obs(obs)
    best_name, best_v, best_mv = "exp48", None, c_exp48
    for name, mv in candidates.items():
        st = {
            "planets": [list(p) for p in st0["planets"]],
            "fleets": [list(f) for f in st0["fleets"]],
            "initial_planets": st0["initial_planets"],
            "comets": [dict(c, planet_ids=list(c["planet_ids"])) for c in st0["comets"]],
            "comet_planet_ids": list(st0["comet_planet_ids"]),
            "angular_velocity": st0["angular_velocity"],
            "step": st0["step"], "next_fleet_id": st0["next_fleet_id"],
        }
        sim.step(st, {player: mv, opp: opp_move})
        for _ in range(K_SETTLE - 1):
            sim.step(st, {})
        v = sim.margin(st, player)
        if best_v is None or v > best_v:
            best_v, best_name, best_mv = v, name, mv
    return best_mv
