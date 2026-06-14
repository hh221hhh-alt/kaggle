"""exp48 + sim-verified aggression (serious lookahead, training-free).

Spine = exp48's move (defence/coherence untouched). Then we GREEDILY add extra
launches from idle surplus planets -- but only commit a launch when a forward
simulation, in which BOTH sides play a fast *reactive* playout policy (grab
weakened/under-defended planets), confirms it improves our material margin K
turns out. The reactive opponent is the key fix: today's blind aggression lost
because it ignored the opponent's punishment; here the sim sees it.
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
import main as B
import sim

K_ROLLOUT   = 14
TIME_BUDGET = 0.80
RESERVE_FRAC = 0.35      # keep this fraction of a planet home (defence)
MIN_SURPLUS  = 12        # only consider idle planets with at least this surplus
EPS          = 1.0       # require this much margin gain to commit an extra launch
MAX_EXTRA    = 6         # cap added launches per turn
SPEED_MAX = 6.0
_LOG1000 = math.log(1000.0)

_mem = B.ProducerLiteMemory()
_PC = {"v": None}


def _speed(n):
    n = max(1.0, float(n))
    return min(SPEED_MAX, 1.0 + (SPEED_MAX - 1.0) * (math.log(n) / _LOG1000) ** 1.5)


def _clone(st):
    return {
        "planets": [list(p) for p in st["planets"]],
        "fleets": [list(f) for f in st["fleets"]],
        "initial_planets": st["initial_planets"],          # read-only
        "comets": [dict(c, planet_ids=list(c["planet_ids"])) for c in st["comets"]],
        "comet_planet_ids": list(st["comet_planet_ids"]),
        "angular_velocity": st["angular_velocity"],
        "step": st["step"],
        "next_fleet_id": st["next_fleet_id"],
    }


def _alive_players(st, n):
    s = set()
    for p in st["planets"]:
        if p[1] != -1:
            s.add(p[1])
    for f in st["fleets"]:
        s.add(f[1])
    return [p for p in range(n) if p in s]


def _playout_move(st, player):
    """Fast reactive policy: each surplus planet grabs its nearest capturable
    non-owned planet. Crude but models the opponent punishing weak planets."""
    planets = st["planets"]
    owned = [p for p in planets if p[1] == player and p[5] > 4]
    if not owned:
        return []
    others = [p for p in planets if p[1] != player]
    if not others:
        return []
    moves = []
    for p in owned:
        send = int(p[5] * 0.7)
        if send < 3:
            continue
        best = None; bd = 1e18
        for q in others:
            if q[5] < send:
                d = (q[2] - p[2]) ** 2 + (q[3] - p[3]) ** 2
                if d < bd:
                    bd = d; best = q
        if best is not None:
            ang = math.atan2(best[3] - p[3], best[2] - p[2])
            moves.append([p[0], ang, send])
    return moves


def _rollout(st0, player, root_moves, n):
    st = _clone(st0)
    alive = _alive_players(st, n)
    acts = {player: root_moves}
    for o in alive:
        if o != player:
            acts[o] = _playout_move(st, o)
    sim.step(st, acts)
    for _ in range(K_ROLLOUT - 1):
        al = _alive_players(st, n)
        sim.step(st, {pl: _playout_move(st, pl) for pl in al})
    return sim.margin(st, player)


def _base_move(obs, player):
    ot = B.single_obs_to_tensor(obs, player_id=player)
    if bool((ot["step"] == 0).all()):
        _PC["v"] = None; _mem.reset()
    if _PC["v"] is None:
        _PC["v"] = B.largest_initial_player_count(ot)
    step = int(ot["step"].reshape(-1)[0].item())
    cfg = B._apply_phase_config(B._config_for(_PC["v"]), step)
    row = B.run_turn(ot, config=cfg, player_count=_PC["v"], memory=_mem)
    return B.sparse_action_row_to_moves(row, obs, player_id=player)


def _extra_candidates(obs, player, base_moves):
    """One candidate launch per idle surplus planet -> nearest capturable target."""
    planets = obs["planets"] if isinstance(obs, dict) else obs.planets
    by_id = {int(p[0]): p for p in planets if int(p[0]) >= 0}
    launched = {}
    for m in base_moves:
        launched[int(m[0])] = launched.get(int(m[0]), 0) + int(round(float(m[2])))
    targets = [p for p in planets if int(p[1]) != player and float(p[5]) >= 0]
    cands = []
    for pid, p in by_id.items():
        if int(p[1]) != player:
            continue
        surplus = int(float(p[5])) - launched.get(pid, 0)
        usable = int(surplus * (1.0 - RESERVE_FRAC))
        if surplus < MIN_SURPLUS or usable < 3:
            continue
        best = None; bd = 1e18
        for q in targets:
            if float(q[5]) < usable:
                d = (float(q[2]) - float(p[2])) ** 2 + (float(q[3]) - float(p[3])) ** 2
                if d < bd:
                    bd = d; best = q
        if best is not None:
            ang = math.atan2(float(best[3]) - float(p[3]), float(best[2]) - float(p[2]))
            cands.append([pid, ang, usable])
    return cands


def agent(obs):
    t0 = time.time()
    player = int(obs["player"] if isinstance(obs, dict) else obs.player)
    with torch.no_grad():
        move = _base_move(obs, player)
    n = _PC["v"] or 2
    st0 = sim.state_from_obs(obs)

    cur = list(move)
    cur_score = _rollout(st0, player, cur, n)
    extras = _extra_candidates(obs, player, cur)
    added = 0
    while extras and added < MAX_EXTRA and (time.time() - t0) < TIME_BUDGET:
        best_i = -1; best_v = cur_score
        for i, L in enumerate(extras):
            v = _rollout(st0, player, cur + [L], n)
            if v > best_v + EPS:
                best_v = v; best_i = i
        if best_i < 0:
            break
        cur.append(extras.pop(best_i)); cur_score = best_v; added += 1
    return cur
