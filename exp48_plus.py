"""exp48 (Producer) + a thin comet-evacuation overlay.

Runs exp48's planner unchanged, then -- for any owned comet that is about to
leave the board with ships still on it that the planner did NOT launch -- adds a
move sending those leftover ships to the nearest owned non-comet planet, so they
aren't lost when the comet expires. Everything else is identical to exp48.
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

import exp48  # the Producer planner (its own runtime/state)

COMET_EVAC_REMAINING = 6   # evac when the comet has <= this many turns of life left
COMET_EVAC_MIN_SHIPS = 5   # only bother evacuating at least this many leftover ships


def _comet_remaining(obs):
    """planet_id -> turns of life left, for active comets."""
    rem = {}
    for grp in (obs.get("comets", []) or []):
        try:
            idx = int(grp.get("path_index", 0))
            pids = grp.get("planet_ids", []) or []
            paths = grp.get("paths", []) or []
            for i, pid in enumerate(pids):
                if i < len(paths):
                    rem[int(pid)] = max(0, len(paths[i]) - idx)
        except (AttributeError, TypeError, IndexError):
            continue
    return rem


def agent(obs):
    moves = exp48.agent(obs)

    try:
        player = obs.get("player", 0) if isinstance(obs, dict) else obs.player
        player = int(player)
        planets = obs.get("planets", []) if isinstance(obs, dict) else obs.planets
        rem = _comet_remaining(obs)
        if not rem:
            return moves

        by_id = {int(p[0]): p for p in planets if len(p) >= 7 and int(p[0]) >= 0}
        comet_ids = set(rem.keys())
        # ships already launched from each planet this turn (by the planner)
        launched = {}
        for m in moves:
            if isinstance(m, (list, tuple)) and len(m) >= 3:
                launched[int(m[0])] = launched.get(int(m[0]), 0) + int(round(float(m[2])))

        # owned, non-comet planets we can evac TO
        dests = [p for pid, p in by_id.items()
                 if int(p[1]) == player and pid not in comet_ids]
        if not dests:
            return moves

        for cid, life in rem.items():
            if life > COMET_EVAC_REMAINING:
                continue
            c = by_id.get(cid)
            if c is None or int(c[1]) != player:
                continue  # not ours
            cx, cy, cships = float(c[2]), float(c[3]), float(c[5])
            leftover = int(cships) - launched.get(cid, 0)
            if leftover < COMET_EVAC_MIN_SHIPS:
                continue
            dst = min(dests, key=lambda p: math.hypot(cx - float(p[2]), cy - float(p[3])))
            angle = math.atan2(float(dst[3]) - cy, float(dst[2]) - cx)
            moves.append([cid, angle, leftover])
    except Exception:
        return moves
    return moves
