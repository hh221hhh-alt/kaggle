"""4-player FFA agent: I'M STRONGER engine + HARD leader-hammer.

Data (Jake's 34 FFA games): 71% of attacks target the current leader, and the
top bot stays the ship-leader only 12% of the time. I'M STRONGER implements
leader-targeting only as a weak additive score bonus (tuning it was neutral).
Here we implement it HARD: after the strong base move, when we are NOT the
leader, take ONLY post-planner surplus (keeping a defensive reserve) and
combine nearby planets to crack the LEADER's reachable planets -- firing only
when sequential combat (growth-aware) guarantees capture. No wasted dribbles,
no touching the base allocation.
"""
from __future__ import annotations
import os, sys, math

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import cand_stronger as BASE   # the strong engine (I'M STRONGER)

CENTER = 50.0
ROT_LIMIT = 50.0
MAX_SPEED = 6.0
_LOG1000 = math.log(1000.0)
RESERVE_FRAC = 0.40     # keep this fraction of a source planet home (defence)
MIN_SURPLUS = 14        # only planets with at least this leftover join a hammer
COORD_MAX_SRC = 5
OVERKILL = 3
MARGIN_TURNS = 1
MAX_HAMMERS = 2         # combined strikes on the leader per turn


def _speed(n):
    n = max(1.0, float(n))
    r = min(1.0, math.log(n) / _LOG1000)
    return 1.0 + (MAX_SPEED - 1.0) * (r ** 1.5)


def _is_static(p):
    return math.hypot(float(p[2]) - CENTER, float(p[3]) - CENTER) + float(p[4]) >= ROT_LIMIT


def _seq_ok(garrison, prod, contribs):
    g = float(garrison); prev = 0
    for eta, sh in sorted(contribs):
        g += max(0.0, float(prod)) * (eta - prev); prev = eta
        if sh > g:
            return True
        g -= sh
    return False


def _ships_by_player(planets, fleets, player):
    tot = {}
    for p in planets:
        o = int(p[1])
        if o >= 0:
            tot[o] = tot.get(o, 0) + float(p[5])
    for f in (fleets or []):
        tot[int(f[1])] = tot.get(int(f[1]), 0) + float(f[6])
    return tot


def agent(obs):
    moves = BASE.agent(obs)
    try:
        player = int(obs["player"] if isinstance(obs, dict) else obs.player)
        planets = obs["planets"] if isinstance(obs, dict) else obs.planets
        fleets = (obs.get("fleets") if isinstance(obs, dict) else getattr(obs, "fleets", [])) or []
        comet_ids = set(int(c) for c in ((obs.get("comet_planet_ids") if isinstance(obs, dict)
                                          else getattr(obs, "comet_planet_ids", [])) or []))
        by_id = {int(p[0]): p for p in planets if len(p) >= 7 and int(p[0]) >= 0}

        tot = _ships_by_player(planets, fleets, player)
        nplayers = len([k for k in tot.keys()])
        if nplayers < 3:
            return moves  # only meddle in multiplayer
        my = tot.get(player, 0.0)
        opps = {k: v for k, v in tot.items() if k != player}
        if not opps:
            return moves
        leader = max(opps, key=lambda k: opps[k])
        # if WE are the overall leader, stay low-profile: do nothing extra
        if my >= max(opps.values()):
            return moves

        launched = {}
        for m in moves:
            if isinstance(m, (list, tuple)) and len(m) >= 3:
                launched[int(m[0])] = launched.get(int(m[0]), 0) + int(round(float(m[2])))
        avail = {}
        for pid, p in by_id.items():
            if int(p[1]) == player and pid not in comet_ids:
                lo = int(float(p[5])) - launched.get(pid, 0)
                use = int(lo * (1.0 - RESERVE_FRAC))
                if lo >= MIN_SURPLUS and use >= 1:
                    avail[pid] = use
        if not avail:
            return moves

        # leader's STATIC planets, weakest first (easiest to crack)
        targets = [p for pid, p in by_id.items()
                   if int(p[1]) == leader and pid not in comet_ids and _is_static(p)]
        targets.sort(key=lambda p: float(p[5]))
        used = set(); hammers = 0
        for tgt in targets:
            if hammers >= MAX_HAMMERS:
                break
            tx, ty = float(tgt[2]), float(tgt[3]); tg = float(tgt[5]); tprod = float(tgt[6])
            srcs = sorted((pid for pid in avail if pid not in used),
                          key=lambda pid: math.hypot(tx - float(by_id[pid][2]), ty - float(by_id[pid][3])))
            contribs = []
            for pid in srcs:
                sp = by_id[pid]; d = math.hypot(tx - float(sp[2]), ty - float(sp[3]))
                sh = avail[pid]; eta = max(1, math.ceil(d / _speed(sh)))
                ang = math.atan2(ty - float(sp[3]), tx - float(sp[2]))
                contribs.append((pid, eta, sh, ang))
                if _seq_ok(tg + OVERKILL + tprod * MARGIN_TURNS, tprod,
                           [(e, s) for _p, e, s, _a in contribs]):
                    for cpid, ceta, csh, cang in contribs:
                        moves.append([cpid, cang, csh]); used.add(cpid)
                    hammers += 1
                    break
                if len(contribs) >= COORD_MAX_SRC:
                    break
    except Exception:
        return moves
    return moves
