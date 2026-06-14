"""exp48 (our main) + careful multi-source SIEGE of defended static planets.

Fixes the prior exp48_coord 0-24 failure (which cannibalised defensive
garrison) with two guards:
  (1) per-source defensive RESERVE -- never send a planet's whole leftover;
  (2) only planets with a LARGE surplus qualify as siege sources.
Uses ONLY ships the exp48 planner did not launch this turn. Straight-line aim,
so restricted to STATIC (outer) enemy/neutral targets where that is exact.
Fires a combined strike only when sequential-combat (growth-aware) GUARANTEES
capture; otherwise it sends nothing (no wasted dribbles).
"""
from __future__ import annotations
import math, os, sys
try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import main as base

CENTER=50.0; ROT_LIMIT=50.0; MAX_SPEED=6.0
_LOG1000=math.log(1000.0)
RESERVE_FRAC   = 0.40   # keep this fraction of a source's leftover for defense
MIN_SURPLUS    = 30     # only planets with at least this leftover join a siege
COORD_MAX_SRC  = 5
OVERKILL       = 3
MARGIN_TURNS   = 1
MAX_SIEGES     = 3      # cap combined strikes per turn

def _speed(ships):
    s=max(1.0,float(ships)); r=min(1.0,math.log(s)/_LOG1000)
    return 1.0+(MAX_SPEED-1.0)*(r**1.5)
def _is_static(p):
    return math.hypot(float(p[2])-CENTER,float(p[3])-CENTER)+float(p[4])>=ROT_LIMIT
def _seq_ok(g,prod,contribs):
    g=float(g); prev=0
    for eta,sh in sorted(contribs):
        g+=max(0.0,float(prod))*(eta-prev); prev=eta
        if sh>g: return True
        g-=sh
    return False

def agent(obs):
    moves=base.agent(obs)
    try:
        player=int(obs.get("player",0) if isinstance(obs,dict) else obs.player)
        planets=obs.get("planets",[]) if isinstance(obs,dict) else obs.planets
        comet_ids=set(int(c) for c in (obs.get("comet_planet_ids",[]) or []))
        by_id={int(p[0]):p for p in planets if len(p)>=7 and int(p[0])>=0}
        launched={}
        for m in moves:
            if isinstance(m,(list,tuple)) and len(m)>=3:
                launched[int(m[0])]=launched.get(int(m[0]),0)+int(round(float(m[2])))
        # usable surplus per owned non-comet planet (keep RESERVE_FRAC for defense)
        avail={}
        for pid,p in by_id.items():
            if int(p[1])==player and pid not in comet_ids:
                lo=int(float(p[5]))-launched.get(pid,0)
                use=int(lo*(1.0-RESERVE_FRAC))
                if lo>=MIN_SURPLUS and use>=1:
                    avail[pid]=use
        if not avail: return moves
        targets=[p for pid,p in by_id.items()
                 if int(p[1])!=player and pid not in comet_ids and _is_static(p) and float(p[5])>=1]
        targets.sort(key=lambda p:-float(p[5]))
        used=set(); sieges=0
        for tgt in targets:
            if sieges>=MAX_SIEGES: break
            tx,ty=float(tgt[2]),float(tgt[3]); tg=float(tgt[5]); tprod=float(tgt[6])
            srcs=sorted((pid for pid in avail if pid not in used),
                        key=lambda pid:math.hypot(tx-float(by_id[pid][2]),ty-float(by_id[pid][3])))
            contribs=[]
            for pid in srcs:
                sp=by_id[pid]; d=math.hypot(tx-float(sp[2]),ty-float(sp[3]))
                sh=avail[pid]; eta=max(1,math.ceil(d/_speed(sh)))
                ang=math.atan2(ty-float(sp[3]),tx-float(sp[2]))
                contribs.append((pid,eta,sh,ang))
                if _seq_ok(tg+OVERKILL+tprod*MARGIN_TURNS,tprod,[(e,s) for _p,e,s,_a in contribs]):
                    for cpid,ceta,csh,cang in contribs:
                        moves.append([cpid,cang,csh]); used.add(cpid)
                    sieges+=1; break
                if len(contribs)>=COORD_MAX_SRC: break
    except Exception:
        return moves
    return moves
