"""exp48 (Producer) + coordinated multi-source strikes on defended STATIC planets.

The Producer attacks each target from a single source, so an enemy/neutral
planet defended by more than any one of our planets' spare ships is left alone
(it only cracks it slowly via regroup-and-accumulate). This overlay runs exp48
unchanged, then -- using only the ships exp48 did NOT launch -- combines the
nearest planets to crack such defended STATIC planets in one turn (sequential-
combat verified). Straight-line aim, so limited to static (outer) targets where
that is exact.
"""
from __future__ import annotations

import math
import os
import sys

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import exp48

CENTER = 50.0
ROT_LIMIT = 50.0
MAX_SPEED = 6.0
_LOG1000 = math.log(1000.0)
COORD_MAX_SOURCES = 4
COORD_MIN_PER_SRC = 5
COORD_OVERKILL = 2          # extra ships over the projected garrison
MARGIN_TURNS = 1            # production turns of slack added to growth


def _speed(ships):
    s = max(1.0, float(ships))
    r = min(1.0, math.log(s) / _LOG1000)
    return 1.0 + (MAX_SPEED - 1.0) * (r ** 1.5)


def _is_static(p):
    d = math.hypot(float(p[2]) - CENTER, float(p[3]) - CENTER)
    return d + float(p[4]) >= ROT_LIMIT


def _seq_capture_ok(garrison, prod, contribs):
    """contribs = [(eta, ships)] sequential combat with per-turn growth."""
    g = float(garrison)
    prev = 0
    for eta, sh in sorted(contribs):
        g += max(0.0, float(prod)) * (eta - prev)
        prev = eta
        if sh > g:
            return True
        g -= sh
    return False


def agent(obs):
    moves = exp48.agent(obs)
    try:
        player = int(obs.get("player", 0) if isinstance(obs, dict) else obs.player)
        planets = obs.get("planets", []) if isinstance(obs, dict) else obs.planets
        comet_ids = set(int(c) for c in (obs.get("comet_planet_ids", []) or []))
        by_id = {int(p[0]): p for p in planets if len(p) >= 7 and int(p[0]) >= 0}

        launched = {}
        for m in moves:
            if isinstance(m, (list, tuple)) and len(m) >= 3:
                launched[int(m[0])] = launched.get(int(m[0]), 0) + int(round(float(m[2])))
        # leftover ships per owned non-comet planet
        leftover = {}
        for pid, p in by_id.items():
            if int(p[1]) == player and pid not in comet_ids:
                lo = int(float(p[5])) - launched.get(pid, 0)
                if lo >= COORD_MIN_PER_SRC:
                    leftover[pid] = lo
        if not leftover:
            return moves

        # defended STATIC enemy/neutral targets, biggest garrison first
        targets = [p for pid, p in by_id.items()
                   if int(p[1]) != player and pid not in comet_ids and _is_static(p)
                   and float(p[5]) >= 1]
        targets.sort(key=lambda p: -float(p[5]))
        max_single = max(leftover.values())

        used = set()
        for tgt in targets:
            tid = int(tgt[0]); tx, ty = float(tgt[2]), float(tgt[3]); tg = float(tgt[5])
            tprod = float(tgt[6])
            need_now = tg + 1
            if need_now <= max_single:
                continue  # the Producer can already take this with one source
            srcs = sorted((pid for pid in leftover if pid not in used),
                          key=lambda pid: math.hypot(tx - float(by_id[pid][2]),
                                                     ty - float(by_id[pid][3])))
            contribs = []   # (pid, eta, ships, angle)
            for pid in srcs:
                sp = by_id[pid]
                d = math.hypot(tx - float(sp[2]), ty - float(sp[3]))
                sh = leftover[pid]
                eta = max(1, math.ceil(d / _speed(sh)))
                ang = math.atan2(ty - float(sp[3]), tx - float(sp[2]))
                contribs.append((pid, eta, sh, ang))
                # growth-aware sequential capture check (+overkill)
                if _seq_capture_ok(tg + COORD_OVERKILL + tprod * MARGIN_TURNS, tprod,
                                   [(e, s) for _p, e, s, _a in contribs]):
                    for cpid, ceta, csh, cang in contribs:
                        moves.append([cpid, cang, csh])
                        used.add(cpid)
                    break
                if len(contribs) >= COORD_MAX_SOURCES:
                    break
    except Exception:
        return moves
    return moves
