"""I'M STRONGER + coalition/proactive defense (principle #1).
After the base move, reinforce owned planets that are out-threatened by a
nearby enemy mass, pulling surplus from the nearest stronger owned planet.
Defensive (sends to OWN planets), keeps a reserve on each source."""
from __future__ import annotations
import os, sys, math
try: _HERE=os.path.dirname(os.path.abspath(__file__))
except NameError: _HERE=os.getcwd()
if _HERE not in sys.path: sys.path.insert(0,_HERE)
import cand_stronger as B
THREAT_DIST=28.0; RESERVE_FRAC=0.5; MIN_SURPLUS=12
def agent(obs):
    moves=B.agent(obs)
    try:
        player=int(obs["player"] if isinstance(obs,dict) else obs.player)
        planets=obs["planets"] if isinstance(obs,dict) else obs.planets
        comet=set(int(c) for c in ((obs.get("comet_planet_ids") if isinstance(obs,dict) else getattr(obs,"comet_planet_ids",[])) or []))
        mine=[p for p in planets if int(p[1])==player and int(p[0]) not in comet]
        enemy=[p for p in planets if int(p[1])!=player and int(p[1])>=0]
        if not mine or not enemy: return moves
        launched={}
        for m in moves:
            if len(m)>=3: launched[int(m[0])]=launched.get(int(m[0]),0)+int(round(float(m[2])))
        # threatened owned planets: nearby enemy mass > own garrison
        for victim in mine:
            vx,vy=float(victim[2]),float(victim[3]); vg=float(victim[5])
            threat=sum(float(e[5]) for e in enemy if math.hypot(float(e[2])-vx,float(e[3])-vy)<=THREAT_DIST)
            if threat<=vg*1.1: continue
            need=int(threat-vg)
            # rally from nearest stronger owned planets' surplus
            srcs=sorted([p for p in mine if int(p[0])!=int(victim[0])],
                        key=lambda p: math.hypot(float(p[2])-vx,float(p[3])-vy))
            for s in srcs:
                if need<=0: break
                sid=int(s[0]); lo=int(float(s[5]))-launched.get(sid,0)
                use=int(lo*(1.0-RESERVE_FRAC))
                if lo<MIN_SURPLUS or use<3: continue
                send=min(use,need)
                ang=math.atan2(vy-float(s[3]),vx-float(s[2]))
                moves.append([sid,ang,send]); launched[sid]=launched.get(sid,0)+send; need-=send
    except Exception: return moves
    return moves
