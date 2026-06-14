# Hand-crafted bot — final version (preserved)

Haruka's original hand-built agent. ~8,600 lines. Fused design: an "old bot"
(o_-prefixed functions) for the opening + a custom territorial pipeline for
mid/late game.

## Files
- `submission.py`  the original Kaggle cell (first line is `%%writefile submission.py`)
- `main_new.py`    the runnable agent (same code, %%writefile line stripped) — use this
                   to run locally: `env.run(["handcrafted_final/main_new.py", ...])`

## Strength on the ladder
~890 public score (below exp48's 1067 and the router's 1103). Its ENGINE
(fleet sizing / arrival forecasting) is weaker than the Producer, but its
STRATEGIC BRAIN is sound and matches what top bots do.

## Strategy brain (validated against Jake's 1698 replays)
Mid/late pipeline priority (handle_* call order ~line 5268):
  comet_evac -> defense -> home_defense -> proactive_defense
  -> opportunistic_attack -> enemy_assault -> steady_fire
  -> comet_capture -> frontier_concentration

Key principles (all confirmed by top-bot replays):
1. Standing-aware risk: winning -> cautious (gain>1 only), even -> gain>0,
   losing -> aggressive (gain>-2), late -> all-out.
2. Proximity-first targeting (distance weighted x4 early).
3. Capture-guarantee: garrison-AT-ARRIVAL + reaction margin, never partial fleets.
4. Per-planet safe reserve.
5. Frontier / territory concentration: push surplus to the attack edge,
   cover the rear first, middle stays thin. Quadrant-based "_parent_quads".
6. Relay/staging: far targets advance to a nearer friendly planet.
Lots of 4-player (FFA) logic: COALITION, MEGA_HAMMER_4P, NEUTRAL_HARD_CAP_4P,
PROD_RESERVE_4P_ONLY, VALUE_WEIGHT_4P, etc.

## Session finding
Grafting these principles onto the Producer (exp48 / I'M STRONGER) was tested
exhaustively and did NOT help — the Producer already implements the good
tactical ones (#2 proximity, #3 capture, #4 reserve) in its core, and bolting
on the rest (standing/frontier/coalition) degraded it. Kept here as the record
of the strategy design (useful if a from-scratch planner is built later).
