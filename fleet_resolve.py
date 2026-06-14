"""Exact incoming-fleet resolution using the faithful sim's geometry.

incoming(obs_dict, horizon) -> {planet_id: (friendly_by_owner, first_eta)}
Concretely returns dict: planet_id -> {"by_owner": {owner: ships}, "eta": {owner: first_arrival_tick}}
by simulating every fleet forward against rotating planets (no combat, no
launches) and recording which planet each fleet sweeps into and when.
"""
import math

BOARD = 100.0
CENTER = 50.0
SUN_R = 10.0
ROT_LIM = 50.0


def _swept(A, B, P0, P1, r):
    d0x, d0y = A[0] - P0[0], A[1] - P0[1]
    dvx = (B[0] - A[0]) - (P1[0] - P0[0])
    dvy = (B[1] - A[1]) - (P1[1] - P0[1])
    a = dvx * dvx + dvy * dvy
    b = 2.0 * (d0x * dvx + d0y * dvy)
    c = d0x * d0x + d0y * d0y - r * r
    if a < 1e-12:
        return c <= 0.0
    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        return False
    sq = math.sqrt(disc)
    t1 = (-b - sq) / (2.0 * a)
    t2 = (-b + sq) / (2.0 * a)
    return t2 >= 0.0 and t1 <= 1.0


def _pt_seg(p, v, w):
    l2 = (v[0] - w[0]) ** 2 + (v[1] - w[1]) ** 2
    if l2 == 0.0:
        return math.hypot(p[0] - v[0], p[1] - v[1])
    t = max(0, min(1, ((p[0] - v[0]) * (w[0] - v[0]) + (p[1] - v[1]) * (w[1] - v[1])) / l2))
    proj = (v[0] + t * (w[0] - v[0]), v[1] + t * (w[1] - v[1]))
    return math.hypot(p[0] - proj[0], p[1] - proj[1])


def incoming(obs, horizon=30, max_speed=6.0):
    planets = obs.get("planets", [])
    fleets = obs.get("fleets", []) or []
    if not fleets or not planets:
        return {}
    initial = {p[0]: p for p in obs.get("initial_planets", []) or []}
    av = float(obs.get("angular_velocity", 0.03))
    step0 = int(obs.get("step", 0))
    comet_set = set(obs.get("comet_planet_ids", []) or [])

    # planet positions per tick (rotating ones move; comets approximated static)
    def pos_at(p, k):
        ip = initial.get(p[0])
        if ip is None or p[0] in comet_set:
            return (float(p[2]), float(p[3]))
        dx = float(ip[2]) - CENTER; dy = float(ip[3]) - CENTER
        r = math.hypot(dx, dy)
        if r + float(p[4]) >= ROT_LIM:
            return (float(p[2]), float(p[3]))
        ang = math.atan2(dy, dx) + av * (step0 + k)
        return (CENTER + r * math.cos(ang), CENTER + r * math.sin(ang))

    out = {}
    live = [[float(f[2]), float(f[3]), float(f[4]), int(f[1]), float(f[6])] for f in fleets]
    for k in range(1, horizon + 1):
        if not live:
            break
        nxt = []
        for fl in live:
            x, y, ang, owner, ships = fl
            sp = 1.0 + (max_speed - 1.0) * (math.log(max(ships, 1.0)) / math.log(1000.0)) ** 1.5
            sp = min(sp, max_speed)
            nx = x + math.cos(ang) * sp
            ny = y + math.sin(ang) * sp
            hit = None
            for p in planets:
                p_old = pos_at(p, k - 1)
                p_new = pos_at(p, k)
                if _swept((x, y), (nx, ny), p_old, p_new, float(p[4])):
                    hit = p[0]
                    break
            if hit is not None:
                d = out.setdefault(hit, {"by_owner": {}, "eta": {}})
                d["by_owner"][owner] = d["by_owner"].get(owner, 0.0) + ships
                if owner not in d["eta"]:
                    d["eta"][owner] = k
                continue
            if not (0 <= nx <= BOARD and 0 <= ny <= BOARD):
                continue
            if _pt_seg((CENTER, CENTER), (x, y), (nx, ny)) < SUN_R:
                continue
            nxt.append([nx, ny, ang, owner, ships])
        live = nxt
    return out
