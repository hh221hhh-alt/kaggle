"""Run OLD vs NEW once and auto-diagnose where NEW (our bot) goes wrong.

Usage (on your machine where orbit_wars works):
    python analyze_replay.py
Then paste the printed report back to me.

It plays submission-old.py (player 0) vs submission.py (player 1 = us) and prints:
  - a turn-by-turn time series of planets / ships / production for us vs enemy
    (so we can SEE the exact turn range where we fall behind), and
  - flags for: planets we lost, turns where a rich planet of ours sat idle,
    and our total fleet launches per turn (to spot the small-fleet 'rapid fire').
"""
import sys
from collections import defaultdict
from kaggle_environments import make

OLD = "submission-old.py"   # player 0
NEW = "submission.py"        # player 1 = us
US = 1                       # our player index
SEED = 42
IDLE_SHIP_THRESHOLD = 30     # a planet with >= this many ships that launched nothing = "idle"


def _planets(step):
    # shared observation lives on player 0's slot
    obs = step[0]["observation"]
    return obs.get("planets", []) or [], obs.get("fleets", []) or []


def _action_moves(step, player):
    """Return the list of [from_id, angle, ships] launches that `player` made."""
    a = step[player].get("action")
    if a is None:
        return []
    # action may be a plain move list, or a dict wrapping one
    if isinstance(a, dict):
        for k in ("submission", "action", "moves", "value"):
            if k in a and isinstance(a[k], list):
                a = a[k]
                break
        else:
            return []
    out = []
    if isinstance(a, list):
        for m in a:
            if isinstance(m, (list, tuple)) and len(m) >= 3:
                out.append((int(m[0]), float(m[1]), int(round(float(m[2])))))
    return out


def main():
    env = make("orbit_wars", configuration={"seed": SEED}, debug=False)
    env.run([OLD, NEW])
    steps = env.steps
    n = len(steps)
    print(f"game length: {n} turns,  seed {SEED},  US = player {US} ({NEW})")

    prev_owner = {}
    lost_log = []     # (turn, planet_id, new_owner)
    taken_log = []    # (turn, planet_id, from_owner) we captured
    cross_turn = None  # first turn our production lead goes negative

    print("\nturn |  our P/S/Prod        enemy P/S/Prod      | launches(ours)  idleRich")
    for t, step in enumerate(steps):
        planets, fleets = _planets(step)
        pc = defaultdict(int); sh = defaultdict(float); pr = defaultdict(float)
        owner_of = {}
        ships_of = {}
        for p in planets:
            if len(p) < 7:
                continue
            pid, owner, x, y, r, ships, prod = p[:7]
            pid = int(pid)
            if pid < 0:
                continue
            owner = int(owner)
            owner_of[pid] = owner
            ships_of[pid] = float(ships)
            if owner >= 0:
                pc[owner] += 1; sh[owner] += float(ships); pr[owner] += float(prod)

        # ownership changes
        for pid, owner in owner_of.items():
            po = prev_owner.get(pid)
            if po is not None and po != owner:
                if po == US and owner != US:
                    lost_log.append((t, pid, owner))
                elif owner == US and po != US:
                    taken_log.append((t, pid, po))
        prev_owner = dict(owner_of)

        moves = _action_moves(step, US)
        launched_from = {m[0] for m in moves}
        # idle rich planets: ours, >= threshold ships, launched nothing this turn
        idle_rich = sum(1 for pid, ow in owner_of.items()
                        if ow == US and ships_of.get(pid, 0) >= IDLE_SHIP_THRESHOLD
                        and pid not in launched_from)

        enemy = [o for o in pc if o != US]
        our_pr = pr.get(US, 0)
        en_pr = max((pr[o] for o in enemy), default=0)
        if cross_turn is None and t > 5 and our_pr < en_pr:
            cross_turn = t

        if t % 25 == 0 or t == n - 1:
            es = "/".join(f"{pc[o]}·{sh[o]:.0f}·{pr[o]:.0f}" for o in sorted(enemy)) or "-"
            print(f"{t:>4} |  {pc.get(US,0)}·{sh.get(US,0):.0f}·{our_pr:.0f}"
                  f"{'':6} {es:<18} |   {len(moves):>3}            {idle_rich}")

    print("\n--- diagnostics ---")
    final = steps[-1]
    print(f"final reward: us={final[US].reward}  enemy={final[1-US].reward}"
          f"  status us={final[US].status}")
    if cross_turn is not None:
        print(f"** our production first fell behind the enemy at turn {cross_turn} **")
    else:
        print("we kept the production lead the whole game (or won).")
    print(f"planets we LOST: {len(lost_log)} -> "
          f"{[(t, pid) for t, pid, _ in lost_log][:15]}")
    print(f"planets we CAPTURED: {len(taken_log)}")
    # launch-size histogram (spot the small-fleet rapid fire)
    sizes = []
    for step in steps:
        for m in _action_moves(step, US):
            sizes.append(m[2])
    if sizes:
        small = sum(1 for s in sizes if s <= 15)
        print(f"total launches: {len(sizes)},  <=15 ships: {small} "
              f"({100*small/len(sizes):.0f}%),  avg size {sum(sizes)/len(sizes):.1f}")

    with open("replay_diag.html", "w", encoding="utf-8") as f:
        f.write(env.render(mode="html"))
    print("rendered replay -> replay_diag.html")


if __name__ == "__main__":
    main()
