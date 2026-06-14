"""Faithful, dependency-free forward simulator for orbit_wars.

Replicates kaggle_environments orbit_wars `interpreter` step EXACTLY for the
deterministic parts (production, planet rotation, fleet movement w/ swept-pair
collision, sun/bounds, combat). The only thing it does NOT model is future
comet *spawns* (seed is hidden) -- existing comets still move and expire.

State is a plain dict of lists so it is cheap to deep-copy for lookahead.
"""
import math

BOARD_SIZE = 100.0
CENTER = BOARD_SIZE / 2.0
SUN_RADIUS = 10.0
ROTATION_RADIUS_LIMIT = 50.0


def _distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def _pt_seg(p, v, w):
    l2 = (v[0] - w[0]) ** 2 + (v[1] - w[1]) ** 2
    if l2 == 0.0:
        return _distance(p, v)
    t = max(0, min(1, ((p[0]-v[0])*(w[0]-v[0]) + (p[1]-v[1])*(w[1]-v[1])) / l2))
    proj = (v[0] + t*(w[0]-v[0]), v[1] + t*(w[1]-v[1]))
    return _distance(p, proj)


def _swept(A, B, P0, P1, r):
    d0x, d0y = A[0]-P0[0], A[1]-P0[1]
    dvx = (B[0]-A[0]) - (P1[0]-P0[0])
    dvy = (B[1]-A[1]) - (P1[1]-P0[1])
    a = dvx*dvx + dvy*dvy
    b = 2.0*(d0x*dvx + d0y*dvy)
    c = d0x*d0x + d0y*d0y - r*r
    if a < 1e-12:
        return c <= 0.0
    disc = b*b - 4.0*a*c
    if disc < 0.0:
        return False
    sq = math.sqrt(disc)
    t1 = (-b - sq)/(2.0*a)
    t2 = (-b + sq)/(2.0*a)
    return t2 >= 0.0 and t1 <= 1.0


def state_from_obs(obs):
    """Build a mutable sim state from an agent observation dict."""
    g = (lambda k, d=None: obs.get(k, d)) if isinstance(obs, dict) else (lambda k, d=None: getattr(obs, k, d))
    return {
        "planets": [list(p) for p in g("planets", [])],
        "fleets": [list(f) for f in g("fleets", []) or []],
        "initial_planets": [list(p) for p in g("initial_planets", []) or []],
        "comets": [dict(c, planet_ids=list(c["planet_ids"]), paths=c["paths"],
                        path_index=c["path_index"]) for c in (g("comets", []) or [])],
        "comet_planet_ids": list(g("comet_planet_ids", []) or []),
        "angular_velocity": float(g("angular_velocity", 0.03)),
        "step": int(g("step", 0)),
        "next_fleet_id": int(g("next_fleet_id", 0)),
    }


