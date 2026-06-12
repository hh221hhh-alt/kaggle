"""Player-count router: exp48 for 2P (stronger there), I'M STRONGER for 4P (FFA).
Both are ProducerLite variants sharing orbit_lite; each keeps its own runtime."""
from __future__ import annotations
import os, sys
try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import exp48_agent as TWO           # exp48
import stronger_agent as FOUR # I'M STRONGER (FFA-aware)
_C = {"n": None}
def _nplayers(obs):
    pl = obs.get("planets") if isinstance(obs, dict) else obs.planets
    owners = {int(p[1]) for p in (pl or []) if int(p[1]) >= 0}
    return (max(owners) + 1) if owners else 2
def agent(obs):
    step = obs.get("step", 0) if isinstance(obs, dict) else getattr(obs, "step", 0)
    if step == 0 or _C["n"] is None:
        _C["n"] = _nplayers(obs)
    return FOUR.agent(obs) if _C["n"] >= 4 else TWO.agent(obs)
