"""Phase 3a: build (features[40,F], target_matrix[40,40]) samples from Jake replays.
Label = where Jake sent ships (src_slot -> tgt_slot), recovered via intercept geometry.
Only turns with >=1 clean (angle_err<0.12) launch are kept. Slot = obs planet order."""
import json, glob, math, torch, sys
sys.path.insert(0,"/Users/haruka/kaggle")
from orbit_lite.adapter import single_obs_to_tensor
from orbit_lite.obs import parse_obs
from orbit_lite.movement import MovementConfig
from orbit_lite.movement_step import ensure_planet_movement
from orbit_lite.intercept_aim import intercept_angle

N=40; F=7; CENTER=50.0; ERRTOL=0.12
def feats(obs, ot, pid):
    P=obs.P
    x=torch.zeros(N,F)
    own=torch.zeros(P)
    own[obs.owned]=1.0
    enemy=obs.alive & (obs.owner_abs>=0) & (obs.owner_abs!=pid)
    own[enemy]=-1.0
    px=obs.x.float(); py=obs.y.float()
    ships=obs.ships.float()
    prod=ot["planets"][:,6].float() if ot["planets"].shape[1]>6 else torch.zeros(P)
    rad=ot["planets"][:,4].float() if ot["planets"].shape[1]>4 else torch.zeros(P)
    dist=torch.hypot(px-CENTER,py-CENTER)
    static=((dist+rad)>=50.0).float()
    k=min(P,N)
    x[:k,0]=own[:k]; x[:k,1]=ships[:k]/100.0; x[:k,2]=prod[:k]/10.0
    x[:k,3]=px[:k]/100.0; x[:k,4]=py[:k]/100.0; x[:k,5]=rad[:k]/5.0; x[:k,6]=static[:k]
    return x

def label_game(rep, samples):
    rw=rep["rewards"]; ji=rw.index(max(rw)); steps=rep["steps"]
    for s in steps:
        a=s[ji].get("action") or []
        if not a: continue
        od=s[ji]["observation"]; pid=int(od["player"])
        ot=single_obs_to_tensor(od,player_id=pid); obs=parse_obs(ot); P=obs.P
        if P<2: continue
        mv=ensure_planet_movement(obs_tensors=ot,
            expected_cfg=MovementConfig(movement_horizon=18,drift_epsilon=1e-3,track_fleets=True,player_count=2,max_tracked_fleets=128),
            cached_movement=None)
        pids=ot["planets"][...,0].long().tolist(); id2slot={p:i for i,p in enumerate(pids)}
        tgt=torch.arange(P)
        M=torch.zeros(N,N)
        any_lab=False
        for (src_id,ang,ships) in a:
            si=id2slot.get(int(src_id))
            if si is None or si>=N: continue
            sizes=torch.full((1,P),float(ships))
            aim=intercept_angle(mv,torch.tensor([[si]]),tgt.view(1,P),sizes,active=torch.ones(1,P,dtype=torch.bool))
            d=torch.remainder(aim["angle"].view(P)-float(ang)+math.pi,2*math.pi)-math.pi
            d=d.abs(); d[~aim["viable"].view(P)]=99
            best=int(d.argmin())
            if float(d[best])<ERRTOL and best<N:
                M[si,best]+=float(ships); any_lab=True
        if any_lab:
            samples.append((feats(obs,ot,pid), M))

files=sorted(glob.glob("replays/jake/*.json"))
samples=[]
for i,f in enumerate(files):
    try: label_game(json.load(open(f)), samples)
    except Exception as e: print("skip",f,e)
    if (i+1)%20==0: print(f"{i+1}/{len(files)} games, {len(samples)} samples")
X=torch.stack([s[0] for s in samples]); Y=torch.stack([s[1] for s in samples])
torch.save({"X":X,"Y":Y}, "jake_dataset.pt")
print("SAVED jake_dataset.pt  X",tuple(X.shape),"Y",tuple(Y.shape))
