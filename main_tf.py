"""Transformer-clone agent (standalone policy, no Producer planner).

Loads orbit_tf.pth (TFClone + calibrated launch threshold). Per turn: features
-> transformer -> for each owned planet above the launch threshold, send
(size_frac * garrison) ships at the relational head's top viable target using
orbit_lite's exact intercept aiming.
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
from fleet_resolve import incoming

N, F = 40, 17
CENTER = 50.0
MIN_SEND = 2


class TFClone(nn.Module):
    def __init__(self, d=96, nlayer=3, nhead=4):
        super().__init__()
        self.embed = nn.Linear(F, d)
        layer = nn.TransformerEncoderLayer(
            d_model=d, nhead=nhead, dim_feedforward=4 * d,
            batch_first=True, dropout=0.1, norm_first=True)
        self.enc = nn.TransformerEncoder(layer, nlayer)
        self.launch = nn.Linear(d, 1)
        self.q = nn.Linear(d, d)
        self.k = nn.Linear(d, d)
        self.size = nn.Linear(d, 1)
        self.dist_w = nn.Parameter(torch.tensor(-4.0))

    def forward(self, x):
        pad = x.abs().sum(-1) == 0
        h = self.enc(self.embed(x), src_key_padding_mask=pad)
        lo = self.launch(h).squeeze(-1)
        lo = lo.masked_fill(pad, -20.0)
        q = self.q(h); k = self.k(h)
        tl = torch.einsum("bid,bjd->bij", q, k) / (q.size(-1) ** 0.5)
        px, py = x[..., 3], x[..., 4]
        dmat = torch.sqrt((px.unsqueeze(2) - px.unsqueeze(1)) ** 2
                          + (py.unsqueeze(2) - py.unsqueeze(1)) ** 2 + 1e-9)
        tl = tl + self.dist_w * dmat
        tl = tl.masked_fill(pad.unsqueeze(1), -20.0)
        so = self.size(h).squeeze(-1)
        return lo, tl, so


_ckpt = torch.load(os.path.join(_HERE, "orbit_tf.pth"), map_location="cpu", weights_only=True)
_MODEL = TFClone()
_MODEL.load_state_dict(_ckpt["state"])
_MODEL.eval()
LAUNCH_TH = float(_ckpt.get("th", 0.7))

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
    inc = incoming(obs_dict, horizon=30)
    for i, p in enumerate(planets):
        if i >= N:
            break
        o = int(p[1])
        px, py = float(p[2]), float(p[3])
        rad = float(p[4]); ships = float(p[5])
        prod = float(p[6]) if len(p) > 6 else 0.0
        dist_c = math.hypot(px - CENTER, py - CENTER)
        d = inc.get(p[0], None)
        if d is not None:
            in_f = d["by_owner"].get(player, 0.0)
            in_e = sum(v for k_, v in d["by_owner"].items() if k_ != player)
            eta_f = d["eta"].get(player, 30)
            eta_e = min((v for k_, v in d["eta"].items() if k_ != player), default=30)
        else:
            in_f = in_e = 0.0; eta_f = eta_e = 30
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
        x[i, 7] = in_f / 100.0
        x[i, 8] = in_e / 100.0
        x[i, 9] = d_en / 100.0
        x[i, 10] = d_my / 100.0
        x[i, 11] = step
        x[i, 12] = standing if o == player else (npl - 2) / 2.0
        x[i, 13] = eta_e / 30.0
        x[i, 14] = eta_f / 30.0
        sign = 1.0 if o == player else (-1.0 if o >= 0 else 0.0)
        x[i, 15] = (ships * sign + in_f - in_e) / 100.0
        x[i, 16] = (in_e - ships) / 100.0 if o == player else 0.0
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
        lo, tl, so = _MODEL(X.unsqueeze(0))
        p_launch = torch.sigmoid(lo[0])
        tlog = tl[0]
        frac = torch.sigmoid(so[0])

    P = min(len(planets), N)
    launchers = []
    for i in range(P):
        if int(planets[i][1]) != player:
            continue
        if float(planets[i][5]) < MIN_SEND + 1:
            continue
        if float(p_launch[i]) >= LAUNCH_TH:
            launchers.append(i)
    # Jake's tempo: ~1.5 launches per acting turn — cap to the 2 most confident
    launchers = sorted(launchers, key=lambda i: -float(p_launch[i]))[:2]
    if not launchers:
        return []

    ot = single_obs_to_tensor(od, player_id=player)
    parse_obs(ot)
    mv = ensure_planet_movement(
        obs_tensors=ot,
        expected_cfg=MovementConfig(movement_horizon=18, drift_epsilon=1e-3,
                                    track_fleets=True, player_count=int(_mem["pc"]),
                                    max_tracked_fleets=128),
        cached_movement=_mem["movement"])
    _mem["movement"] = mv
    pids = ot["planets"][..., 0].long().tolist()
    Pt = ot["planets"].shape[0]
    tgt_all = torch.arange(Pt)

    moves = []
    for si in launchers:
        if si >= Pt:
            continue
        g = float(planets[si][5])
        send = max(MIN_SEND, int(g * float(frac[si])))
        if send > g:
            send = int(g)
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
