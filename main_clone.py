"""Full-policy clone agent (standalone — no Producer planner).

Per turn: build per-planet features, run the cloned policy net, and for every
owned planet the net says should LAUNCH, send (size_frac * garrison) ships at
the net's chosen target using orbit_lite's exact intercept aiming.
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
import torch.nn as nn

from orbit_lite.adapter import single_obs_to_tensor
from orbit_lite.obs import parse_obs
from orbit_lite.movement import MovementConfig
from orbit_lite.movement_step import ensure_planet_movement
from orbit_lite.intercept_aim import intercept_angle

N, F = 40, 13
CENTER = 50.0
LAUNCH_TH = 0.20
MIN_SEND = 2


class Clone(nn.Module):
    def __init__(self, h=384):
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Linear(N * F, h), nn.LayerNorm(h), nn.ReLU(),
            nn.Linear(h, h), nn.ReLU(),
            nn.Linear(h, 256), nn.ReLU(),
        )
        self.launch = nn.Linear(256, N)
        self.target = nn.Linear(256, N * N)
        self.size = nn.Linear(256, N)

    def forward(self, x):
        z = self.trunk(x.view(x.size(0), -1))
        return self.launch(z), self.target(z).view(-1, N, N), self.size(z)


_MODEL = Clone()
_MODEL.load_state_dict(torch.load(os.path.join(_HERE, "orbit_clone.pth"),
                                  map_location="cpu", weights_only=True))
_MODEL.eval()

_mem = {"movement": None, "pc": None}


def _feats(obs_dict, player):
    planets = obs_dict["planets"]
    fleets = obs_dict.get("fleets", []) or []
    x = torch.zeros(N, F)
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
    for i, p in enumerate(planets):
        if i >= N:
            break
        o = int(p[1])
        px, py = float(p[2]), float(p[3])
        rad = float(p[4]); ships = float(p[5])
        prod = float(p[6]) if len(p) > 6 else 0.0
        dist_c = math.hypot(px - CENTER, py - CENTER)
        nf = ne = 0.0
        for f in fleets:
            d = math.hypot(float(f[2]) - px, float(f[3]) - py)
            if d <= 15.0:
                if int(f[1]) == player:
                    nf += float(f[6])
                else:
                    ne += float(f[6])
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
        x[i, 7] = nf / 100.0
        x[i, 8] = ne / 100.0
        x[i, 9] = d_en / 100.0
        x[i, 10] = d_my / 100.0
        x[i, 11] = step
        x[i, 12] = standing if o == player else (npl - 2) / 2.0
    return x, npl


def agent(obs):
    od = obs if isinstance(obs, dict) else obs.__dict__
    player = int(od.get("player", 0))
    planets = od.get("planets", [])
    if not planets:
        return []
    step = int(od.get("step", 0))
    if step == 0:
        _mem["movement"] = None
        _mem["pc"] = None

    X, npl = _feats(od, player)
    if _mem["pc"] is None:
        _mem["pc"] = npl
    with torch.no_grad():
        lo, to, so = _MODEL(X.unsqueeze(0))
        p_launch = torch.sigmoid(lo[0])
        tlog = to[0]
        frac = torch.sigmoid(so[0])

    P = min(len(planets), N)
    moves = []
    # who launches?
    launchers = []
    for i in range(P):
        if int(planets[i][1]) != player:
            continue
        g = float(planets[i][5])
        if g < MIN_SEND + 1:
            continue
        if float(p_launch[i]) >= LAUNCH_TH:
            launchers.append(i)
    if not launchers:
        return []

    # aim with the engine's intercept geometry
    ot = single_obs_to_tensor(od, player_id=player)
    obs_t = parse_obs(ot)
    Pt = obs_t.P
    mv = ensure_planet_movement(
        obs_tensors=ot,
        expected_cfg=MovementConfig(movement_horizon=18, drift_epsilon=1e-3,
                                    track_fleets=True, player_count=int(_mem["pc"]),
                                    max_tracked_fleets=128),
        cached_movement=_mem["movement"])
    _mem["movement"] = mv
    pids = ot["planets"][..., 0].long().tolist()
    tgt_all = torch.arange(Pt)

    alive_slots = [i for i in range(min(Pt, N))]
    for si in launchers:
        if si >= Pt:
            continue
        g = float(planets[si][5])
        send = int(g * float(frac[si]))
        if send < MIN_SEND:
            continue
        # rank targets by the net, try until a viable intercept is found
        order = torch.argsort(tlog[si][: min(Pt, N)], descending=True).tolist()
        sizes = torch.full((1, Pt), float(send))
        aim = intercept_angle(mv, torch.tensor([[si]]), tgt_all.view(1, Pt), sizes,
                              active=torch.ones(1, Pt, dtype=torch.bool))
        ang = aim["angle"].view(Pt); viable = aim["viable"].view(Pt)
        for ti in order[:6]:
            if ti == si or ti >= Pt:
                continue
            if bool(viable[ti]):
                moves.append([int(pids[si]), float(ang[ti]), send])
                break
    return moves
