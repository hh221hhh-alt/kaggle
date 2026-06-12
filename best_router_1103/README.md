# BEST submission so far — Router (public score 1103.1)

Submitted 2026-06-11 (ref 53569678), status COMPLETE, **publicScore = 1103.1**
(previous exp48 baseline = 1067 -> +36).

## What it is
A player-count ROUTER:
- **2-player games -> exp48** (`exp48_agent.py`) — strongest in 2P.
- **4-player games -> I'M STRONGER** (`stronger_agent.py`) — FFA leader-targeting,
  beats exp48 ~71% in 4P.

Entry point = `main.py` (the router). Detects player count from `planets`
owners at step 0 (max owner index + 1) and dispatches.

## Files
- main.py            router (entry)
- exp48_agent.py     exp48 (ProducerLite, 7 waves)  -- 2P agent
- stronger_agent.py  "I'M STRONGER" (ProducerLite + FFA)  -- 4P agent
- orbit_lite/        shared planner library
- submission.tar.gz  the exact archive that was submitted

## Rebuild the tarball
    rm -rf build && mkdir build
    cp main.py exp48_agent.py stronger_agent.py build/
    cp -r orbit_lite build/orbit_lite
    tar -czf submission.tar.gz -C build .

## Local results (vs exp48)
- 2P: ~50% (routes to exp48 = identical)
- 4P: ~71% (routes to I'M STRONGER)

## Leaderboard context (4311 teams)
1103 = rank ~844 (top 20%). Bronze ~1177 (top10%), Silver ~1210 (top5%), Gold ~1490.