def step(st, actions, max_speed=6.0):
    """Advance one tick. actions = {player_id: [[from_id, angle, ships], ...]}.
    Mutates and returns st. Mirrors interpreter lines 409-715 (no comet spawn)."""
    planets = st["planets"]; fleets = st["fleets"]
    comet_set = set(st["comet_planet_ids"])
    initial_by_id = {p[0]: p for p in st["initial_planets"]}
    av = st["angular_velocity"]; step_n = st["step"]

    # expire comets that ran off their path (pre-launch)
    expired = []
    for grp in st["comets"]:
        idx = grp["path_index"]
        for i, pid in enumerate(grp["planet_ids"]):
            if idx >= len(grp["paths"][i]):
                expired.append(pid)
    if expired:
        es = set(expired)
        planets[:] = [p for p in planets if p[0] not in es]
        st["comet_planet_ids"] = [x for x in st["comet_planet_ids"] if x not in es]
        for grp in st["comets"]:
            grp["planet_ids"] = [x for x in grp["planet_ids"] if x not in es]
        st["comets"] = [g for g in st["comets"] if g["planet_ids"]]
        comet_set = set(st["comet_planet_ids"])

    # 0. launches
    for pid_player, action in actions.items():
        if not action:
            continue
        for move in action:
            if len(move) != 3:
                continue
            from_id, angle, ships = move
            ships = int(ships)
            fp = next((p for p in planets if p[0] == from_id), None)
            if fp and fp[1] == pid_player and fp[5] >= ships and ships > 0:
                fp[5] -= ships
                sx = fp[2] + math.cos(angle) * (fp[4] + 0.1)
                sy = fp[3] + math.sin(angle) * (fp[4] + 0.1)
                fleets.append([st["next_fleet_id"], pid_player, sx, sy, angle, from_id, ships])
                st["next_fleet_id"] += 1

    # 1. production
    for p in planets:
        if p[1] != -1:
            p[5] += p[6]

    # 2. planet end-of-tick positions
    paths = {}
    expired2 = []
    for p in planets:
        if p[0] in comet_set:
            continue
        old = (p[2], p[3]); new = old
        ip = initial_by_id.get(p[0])
        if ip is not None:
            dx = ip[2]-CENTER; dy = ip[3]-CENTER
            r = math.sqrt(dx*dx + dy*dy)
            if r + p[4] < ROTATION_RADIUS_LIMIT:
                ang0 = math.atan2(dy, dx)
                cur = ang0 + av*step_n  # matches env: angle = initial + av*step
                new = (CENTER + r*math.cos(cur), CENTER + r*math.sin(cur))
        paths[p[0]] = (old, new, True)
    for grp in st["comets"]:
        grp["path_index"] += 1
        idx = grp["path_index"]
        for i, pid in enumerate(grp["planet_ids"]):
            p = next((q for q in planets if q[0] == pid), None)
            if p is None:
                continue
            pp = grp["paths"][i]; old = (p[2], p[3])
            if idx >= len(pp):
                expired2.append(pid); paths[pid] = (old, old, True)
            else:
                new = (pp[idx][0], pp[idx][1]); check = old[0] >= 0
                paths[pid] = (old, new, check)

    # 3. fleet movement + collision
    remove = []; combat = {p[0]: [] for p in planets}
    for f in fleets:
        angle = f[4]; ships = f[6]
        sp = 1.0 + (max_speed-1.0) * (math.log(ships)/math.log(1000)) ** 1.5
        sp = min(sp, max_speed)
        old = (f[2], f[3])
        f[2] += math.cos(angle)*sp; f[3] += math.sin(angle)*sp
        new = (f[2], f[3])
        hit = False
        for p in planets:
            pa = paths.get(p[0])
            if pa is None or not pa[2]:
                continue
            if _swept(old, new, pa[0], pa[1], p[4]):
                combat[p[0]].append(f); remove.append(f); hit = True; break
        if hit:
            continue
        if not (0 <= f[2] <= BOARD_SIZE and 0 <= f[3] <= BOARD_SIZE):
            remove.append(f); continue
        if _pt_seg((CENTER, CENTER), old, new) < SUN_RADIUS:
            remove.append(f); continue

    # 4. apply planet movement
    for p in planets:
        pa = paths.get(p[0])
        if pa is not None:
            p[2], p[3] = pa[1]

    if expired2:
        es = set(expired2)
        planets[:] = [p for p in planets if p[0] not in es]
        st["comet_planet_ids"] = [x for x in st["comet_planet_ids"] if x not in es]
        for grp in st["comets"]:
            grp["planet_ids"] = [x for x in grp["planet_ids"] if x not in es]
        st["comets"] = [g for g in st["comets"] if g["planet_ids"]]

    st["fleets"] = [f for f in fleets if f not in remove]

    # 5. combat
    for pid, pf in combat.items():
        p = next((q for q in planets if q[0] == pid), None)
        if not p or not pf:
            continue
        ps = {}
        for f in pf:
            ps[f[1]] = ps.get(f[1], 0) + f[6]
        sp = sorted(ps.items(), key=lambda kv: kv[1], reverse=True)
        top_p, top_s = sp[0]
        if len(sp) > 1:
            sec = sp[1][1]; surv = top_s - sec
            if sp[0][1] == sp[1][1]:
                surv = 0
            surv_owner = top_p if surv > 0 else -1
        else:
            surv_owner = top_p; surv = top_s
        if surv > 0:
            if p[1] == surv_owner:
                p[5] += surv
            else:
                p[5] -= surv
                if p[5] < 0:
                    p[1] = surv_owner; p[5] = abs(p[5])

    st["step"] = step_n + 1
    return st


def score(st, player):
    """Ship count for `player` across planets+fleets (the env's tie-break metric)."""
    s = 0.0
    for p in st["planets"]:
        if p[1] == player:
            s += p[5]
    for f in st["fleets"]:
        if f[1] == player:
            s += f[6]
    return s


def margin(st, player, n_players=2):
    """player's ships minus the best opponent's -- the quantity we maximise."""
    tot = {}
    for p in st["planets"]:
        if p[1] != -1:
            tot[p[1]] = tot.get(p[1], 0) + p[5]
    for f in st["fleets"]:
        tot[f[1]] = tot.get(f[1], 0) + f[6]
    me = tot.get(player, 0.0)
    opp = max([v for k, v in tot.items() if k != player], default=0.0)
    return me - opp
