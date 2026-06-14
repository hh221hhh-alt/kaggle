"""Agent factory for ES fine-tuning: build a self-contained clone agent from a
given state_dict + threshold (no module-level globals shared across games)."""
import sys, os

sys.path.insert(0, "/Users/haruka/kaggle")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import torch
from orbit_lite.adapter import single_obs_to_tensor
from orbit_lite.obs import parse_obs
from orbit_lite.movement import MovementConfig
from orbit_lite.movement_step import ensure_planet_movement
from orbit_lite.intercept_aim import intercept_angle
from train_tf import TFClone
import main_tf as MT  # reuse _feats (F=17 with exact incoming)

N = 40
MIN_SEND = 2


def make_agent(state_dict, th):
    model = TFClone()
    model.load_state_dict(state_dict)
    model.eval()
    mem = {"movement": None, "pc": None}

    def agent(obs):
        od = obs if isinstance(obs, dict) else obs.__dict__
        player = int(od.get("player", 0))
        planets = od.get("planets", [])
        if not planets:
            return []
        if int(od.get("step", 0)) == 0:
            mem["movement"] = None
            mem["pc"] = None
        X, npl = MT._feats(od, player)
        if mem["pc"] is None:
            mem["pc"] = npl
        with torch.no_grad():
            lo, tl, so = model(X.unsqueeze(0))
            p_launch = torch.sigmoid(lo[0])
            tlog = tl[0]
            frac = torch.sigmoid(so[0])
        P = min(len(planets), N)
        launchers = [i for i in range(P)
                     if int(planets[i][1]) == player
                     and float(planets[i][5]) >= MIN_SEND + 1
                     and float(p_launch[i]) >= th]
        launchers = sorted(launchers, key=lambda i: -float(p_launch[i]))[:2]
        if not launchers:
            return []
        ot = single_obs_to_tensor(od, player_id=player)
        parse_obs(ot)
        mv = ensure_planet_movement(
            obs_tensors=ot,
            expected_cfg=MovementConfig(movement_horizon=18, drift_epsilon=1e-3,
                                        track_fleets=True, player_count=int(mem["pc"]),
                                        max_tracked_fleets=128),
            cached_movement=mem["movement"])
        mem["movement"] = mv
        pids = ot["planets"][..., 0].long().tolist()
        Pt = ot["planets"].shape[0]
        tgt_all = torch.arange(Pt)
        moves = []
        for si in launchers:
            if si >= Pt:
                continue
            g = float(planets[si][5])
            send = max(MIN_SEND, min(int(g), int(g * float(frac[si]))))
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

    return agent
