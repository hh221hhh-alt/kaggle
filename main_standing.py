"""I'M STRONGER + standing-aware aggression (hand-crafted principle #2).

Each turn, judge whether we are winning / even / losing by total ship count,
and modulate the planner config: WINNING -> cautious (consolidate the lead,
don't overextend -> stay low-profile, the validated FFA principle); LOSING ->
aggressive (take risks to catch up); EVEN -> base. This is a CORE behaviour
switch (config per turn), not a surplus-moving overlay.
"""
from __future__ import annotations
import os, sys, dataclasses

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import torch
import cand_stronger as B

_mem = B.ProducerLiteMemory()
_PC = {"v": None}

WIN_RATIO = 1.15    # my ships > best_opp * this -> winning
LOSE_RATIO = 0.87   # my ships < best_opp * this -> losing


def _standing(obs, player):
    planets = obs["planets"] if isinstance(obs, dict) else obs.planets
    fleets = (obs.get("fleets") if isinstance(obs, dict) else getattr(obs, "fleets", [])) or []
    tot = {}
    for p in planets:
        o = int(p[1])
        if o >= 0:
            tot[o] = tot.get(o, 0) + float(p[5])
    for f in fleets:
        tot[int(f[1])] = tot.get(int(f[1]), 0) + float(f[6])
    me = tot.get(player, 0.0)
    opp = max([v for k, v in tot.items() if k != player], default=0.0)
    if opp <= 1e-6:
        return "winning"
    if me > opp * WIN_RATIO:
        return "winning"
    if me < opp * LOSE_RATIO:
        return "losing"
    return "even"


def _modulate(cfg, standing):
    if standing == "winning":   # cautious: fewer, higher-ROI commits; hold reserve
        return dataclasses.replace(
            cfg,
            roi_threshold=float(cfg.roi_threshold) * 1.4,
            max_waves_per_turn=max(3, int(cfg.max_waves_per_turn) - 2),
            min_ships_to_launch=float(cfg.min_ships_to_launch) + 3.0,
        )
    if standing == "losing":    # aggressive: cheaper commits, more waves
        return dataclasses.replace(
            cfg,
            roi_threshold=max(1.0, float(cfg.roi_threshold) * 0.7),
            max_waves_per_turn=int(cfg.max_waves_per_turn) + 4,
        )
    return cfg


def agent(obs):
    player = int(obs["player"] if isinstance(obs, dict) else obs.player)
    ot = B.single_obs_to_tensor(obs, player_id=player)
    if bool((ot["step"] == 0).all()):
        _PC["v"] = None
        _mem.reset()
    if _PC["v"] is None:
        _PC["v"] = B.largest_initial_player_count(ot)
    base_cfg = B._config_for(_PC["v"])
    cfg = _modulate(base_cfg, _standing(obs, player))
    with torch.no_grad():
        row = B.run_turn(ot, config=cfg, player_count=_PC["v"], memory=_mem)
    return B.sparse_action_row_to_moves(row, obs, player_id=player)
