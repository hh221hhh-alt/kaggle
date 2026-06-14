"""I'M STRONGER + frontier concentration (principle #6).
After the base move, every owned planet pushes its surplus toward our FRONTIER
planet (the owned planet nearest the enemy mass), massing force at the front."""
from __future__ import annotations
import os, sys, math
try: _HERE=os.path.dirname(os.path.abspath(__file__))
except NameError: _HERE=os.getcwd()
if _HERE not in sys.path: sys.path.insert(0,_HERE)
import cand_stronger as B
RESERVE_FRAC=0.4; MIN_SURPLUS=12
def agent(obs):
    moves=B.agent(obs)
    try:
        player=int(obs["player"] if isinstance(obs,dict) else obs.player)
        planets=obs["planets"] if isinstance(obs,dict) else obs.planets
        comet=set(int(c) for c in ((obs.get("comet_planet_ids") if isinstance(obs,dict) else getattr(obs,"comet_planet_ids",[])) or []))
        mine=[p for p in planets if int(p[1])==player and int(p[0]) not in comet]
        enemy=[p for p in planets if int(p[1])!=player and int(p[1])>=0]
        if len(mine)<2 or not enemy: return moves
        ex=sum(float(e[2])*float(e[5]) for e in enemy)/max(1,sum(float(e[5]) for e in enemy))
        ey=sum(float(e[3])*float(e[5]) for e in enemy)/max(1,sum(float(e[5]) for e in enemy))
        front=min(mine,key=lambda p: math.hypot(float(p[2])-ex,float(p[3])-ey))
        fx,fy=float(front[2]),float(front[3])
        launched={}
        for m in moves:
            if len(m)>=3: launched[int(m[0])]=launched.get(int(m[0]),0)+int(round(float(m[2])))
        for s in mine:
            sid=int(s[0])
            if sid==int(front[0]): continue
            lo=int(float(s[5]))-launched.get(sid,0); use=int(lo*(1.0-RESERVE_FRAC))
            if lo<MIN_SURPLUS or use<3: continue
            ang=math.atan2(fy-float(s[3]),fx-float(s[2]))
            moves.append([sid,ang,use]); launched[sid]=launched.get(sid,0)+use
    except Exception: return moves
    return moves
