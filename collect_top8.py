"""Collect top-8 bots' episodes: list via EpisodeService (with 429 backoff),
then download every episode the top bot WON from kaggleusercontent (no limit).
Builds replays/top8/index.json with per-episode metadata for analysis."""
import json, os, time, requests

TOKEN = os.environ.get("KAGGLE_API_TOKEN", "")  # set this env var before running
BASE = "https://www.kaggle.com/api/i/competitions.EpisodeService/"
HDR = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
TOP = {  # teamId -> (name, submissionId)
    15649057: ("JakeWill_1698", 53517858),
    15660477: ("Hober_1600", 53557911),
    15653847: ("Xiangyu_1574", 53516553),
    15719716: ("TonyK_1567", 53507942),
    15636758: ("tubo213_1564", 53449995),
    15654425: ("typeIIIfairy_1547", 53518572),
    15634651: ("MJM_1545", 53545513),
    15633678: ("dragon_1540", 53526382),
}

os.makedirs("replays/top8", exist_ok=True)


def list_eps(sub, tries=7):
    wait = 10
    for _ in range(tries):
        r = requests.post(BASE + "ListEpisodes", headers=HDR,
                          data=json.dumps({"submissionId": sub}), timeout=40)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            time.sleep(wait); wait = min(wait * 2, 120); continue
        print(f"  sub {sub}: HTTP {r.status_code}", flush=True)
        return None
    return None


index = []
for tid, (name, sub) in TOP.items():
    j = list_eps(sub)
    if not j:
        print(f"{name}: LIST FAILED", flush=True)
        continue
    eps = j.get("episodes", [])
    wins = []
    for e in eps:
        ags = e.get("agents", [])
        mine = [a for a in ags if a.get("submissionId") == sub]
        if not mine:
            continue
        my = mine[0]
        myr = my.get("reward", -99)
        best = max(a.get("reward", -99) for a in ags)
        won = myr is not None and myr == best and myr > -99
        meta = {
            "episode_id": e["id"], "team": name, "sub": sub,
            "agent_index": my.get("index", 0), "n_agents": len(ags),
            "won": bool(won),
            "rewards": [a.get("reward") for a in sorted(ags, key=lambda x: x.get("index", 0))],
            "scores": [round(a.get("initialScore") or 0) for a in sorted(ags, key=lambda x: x.get("index", 0))],
        }
        index.append(meta)
        if won:
            wins.append(meta)
    print(f"{name}: {len(eps)} eps, {len(wins)} wins", flush=True)
    # download wins
    got = 0
    for m in wins:
        p = f"replays/top8/{m['episode_id']}.json"
        if os.path.exists(p):
            got += 1; continue
        try:
            r = requests.get(f"https://www.kaggleusercontent.com/episodes/{m['episode_id']}.json", timeout=60)
            if r.status_code == 200:
                open(p, "wb").write(r.content); got += 1
        except Exception:
            pass
    print(f"  downloaded {got}/{len(wins)}", flush=True)
    time.sleep(8)  # be gentle on ListEpisodes rate limit

json.dump(index, open("replays/top8/index.json", "w"))
n2 = sum(1 for m in index if m["won"] and m["n_agents"] == 2)
n4 = sum(1 for m in index if m["won"] and m["n_agents"] == 4)
print(f"DONE index={len(index)} entries; wins on disk: 2P={n2} 4P={n4}", flush=True)
