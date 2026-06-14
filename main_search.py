"""exp48 + inference-time lookahead (training-free, GPU-immune).

Each turn we generate TWO coherent exp48 moves -- one under the base config,
one under a more aggressive config -- then roll each forward with the faithful
`sim` and keep whichever leaves us with the better material/territory margin.
Both candidates are real exp48 moves, so play stays coherent (no graft).
Falls back to the base move if we run low on the 1s act-budget.
"""
from __future__ import annotations
import os, sys, time, dataclasses

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import torch
import main as B
import sim

AGGR = dataclasses.replace(
    B.ProducerLiteConfig(),
    roi_threshold=1.05,
    max_waves_per_turn=14,
    terminal_max_waves_per_turn=14,
)
K_ROLLOUT = 12
TIME_BUDGET = 0.80   # seconds; leave margin under the 1s actTimeout

_base_mem = B.ProducerLiteMemory()
_aggr_mem = B.ProducerLiteMemory()
_PC = {"v": None}


def _moves_for(obs, player, base_cfg, mem):
    ot = B.single_obs_to_tensor(obs, player_id=player)   # fresh tensors per call
    step = int(ot["step"].reshape(-1)[0].item())
    cfg = B._apply_phase_config(base_cfg, step)
    row = B.run_turn(ot, config=cfg, player_count=_PC["v"], memory=mem)
    return B.sparse_action_row_to_moves(row, obs, player_id=player)


def _rollout_margin(obs, player, moves, opp):
    st = sim.state_from_obs(obs)
    sim.step(st, {player: moves, opp: []})
    for _ in range(K_ROLLOUT - 1):
        sim.step(st, {})
    return sim.margin(st, player)


def agent(obs):
    t0 = time.time()
    player = int(obs["player"] if isinstance(obs, dict) else obs.player)
    ot0 = B.single_obs_to_tensor(obs, player_id=player)
    if bool((ot0["step"] == 0).all()):
        _PC["v"] = None
        _base_mem.reset(); _aggr_mem.reset()
    if _PC["v"] is None:
        _PC["v"] = B.largest_initial_player_count(ot0)
    base_cfg = B._config_for(_PC["v"])

    with torch.no_grad():
        m_base = _moves_for(obs, player, base_cfg, _base_mem)
        cands = [m_base]
        if time.time() - t0 < TIME_BUDGET:
            cands.append(_moves_for(obs, player, AGGR, _aggr_mem))

    pc = _PC["v"] or 2
    opp = (1 - player) if pc == 2 else (player + 1) % pc
    best = m_base; bestv = None
    for mv in cands:
        v = _rollout_margin(obs, player, mv, opp)
        if bestv is None or v > bestv:
            bestv = v; best = mv
    return best
