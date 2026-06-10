%%writefile submission.py
import math
import os
import time
from collections import defaultdict, namedtuple

F14_4A_2P_FOCUS_ENABLED = True
F14_4A_2P_FOCUS_DIST_BONUS = 18.0   
F14_4A_2P_FOCUS_HAMMER_BONUS = 20.0
F14_4A_2P_FOCUS_MEGA_BONUS = 100

BOARD = 100.0
CENTER_X = 50.0
CENTER_Y = 50.0
SUN_R = 10.0
SUN_SAFETY = 1.5
ROTATION_LIMIT = 50.0
LAUNCH_CLEARANCE = 0.1
MAX_SPEED = 6.0
TOTAL_STEPS = 500
SIM_HORIZON = 110
FWD_SIM_FILTER_ENABLED = True   
FWD_SIM_HORIZON = 7             
FWD_SIM_DEFENSE_CHECK = True    
FWD_SIM_RANK_BONUS_4P = 0.0     
                                
SEARCH_EXPAND_4P_ENABLED = True 
                                
                                
SEARCH_EXPAND_2P_ENABLED = True 
SEARCH_MAX_PER_SOURCE = 3       
SEARCH_MAX_ACTIONS_TO_PICK = 5    
SEARCH_MAX_ACTIONS_TO_PICK_2P = 7 
SEARCH_DISABLES_CHEAP_PICKUP = True  
HAMMER_MELIS_VERIFY = True      
SEARCH_DEPTH2_ENABLED = True   


NEUTRAL_CAP_USES_EFFECTIVE_GARRISON = True
NEUTRAL_CAP_LOOKAHEAD = 10       

N6_USE_EFFECTIVE_PRE_GARRISON = True

TERMINAL_PHASE_ENABLED = True
TERMINAL_PHASE_TURNS = 30

FLEET_INTENT_ENABLED = True
FLEET_INTENT_MIN_DROP = 8       
FLEET_INTENT_HAMMER_BONUS = 5.0 


F1B_EXPAND_BONUS_ENABLED = True
F1B_EXPAND_BONUS = 3.0   


R1_RECAPTURE_PRIORITY_ENABLED = True
R1_RECAPTURE_HAMMER_BONUS = 8.0

E2_USE_GARRISON_THRESHOLD = True


SO1_STATIC_PREFERENCE_ENABLED = True
SO1_STATIC_BONUS = 2.179862   
SO1_STATIC_BONUS_2P = 2.179862    
SO1_STATIC_BONUS_4P = 2.95474    


SP1_SPEED_AWARE_ENABLED = True
SP1_LONG_DIST_THRESHOLD = 27.637375  
SP1_LONG_DIST_SHIPS = 22         


TI1_TIE_FOR_WIN_ENABLED = True
TI1_HORIZON_TURNS = 25           
TI1_REQUIRED_EXTRA_MARGIN = 5    
TI1_TRAILING_GAP_MIN = 10        


AS1_ANTI_SECOND_ENABLED = True


FAILTOLERANT_ENABLED = True


MELIS_SANITY_ENABLED = True
MELIS_SANITY_THETA = 3.0


F16_DIVERSITY_ENABLED = True
F16_CLOSEST_PICKS = 2   
F16_PROD_PICKS = 1      


FWD_SCORE_AGG_ENABLED = True
FWD_SCORE_AGG_TURNS = (4, 8, 14, 20)


PSM_OPENING_TURN = 14
PSM_OPENING_TURN_2P = 14    
PSM_OPENING_TURN_4P = 10    


ABSORB_MIN_THREAT = 3            
ABSORB_PROJECTION_MARGIN = 0     


DEFENSE_OVERSEND = 1             
DEFENSE_OVERSEND_2P = 1    
DEFENSE_OVERSEND_4P = 0    
DEFENSE_COALITION_MAX = 2        


MIN_DISPATCH_SHIPS = 10
SURPLUS_SHIP_TRIGGER = 10
SURPLUS_TARGET_CAP = 10

AIM_MAX_ITERS = 8
AIM_CONVERGE_DIST = 0.5
AIM_CONVERGE_TURNS = 1

ATTACK_MAX_SHIPS = 20          # non-collector attack cap

COMET_EVAC_REMAINING_TURNS = 8
COMET_EVAC_MIN_SHIPS = MIN_DISPATCH_SHIPS
COMET_CAPTURE_MIN_LIFE = 10    # only grab a comet if we'd own it at least this many turns

DOOM_EVAC_ENABLED = True
DOOM_EVAC_MIN_SHIPS = MIN_DISPATCH_SHIPS
DOOM_EVAC_MAX_TRAVEL = 10
DOOM_EVAC_ATTACK_FALLBACK_ENABLED = True
DOOM_EVAC_ATTACK_FALLBACK_4P_ONLY = False
DOOM_EVAC_ATTACK_OVERKILL = 2
DOOM_EVAC_ATTACK_PREFER_LAUNCHED_BONUS = 3

PREEMPTIVE_DOOM_EVAC_ENABLED = True
PREEMPTIVE_DOOM_EVAC_2P_ONLY = False
PREEMPTIVE_EVAC_DOOM_RATIO = 1.5
PREEMPTIVE_EVAC_DEFAULT_WINDOW = 5
PREEMPTIVE_EVAC_USE_LARGEST_SINGLE_ENEMY_4P = False

PROD_RESERVE_4P_ONLY = True
PROD_RESERVE_FRAC = 0.3
PROD_RESERVE_MIN_PROD = 3
PROD_RESERVE_TURN_MIN = 20

FWD_STAB_HORIZON = 15

GARRISON_TARGET = 10           # keep each planet at this many ships
SEGMENT_MAX_TURNS = 10         # never fire if arrival takes more than this many turns
EARLY_GAME_TURNS = 100         # aggressive early phase: fire when garrison > 5
HOME_SWEEP_TURN = 30           # start capturing all territory planets after this turn
EARLY_MIN_SHIPS = 5            # minimum fleet size in early game
HOME_RETURN_DIST_2P = 35.0     # send ships home if farther than this (2P)
HOME_RETURN_DIST_4P = 22.0     # send ships home if farther than this (4P)
ENEMY_ASSAULT_RATIO = 1.5      # launch all-out attack when we have this multiple of enemy garrison
THREAT_RATIO = 1.2             # planet is "threatened" if incoming enemy > defense * this
ROI_MIN_PROD = 1              # skip capturing a target whose production is below this (late only)
FWD_LOOKAHEAD_ENABLED = True   # late game: re-rank attack targets by board forward-sim
FWD_LOOKAHEAD_TOPK = 8        # only forward-sim the top-K candidates (cost control)
FRONTIER_SPLIT = 0.7          # surplus: 70% to frontier region, 30% to non-frontier
# Concentration target: if one quadrant is taking the bulk of incoming enemy
# fire, mass surplus there instead of the frontier. Otherwise default to frontier.
PRESSURE_FOCUS_SHARE = 0.65      # divert from frontier only if one quadrant holds
                                 # >=65% of all incoming enemy (clear single front)
PRESSURE_FOCUS_MIN_SHIPS = 20    # ignore trivial total pressure (noise) -> frontier
# Reaction-time capture margin: a far target gives the enemy time to reinforce,
# so add a flight-time-scaled buffer on top of the exact capture need.
REACT_FREE_TURNS = 3             # within this flight time the enemy can't react
REACT_SCALE_TURNS = 6            # then reaction ramps to full over this many turns
REACT_MARGIN_SHIPS = 8           # max extra ships added for a long-flight capture
# Pressure metric: blend in-flight enemy (certain) with "reachable enemy mass"
# (enemy garrison that could fly here within the horizon, distance-decayed) so
# the frontline signal anticipates threats before the enemy even launches.
PRESSURE_REACH_HORIZON = 12      # turns within which enemy garrison counts as "reachable"
PRESSURE_REACH_WEIGHT = 0.5      # weight of potential (reachable) mass vs in-flight ships
# Opportunistic attack: an enemy that just launched is a target if its CURRENT
# garrison is thin relative to its value -> threshold = OPP_BASE + production*OPP_PER_PROD
# (prod1->12, prod3->20, prod5->28). High-output planets are worth taking even
# when stocked; low-output ones only when nearly empty.
OPP_BASE = 8.0
OPP_PER_PROD = 4.0
# Opportunistic target priority = comprehensive of value / cost / distance
# (higher production better, fewer ships to crack better, nearer better).
OPP_W_PROD = 1.0
OPP_W_COST = 0.1
OPP_W_DIST = 0.05
OPP_MAX_COALITION = 3            # max planets that may combine on one opportunistic target
ASSAULT_MAX_COALITION = 4        # max planets that may combine to crack one assault target
# Opponent adaptation (#5) + proactive defense (#4). Aggression = share of the
# enemy's force that is in flight (vs sitting on planets), smoothed over turns.
AGGRESSION_EMA = 0.3             # smoothing factor for the aggression estimate
AGGRESSION_THRESHOLD = 0.25      # >= this share mobilized -> "aggressive" -> pre-defend
PROACTIVE_PRESSURE_MIN = 8.0     # only pre-reinforce planets whose net pressure clears this
PROACTIVE_MAX_TARGETS = 2        # at most this many pre-reinforcements per turn
PROACTIVE_MAX_SEND = 30          # cap ships sent per pre-reinforcement
# Parent (territory anchor) system. Parents = anchored quadrants; the anchor
# planet of a quadrant is its most central (corner-ward), static-preferred owned
# planet. Ships from planets that drift OUT of our anchored quadrants are pulled
# back to the nearest anchor.
PARENT_MAX = 4                   # at most one anchor per quadrant
PARENT_GROW_FRACTION = 0.40      # add an anchor in a quadrant once we own >= this share of its planets
BOARD_FILL_SWITCH = 0.80         # leave the early (old-bot) phase once this share of the board is claimed
INTERIOR_CAPTURE_BONUS = 20.0    # late capture: prefer targets inside our anchored quadrants
INTERIOR_OUTSIDE_PENALTY = 10.0  # ...and mildly avoid capturing outside our territory
DRIFT_RECLAIM_SECOND_DELAY = 5   # a drifted planet reclaims now and once more after this many turns
DRIFT_RECLAIM_KEEP_PROD = 4      # drifted planets with production >= this keep a defensive reserve
O_MAX_TRAVEL_CAP = 15        # early game: never launch a fleet taking more turns than this
COLLECTOR_ENABLED = False      # set True to re-enable collector fleet strategy
PARENT_ENABLED = True          # parent planet strategy
PARENT_START_TURN = 50         # parent strategy activates after this turn
OCCUPIED_THRESHOLD = 0.8       # 80% of planets owned = "occupied territory"
OCCUPIED_TURN = 50             # activate occupied distribution after this turn
# Opposite quadrant map: SE↔NW, NE↔SW
_OPPOSITE_Q = {3: 0, 0: 3, 2: 1, 1: 2}

F3_THREE_BUCKET_ENABLED = True
F3_SAFE_FLOOR = MIN_DISPATCH_SHIPS
F3_SAFE_DIST = 12.0
F3_HARD_FLOOR = 14
F3_HARD_GARRISON = 14


EXPAND_K_OPENING = 2             
EXPAND_K_MID = 1                 
EXPAND_MAX_TRAVEL_OPENING = 20
EXPAND_MAX_TRAVEL_MID = 14
EXPAND_MIN_MARGIN = 0            
EXPAND_MIN_MARGIN_4P = 3  


X8B_2P_EXTRA = 3
EXPAND_MIN_SHIPS = MIN_DISPATCH_SHIPS


EXPAND_MIN_PROD_2P = 2


TIEBREAK_ENABLED = True
TIEBREAK_EPS_FRAC = 0.005   
TIEBREAK_EPS_MIN = 1.439234      


ROT_AWARE_RANK_ENABLED = os.environ.get("V124_ROT_AWARE", "1") != "0"


VALUE_WEIGHT_2P = 4.86118
VALUE_WEIGHT_4P = float(os.environ.get("V126_VALUE_WEIGHT_4P", "2.0"))


ANTI_SNIPE_ENABLED = os.environ.get("V124_ANTI_SNIPE", "1") != "0"
ANTI_SNIPE_HORIZON = 25          
ANTI_SNIPE_2P_ONLY = False       


REACTIVE_SNIPE_PROJECTION_ENABLED = True
REACTIVE_EMIT_FRAC = 0.49629        
REACTIVE_MIN_ENEMY_SHIPS = 5     
REACTIVE_MIN_PROJECTED = 3       


SUN_SHADOW_REACTIVE_FILTER = True


COUNTER_SNIPE_ENABLED = os.environ.get("V124_COUNTER_SNIPE", "1") != "0"
COUNTER_SNIPE_2P_ONLY = False    
COUNTER_SNIPE_MAX_COST = 30
COUNTER_SNIPE_MIN_DELAY = 1
COUNTER_SNIPE_MAX_DELAY = 12


CHEAP_PICKUP_ENABLED = os.environ.get("V124_CHEAP_PICKUP", "1") != "0"
CHEAP_PICKUP_4P_ONLY = True
CHEAP_PICKUP_MAX_GARRISON = 25

CHEAP_PICKUP_MIN_PROD = int(os.environ.get("F32_CP_MIN_PROD", "2"))


ENDGAME_ROI_ENABLED = os.environ.get("V128_ENDGAME_ROI", "1") != "0"
ENDGAME_ROI_TURNS = 30


NEUTRAL_TEMPO_FILTER_ENABLED = os.environ.get("V128_TEMPO_FILTER", "1") != "0"
NEUTRAL_TEMPO_THRESHOLD = 10      


LAUNCH_BLACKOUT_ENABLED = os.environ.get("V128_LAUNCH_BLACKOUT", "1") != "0"
LAUNCH_BLACKOUT_TURNS = 10


NEUTRAL_HARD_CAP_ENABLED = os.environ.get("V128_NEUTRAL_CAP", "1") != "0"
NEUTRAL_HARD_CAP_4P = 40          
NEUTRAL_HARD_CAP_2P = 61          
NEUTRAL_WATCHLIST_MIN_DROP = 5   


LOW_PROD_NEUTRAL_SKIP_ENABLED = True
LOW_PROD_NEUTRAL_SKIP_PROD = 1       
LOW_PROD_NEUTRAL_SKIP_GARRISON = 14  


WEAKEST_TARGET_ENABLED = os.environ.get("V128_WEAKEST_TARGET", "1") != "0"
WEAKEST_TARGET_BONUS = 2.0      
WEAKEST_TARGET_MIN_STEP = 60    
WEAKEST_DONT_FINISH_SHARE = 0.05
WEAKEST_DONT_FINISH_PENALTY = 12.0 


LEADER_BASH_ENABLED = os.environ.get("V128_LEADER_BASH", "1") != "0"
LEADER_BASH_RATIO = 1.3
LEADER_BASH_BONUS = 4.0
LEADER_BASH_MIN_STEP = 60    


COALITION_ENABLED = True
COALITION_MAX_PARTICIPANTS = 3   
COALITION_NEUTRALS_ONLY = False  
COALITION_MAX_TRAVEL_BONUS = 2   
COALITION_MIN_PER_CONTRIBUTOR = 15   
COALITION_MIN_PER_CONTRIBUTOR_2P = 15    
COALITION_MIN_PER_CONTRIBUTOR_4P = 5    
COALITION_MIN_TARGET_SHIPS = 20      


HAMMER_ENABLED = True
HAMMER_STOCKPILE_MIN = 50
HAMMER_TARGET_PROD_MIN = 2
HAMMER_PROD_SHARE_TRIGGER = 0.40
HAMMER_OVERKILL_RATIO = 1.30
HAMMER_SURROUNDED_PROMOTE_TURNS = 10  
HAMMER_MAX_TRAVEL = 24                
HAMMER_ABORT_OVERRUN_RATIO = 1.329521     
HAMMER_PLAN_REVALIDATE_INTERVAL = 1   
HAMMER_MIN_PER_CONTRIBUTOR = 9        


MEGA_HAMMER_ENABLED = True


MEGA_HAMMER_4P_ONLY = True
MEGA_HAMMER_SHIPS_MIN = 300           
MEGA_HAMMER_TARGET_GARRISON_MAX = 80  
MEGA_HAMMER_MAX_TRAVEL = 40           


PROD_RESERVE_ENABLED = False          


MEGA_HAMMER_THRESHOLD_BY_PROD = {5: 200, 4: 250, 3: 300, 2: 350, 1: 400}


FRESH_CAPTURE_INHERITANCE_ENABLED = True
FRESH_CAPTURE_MAX_AGE = 5                  
MEGA_HAMMER_SHIPS_MIN_FRESH = 200          


MEGA_HAMMER_CONCENTRATE_ENABLED = True
MEGA_HAMMER_MAX_PER_TURN = 1               


MEGA_HAMMER_MELIS_VERIFY = True


MEGA_HAMMER_VERIFY_OPP_EMIT = 0.30


HAMMER_NO_THREAT_OVERSEND_ENABLED = True
HAMMER_NO_THREAT_OVERSEND_2P_ONLY = True


HAMMER_ALWAYS_OVERSEND_2P = False


HAMMER_SAFE_SURPLUS_OVERSEND_ENABLED = True
HAMMER_SAFE_SURPLUS_RATIO = 2.0  
HAMMER_OVERSEND_MAX_THREAT_RATIO = 0.3   


ACCUMULATOR_ENABLED = True
ACCUMULATOR_4P_ONLY = True                  
ACCUMULATOR_TURN_MIN = 15                   
ACCUMULATOR_LEAD_MIN_SHIPS = 100            
ACCUMULATOR_LEAD_THREAT_RATIO = 0.5         
ACCUMULATOR_FEEDER_MIN_SURPLUS = 30         
ACCUMULATOR_FEEDER_KEEP_RESERVE = 30        
ACCUMULATOR_FEEDER_MAX_TRAVEL = 30          
ACCUMULATOR_MAX_FEEDS_PER_TURN = 3          


BRAIN_LEAD_RESERVE_ENABLED = True
BRAIN_LEAD_RESERVE_4P_ONLY = True            


BRAIN_LEAD_RESERVE_MIN_SHIPS = 200


BRAIN_LEAD_RESERVE_REQUIRE_TARGET = False


BRAIN_LEAD_PREFER_FRONTIER = False
BRAIN_LEAD_FRONTIER_WEIGHT = 2.0


MEGA_HAMMER_TARGET_GARRISON_MAX_ITER_H = 100  


MULTIPRONG_ENABLED = False  
MULTIPRONG_2P_ONLY = True


MULTIPRONG_REINFORCER_MIN_RATIO = 1.0


MULTIPRONG_E_OVERKILL = 1.05

MULTIPRONG_CREDIBILITY_FACTOR = 0.6
MULTIPRONG_MAX_TRAVEL = 40       
MULTIPRONG_MIN_PER_CONTRIBUTOR = 8
MULTIPRONG_MAX_PARTICIPANTS = 3


LATE_FLUSH_REMAINING_TURNS = 25  
LATE_FLUSH_OVERKILL_RATIO = 1.05      


SOFT_DEADLINE_FRACTION = 0.82


RACE_ENABLED = True
RACE_HORIZON_TURNS = 18          
RACE_MAX_NEUTRAL_DIST = 20     
RACE_TIE_GOES_TO_LARGER = True   


PERSONALITY_ENABLED = True
PERSONALITY_AGG_HIGH = 0.30      
PERSONALITY_AGG_LOW = 0.10       
PERSONALITY_MIN_SAMPLE = 50      

MODE_PARAMS = {
    "patient": {
        "expand_k_opening": 2,            
        "expand_max_travel_opening": 22,  
        "expand_k_mid": 1,
        "expand_max_travel_mid": 14,      
        "hammer_prod_share": 0.2,
        "hammer_overkill": 1.30,
        "hammer_stockpile_min": 50,       
    },
    "opportunistic": {
        "expand_k_opening": 3,            
        "expand_max_travel_opening": 22,  
        "expand_k_mid": 2,                
        "expand_max_travel_mid": 18,      
        "hammer_prod_share": 0.35,        
        "hammer_overkill": 1.30,
        "hammer_stockpile_min": 50,
    },
    "pressure": {
        "expand_k_opening": 3,            
        "expand_max_travel_opening": 22,  
        "expand_k_mid": 0,
        "expand_max_travel_mid": 9,      
        "hammer_prod_share": 0.30,        
        "hammer_overkill": 1.20,          
        "hammer_stockpile_min": 50,
    },
}


MODE_PARAMS_2P = {
    "patient": {
        "expand_k_opening": 5,            
        "expand_max_travel_opening": 35,  
        "expand_k_mid": 4,                
        "expand_max_travel_mid": 28,      
        "hammer_prod_share": 0.30,        
        "hammer_overkill": 1.15,          
        "hammer_stockpile_min": 25,       
    },
    "opportunistic": {
        "expand_k_opening": 5,
        "expand_max_travel_opening": 35,
        "expand_k_mid": 6,
        "expand_max_travel_mid": 30,
        "hammer_prod_share": 0.28,
        "hammer_overkill": 1.15,
        "hammer_stockpile_min": 25,
    },
    "pressure": {
        "expand_k_opening": 5,
        "expand_max_travel_opening": 35,
        "expand_k_mid": 2,
        "expand_max_travel_mid": 52,      
        "hammer_prod_share": 0.25,        
        "hammer_overkill": 1.177645,
        "hammer_stockpile_min": 25,
    },
}


TWO_P_PATIENT_NUDGE_TURNS = 10
TWO_P_PATIENT_ESCALATE_TURNS = 20
TWO_P_PROD_SHARE_HISTORY = 10
TWO_P_PROD_SHARE_PROGRESS_EPS = 0.005    


STOP_EXPAND_2P_ENABLED = True


STOP_EXPAND_PROD_SHARE_2P = 0.65    
STOP_EXPAND_TURN_MIN_2P = 30        


COMBAT_STOP_EXPAND_ENABLED = False      
COMBAT_STOP_EXPAND_4P_ONLY = True
COMBAT_STOP_EXPAND_TURN_MIN = 25
COMBAT_CONTACT_MIN_SHIPS = 15
COMBAT_CHEAP_GARRISON = 10              
COMBAT_CHEAP_DIST = 12.0


PROD_LAG_STOP_EXPAND_ENABLED = True
PROD_LAG_STOP_EXPAND_TURN_MIN = 25
PROD_LAG_STOP_EXPAND_THRESH_2P = 0.40   
PROD_LAG_STOP_EXPAND_THRESH_4P = 0.22   


ENEMY_TEMPO_STOP_EXPAND_ENABLED = True
ENEMY_TEMPO_STOP_EXPAND_TURN_MIN = 20
ENEMY_TEMPO_STOP_EXPAND_MIN_LAUNCHES = 2


EASY_ENEMY_STOP_EXPAND_ENABLED = False
EASY_ENEMY_STOP_EXPAND_TURN_MIN = 15
EASY_ENEMY_MAX_GARRISON = 20
EASY_ENEMY_MAX_DIST = 25.0
EASY_ENEMY_MIN_COUNT = 1


TURN_CUTOFF_STOP_EXPAND_ENABLED = True
TURN_CUTOFF_STOP_EXPAND_TURN = 80   


PROD_LEAD_STOP_EXPAND_4P_ENABLED = True
PROD_LEAD_STOP_EXPAND_4P_TURN_MIN = 25
PROD_LEAD_STOP_EXPAND_4P_THRESH = 0.35   


STOCKPILE_STOP_EXPAND_ENABLED = True
STOCKPILE_STOP_EXPAND_TURN_MIN = 20
STOCKPILE_STOP_EXPAND_MAX_GARRISON = 250   


NEUTRAL_SATURATION_STOP_EXPAND_ENABLED = False  
NEUTRAL_SATURATION_2P_ONLY = True
NEUTRAL_SATURATION_TURN_MIN = 20
NEUTRAL_SATURATION_CHEAP_GARRISON = 10
NEUTRAL_SATURATION_REACH_DIST = 30.0


Planet = namedtuple("Planet", ["id", "owner", "x", "y", "radius", "ships", "production"])
Fleet = namedtuple("Fleet", ["id", "owner", "x", "y", "angle", "from_planet_id", "ships"])


def dist(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)


def fleet_speed(ships):
    if ships <= 1:
        return 1.0
    ratio = math.log(ships) / math.log(1000.0)
    ratio = max(0.0, min(1.0, ratio))
    return 1.0 + (MAX_SPEED - 1.0) * (ratio ** 1.5)


def orbital_radius(p):
    return dist(p.x, p.y, CENTER_X, CENTER_Y)


def is_static_planet(p):
    return orbital_radius(p) + p.radius >= ROTATION_LIMIT


def _init_is_static(init):
    """True if a planet's INITIAL position makes it static (outside rotation)."""
    return dist(init.x, init.y, CENTER_X, CENTER_Y) + init.radius >= ROTATION_LIMIT


def point_to_segment_distance(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    seg_sq = dx * dx + dy * dy
    if seg_sq <= 1e-9:
        return dist(px, py, x1, y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / seg_sq))
    return dist(px, py, x1 + t * dx, y1 + t * dy)


def segment_hits_sun(x1, y1, x2, y2):
    return point_to_segment_distance(CENTER_X, CENTER_Y, x1, y1, x2, y2) < SUN_R + SUN_SAFETY


def launch_point(sx, sy, sr, angle):
    c = sr + LAUNCH_CLEARANCE
    return sx + math.cos(angle) * c, sy + math.sin(angle) * c


def safe_geometry(sx, sy, sr, tx, ty, tr):
    """Direct-line angle + clear travel distance, or None if the path crosses the sun."""
    angle = math.atan2(ty - sy, tx - sx)
    lx, ly = launch_point(sx, sy, sr, angle)
    hit_d = max(0.0, dist(sx, sy, tx, ty) - (sr + LAUNCH_CLEARANCE) - tr)
    ex = lx + math.cos(angle) * hit_d
    ey = ly + math.sin(angle) * hit_d
    if segment_hits_sun(lx, ly, ex, ey):
        return None
    return angle, hit_d


def estimate_arrival(sx, sy, sr, tx, ty, tr, ships):
    safe = safe_geometry(sx, sy, sr, tx, ty, tr)
    if safe is None:
        return None
    angle, total_d = safe
    turns = max(1, int(math.ceil(total_d / fleet_speed(max(1, ships)))))
    return angle, turns


def predict_planet_position(planet, initial_by_id, ang_vel, turns):
    init = initial_by_id.get(planet.id)
    if init is None:
        return planet.x, planet.y
    r = dist(init.x, init.y, CENTER_X, CENTER_Y)
    if r + init.radius >= ROTATION_LIMIT:
        return planet.x, planet.y
    cur = math.atan2(planet.y - CENTER_Y, planet.x - CENTER_X)
    new = cur + ang_vel * turns
    return CENTER_X + r * math.cos(new), CENTER_Y + r * math.sin(new)


R4_BEHIND_SUN_WAIT_ENABLED = True
R4_FUTURE_HORIZON = 10    


def predict_comet_position(planet_id, comets, turns):
    for group in comets:
        pids = group.get("planet_ids", []) if isinstance(group, dict) else []
        if planet_id not in pids:
            continue
        idx = pids.index(planet_id)
        paths = group.get("paths", []) if isinstance(group, dict) else []
        path_index = group.get("path_index", 0) if isinstance(group, dict) else 0
        if idx >= len(paths):
            return None
        path = paths[idx]
        future_idx = int(path_index) + int(turns)
        if 0 <= future_idx < len(path):
            return float(path[future_idx][0]), float(path[future_idx][1])
        return None
    return None


def predict_target_position(target, world, turns):
    """Dispatch: comets use their precomputed path; orbital planets use angular
    extrapolation; static planets stay put. Returns (x, y) or None if a comet
    has expired by `turns`."""
    if target.id in world.comet_ids:
        pos = predict_comet_position(target.id, world.comets, turns)
        if pos is not None:
            return pos
        
    return predict_planet_position(target, world.initial_by_id, world.ang_vel, turns)


def is_in_approaching_direction(src, target, ang_vel, tx=None, ty=None):
    """Return True only if target is in the direction opposite to the board's rotation flow.
    Clockwise rotation (ang_vel < 0) → only shoot counter-clockwise (delta > 0).
    Counter-clockwise rotation (ang_vel > 0) → only shoot clockwise (delta < 0).
    No rotation → allow any direction.
    tx, ty: optional predicted target position override (for ideas 1+7).
    """
    if abs(ang_vel) < 1e-9:
        return True
    src_angle = math.atan2(src.y - CENTER_Y, src.x - CENTER_X)
    tgt_angle = math.atan2(
        (ty if ty is not None else target.y) - CENTER_Y,
        (tx if tx is not None else target.x) - CENTER_X,
    )
    delta = tgt_angle - src_angle
    while delta > math.pi:
        delta -= 2 * math.pi
    while delta < -math.pi:
        delta += 2 * math.pi
    if ang_vel < 0:
        return delta > 0
    else:
        return delta < 0


def aim_at_target(src, target, ships, initial_by_id, ang_vel, world=None,
                  check_approach=False):
    """Returns (angle, turns) or None.
    check_approach=True applies SEGMENT_MAX_TURNS limit and direction check.
    """
    est = estimate_arrival(src.x, src.y, src.radius, target.x, target.y, target.radius, ships)
    if est is None and R4_BEHIND_SUN_WAIT_ENABLED and world is not None:
        for future_t in range(2, R4_FUTURE_HORIZON, 2):
            if target.id in world.comet_ids:
                pos = predict_comet_position(target.id, world.comets, future_t)
            else:
                init = initial_by_id.get(target.id)
                if init is None:
                    pos = None
                elif _init_is_static(init):
                    pos = None
                else:
                    pos = predict_planet_position(target, initial_by_id, ang_vel, future_t)
            if pos is None:
                continue
            est = estimate_arrival(src.x, src.y, src.radius, pos[0], pos[1], target.radius, ships)
            if est is not None:
                break
    if est is None:
        return None

    is_comet = world is not None and target.id in world.comet_ids
    if not is_comet:
        init = initial_by_id.get(target.id)
        if init is None:
            result = est
        elif _init_is_static(init):
            result = est
        else:
            result = None
    else:
        result = None

    if result is None:
        angle, turns = est
        tx, ty = target.x, target.y
        for _ in range(AIM_MAX_ITERS):
            if is_comet:
                pos = predict_comet_position(target.id, world.comets, turns)
                if pos is None:
                    return None
                ntx, nty = pos
            else:
                ntx, nty = predict_planet_position(target, initial_by_id, ang_vel, turns)
            nest = estimate_arrival(src.x, src.y, src.radius, ntx, nty, target.radius, ships)
            if nest is None:
                return None
            nangle, nturns = nest
            if (abs(ntx - tx) < AIM_CONVERGE_DIST
                    and abs(nty - ty) < AIM_CONVERGE_DIST
                    and abs(nturns - turns) <= AIM_CONVERGE_TURNS):
                result = (nangle, nturns)
                break
            angle, turns = nangle, nturns
            tx, ty = ntx, nty
        if result is None:
            return None

    if check_approach:
        final_angle, final_turns = result
        if final_turns > SEGMENT_MAX_TURNS:
            return None
        if world is not None:
            pred_x, pred_y = predict_target_position(target, world, int(final_turns))
            if not is_in_approaching_direction(src, target, ang_vel,
                                               tx=pred_x, ty=pred_y):
                return None

    return result


def fleet_target_planet(fleet, planets, initial_by_id=None, ang_vel=0.0):
    """Which planet this in-flight fleet hits, and when (in turns from now).

    Two-pass: static planets via cheap straight-line intersection, orbital
    planets via per-turn forward simulation. The naive straight-line check
    against the planet's CURRENT position misses orbital targets â€" the
    planet has rotated since the fleet launched, so the ray won't intersect
    its current XY but WILL intersect its future orbital position. Without
    accounting for this, incoming hostile fleets at our orbital planets
    don't show up in arrivals_by_planet, and the reservation walk wrongly
    decides our planet is safe and lets it fire offensively.
    """
    dx_dir = math.cos(fleet.angle)
    dy_dir = math.sin(fleet.angle)
    speed = fleet_speed(fleet.ships)

    def _is_orbital(p):
        if initial_by_id is None:
            return False
        init = initial_by_id.get(p.id)
        if init is None:
            return False
        return dist(init.x, init.y, CENTER_X, CENTER_Y) + init.radius < ROTATION_LIMIT

    best_p, best_t = None, float(SIM_HORIZON) + 1.0

    
    for p in planets:
        if _is_orbital(p):
            continue
        dx = p.x - fleet.x
        dy = p.y - fleet.y
        proj = dx * dx_dir + dy * dy_dir
        if proj < 0:
            continue
        perp_sq = dx * dx + dy * dy - proj * proj
        rr = p.radius * p.radius
        if perp_sq >= rr:
            continue
        hit_d = max(0.0, proj - math.sqrt(max(0.0, rr - perp_sq)))
        t = hit_d / speed
        if t <= SIM_HORIZON and t < best_t:
            best_t, best_p = t, p

    
    if initial_by_id is not None:
        best_dsq = None
        max_t = int(math.ceil(min(best_t, float(SIM_HORIZON))))
        for t in range(1, max_t + 1):
            fx = fleet.x + dx_dir * speed * t
            fy = fleet.y + dy_dir * speed * t
            for p in planets:
                if not _is_orbital(p):
                    continue
                px, py = predict_planet_position(p, initial_by_id, ang_vel, t)
                rr = p.radius * p.radius
                dsq = (fx - px) ** 2 + (fy - py) ** 2
                if dsq < rr:
                    if t < best_t or (t == best_t and (best_dsq is None or dsq < best_dsq)):
                        best_t, best_p, best_dsq = float(t), p, dsq
            if best_p is not None and best_t <= t:
                break

    if best_p is None:
        return None, None
    return best_p, max(1, int(math.ceil(best_t)))


def garrison_at_arrival(target, travel_turns):
    """Defender ship count at the moment our fleet lands.
    Engine truth: production is a FLOAT added every turn (garrison = ships +
    production*turns). Flooring the rate first under-counts growth, so use floats.
    """
    if target.owner == -1:
        return float(target.ships)  # neutrals don't grow
    return float(target.ships) + float(target.production) * float(travel_turns)


def needed_to_capture(target, travel_turns):
    """Ships required at arrival to flip ownership (combat needs survivor >
    garrison strictly; engine ties go to the defender). floor(garrison)+1 is the
    smallest integer strictly greater than the (fractional) garrison."""
    return int(math.floor(garrison_at_arrival(target, travel_turns))) + 1


EFFECTIVE_GARRISON_ENABLED = True


def effective_garrison_at_arrival(target, travel_turns, world):
    """Defender count at our arrival, accounting for pre-arrival enemy fleets.
    Returns (projected_owner, projected_ships) at travel_turns."""
    if not EFFECTIVE_GARRISON_ENABLED:
        return target.owner, garrison_at_arrival(target, travel_turns)
    arrivals = world.arrivals_by_planet.get(target.id, [])
    
    if world.is_2p:
        relevant = sorted(
            ((eta, owner, ships) for eta, owner, ships in arrivals
             if 1 <= eta <= travel_turns and ships > 0 and owner != -1),
            key=lambda x: x[0],
        )
    else:
        relevant = sorted(
            ((eta, owner, ships) for eta, owner, ships in arrivals
             if 1 <= eta <= travel_turns and owner != world.player and ships > 0
             and owner != -1),
            key=lambda x: x[0],
        )
    if not relevant:
        return target.owner, garrison_at_arrival(target, travel_turns)
    owner = int(target.owner)
    ships = float(target.ships)
    prod = max(0.0, float(target.production))  # fractional production rate
    last_t = 0
    for eta, fleet_owner, fleet_ships in relevant:

        if owner != -1:
            ships += prod * (eta - last_t)
        if fleet_owner == owner:
            ships += fleet_ships  
        else:
            if fleet_ships > ships:
                owner = int(fleet_owner)
                ships = fleet_ships - ships
            elif fleet_ships < ships:
                ships -= fleet_ships
            else:
                ships = 0  
        last_t = eta
    
    if owner != -1:
        ships += prod * (travel_turns - last_t)
    return owner, ships


def effective_needed_to_capture(target, travel_turns, world):
    """needed_to_capture with effective_garrison_at_arrival projection.
    floor(garrison)+1 = smallest int strictly above the fractional garrison."""
    _, defender_ships = effective_garrison_at_arrival(target, travel_turns, world)
    return int(math.floor(defender_ships)) + 1


def compute_planet_reserve(planet, arrivals, player):
    """The minimum ships we must keep on the surface so the running balance never
    dips below ABSORB_PROJECTION_MARGIN through every incoming fleet's arrival,
    factoring production growth and friendly reinforcements.

    Returns (reserve, holds, deficit, deadline).
        reserve   int, ships that must NOT be sent out this turn.
        holds     True if reserve <= planet.ships (planet survives on its own).
        deficit   ships we still need from outside if !holds (else 0).
        deadline  earliest turn balance dips below margin if !holds (else None).

    V12.3c4 (2.4 redesign): per-fleet ABSORB_MIN_THREAT filter replaced
    with window-aggregated check. Window = garrison/production (the
    planet's natural absorb cycle). If sum(hostile_in_window) < threshold,
    ignore all hostile fleets within the window. Hostile fleets outside
    the window are always counted (they're far out enough that natural
    growth doesn't cover them and they aren't simple noise). Closes the
    Stackelberg-leader exploit (firing many sub-threshold fleets) without
    triggering absorb on transient noise the planet would have absorbed.
    """
    if planet.owner != player:
        return 0, True, 0, None

    prod = max(0.0, float(planet.production))  # fractional production rate
    ships_now = max(0, int(planet.ships))
    if prod > 0:
        absorb_window = max(1, int(ships_now / prod))
    else:
        absorb_window = SIM_HORIZON

    hostile_in_window = 0
    for eta, owner, ships in arrivals:
        if ships <= 0 or owner == player or owner == -1:
            continue
        if int(eta) <= absorb_window:
            hostile_in_window += int(ships)
    
    
    absorb_min_threat = max(1, min(ABSORB_MIN_THREAT, ships_now // 3))
    skip_in_window_hostiles = hostile_in_window < absorb_min_threat

    
    friendly_events = defaultdict(int)
    hostile_by_owner = defaultdict(lambda: defaultdict(int))
    for eta, owner, ships in arrivals:
        if ships <= 0:
            continue
        if owner == player:
            friendly_events[eta] += ships
        elif owner == -1:
            continue
        else:
            if skip_in_window_hostiles and int(eta) <= absorb_window:
                continue
            hostile_by_owner[eta][owner] += int(ships)

    events = defaultdict(int)
    for eta, ships in friendly_events.items():
        events[eta] += ships
    for eta, owner_totals in hostile_by_owner.items():
        
        sorted_h = sorted(owner_totals.values(), reverse=True)
        if len(sorted_h) == 1:
            survivor = sorted_h[0]
        elif sorted_h[0] == sorted_h[1]:
            survivor = 0
        else:
            survivor = sorted_h[0] - sorted_h[1]
        events[eta] -= survivor

    if not events:
        return 0, True, 0, None

    growth = float(planet.production)  # fractional production rate
    bal = float(planet.ships)
    last_t = 0
    min_bal = bal
    deadline = None

    for turn in sorted(events):
        bal += growth * (turn - last_t)
        bal += events[turn]
        if bal < min_bal:
            min_bal = bal
        if bal < ABSORB_PROJECTION_MARGIN and deadline is None:
            deadline = turn
        last_t = turn

    if min_bal >= ABSORB_PROJECTION_MARGIN:
        excess = min_bal - ABSORB_PROJECTION_MARGIN
        # reserve rounded DOWN = keep at least this many (don't over-reserve;
        # extra excess is genuinely spare). Stay safe by flooring excess.
        reserve = max(0, int(planet.ships) - int(math.floor(excess)))
        return reserve, True, 0, None

    # Not holding: round the deficit UP so we ask for enough reinforcement.
    deficit = ABSORB_PROJECTION_MARGIN - min_bal
    return int(planet.ships), False, int(math.ceil(deficit)), deadline


def forward_project(world, our_capture_target=None, our_capture_turn=None,
                    our_capture_ships=None, horizon=20,
                    project_opponent_moves=False,
                    opponent_emit_fraction=0.4,
                    snapshot_turns=None):
    """Project every planet's owner+ship count forward `horizon` turns.

    Inputs:
      world â€" current World snapshot.
      our_capture_target/turn/ships â€" optional our planned capture (treated
        as a hypothetical friendly fleet arrival).
      horizon â€" how many turns to project.
      project_opponent_moves â€" if True, each enemy planet launches a fraction
        of its CURRENT surplus toward its closest non-friendly target every
        few turns. Increases accuracy at cost of pessimism for our holdings.
      opponent_emit_fraction â€" fraction of surplus the projected launch sends.
    Returns:
      dict planet_id -> (owner_at_H, ships_at_H).

    Model:
      - Existing in-flight fleets arrive at their projected ETA (engine
        combat math: attackers fight each other top-minus-second, then
        survivor reinforces or attacks defender garrison).
      - Production accumulates each turn for owned planets.
      - Phantom launches: each enemy planet within max-speed reach of
        our_capture_target projects a fleet of size phantom_factor*ships
        with optimistic ETA. This catches the dominant snipe risk that
        existing arrivals_by_planet misses (the enemy hasn't launched yet
        but COULD before our planet stabilises).
    """
    
    by_pid = defaultdict(list)
    for pid, arrs in world.arrivals_by_planet.items():
        for eta, owner, ships in arrs:
            if 0 < eta <= horizon:
                by_pid[pid].append((int(eta), int(owner), int(ships)))

    
    if our_capture_target is not None and our_capture_turn is not None:
        by_pid[our_capture_target].append(
            (int(our_capture_turn), int(world.player), int(our_capture_ships))
        )

    
    state = {}
    for p in world.planets:
        state[p.id] = [int(p.owner), int(p.ships), int(p.production)]

    
    planet_pos_map = {p.id: (float(p.x), float(p.y)) for p in world.planets}
    pid_list = list(state.keys())

    
    prod_by_pid = {p.id: max(0, int(p.production)) for p in world.planets}

    snapshots = {} if snapshot_turns else None
    snapshot_set = set(snapshot_turns) if snapshot_turns else None
    for t in range(1, horizon + 1):
        
        for pid, st in state.items():
            if st[0] != -1:
                st[1] += st[2]
        
        
        if project_opponent_moves and t % 4 == 0:
            for pid, st in state.items():
                if st[0] == -1 or st[1] < 10:
                    continue
                src_x, src_y = planet_pos_map[pid]
                src_owner = st[0]
                best_d = float("inf")
                best_op = None
                for opid, ost in state.items():
                    if opid == pid or ost[0] == src_owner:
                        continue
                    ox, oy = planet_pos_map[opid]
                    d = ((src_x - ox) ** 2 + (src_y - oy) ** 2) ** 0.5
                    if d < best_d:
                        best_d, best_op = d, opid
                if best_op is None:
                    continue
                
                if src_owner == world.player:
                    frac = opponent_emit_fraction * 0.5
                else:
                    frac = opponent_emit_fraction
                emit = int(st[1] * frac)
                if emit < 5:
                    continue
                ratio = math.log(max(2, emit)) / math.log(1000.0)
                speed = 1.0 + (MAX_SPEED - 1.0) * (ratio ** 1.5)
                eta_arrive = max(1, int(math.ceil(best_d / speed)))
                arrival_t = t + eta_arrive
                if arrival_t > horizon:
                    continue
                by_pid[best_op].append((arrival_t, src_owner, emit))
                st[1] -= emit
        
        
        for pid, arrs in by_pid.items():
            this_turn = [(o, s) for et, o, s in arrs if et == t]
            if not this_turn:
                continue
            st = state[pid]
            defender_owner, garrison = st[0], st[1]
            from_owner = defaultdict(int)
            for o, s in this_turn:
                from_owner[o] += s
            sorted_owners = sorted(from_owner.items(), key=lambda x: -x[1])
            top_owner, top_ships = sorted_owners[0]
            if len(sorted_owners) >= 2:
                second_ships = sorted_owners[1][1]
                if top_ships == second_ships:
                    survivor_ships = 0
                    survivor_owner = -1
                else:
                    survivor_ships = top_ships - second_ships
                    survivor_owner = top_owner
            else:
                survivor_ships = top_ships
                survivor_owner = top_owner
            if survivor_ships > 0:
                if defender_owner == survivor_owner:
                    st[1] = garrison + survivor_ships
                else:
                    new_garrison = garrison - survivor_ships
                    if new_garrison < 0:
                        st[0] = survivor_owner
                        st[1] = -new_garrison
                    else:
                        st[1] = new_garrison
        if snapshot_set is not None and t in snapshot_set:
            snapshots[t] = {pid: (st[0], st[1]) for pid, st in state.items()}

    final = {pid: (st[0], st[1]) for pid, st in state.items()}
    if snapshot_turns is not None:
        return final, snapshots
    return final


def _depth2_penalty(world, our_action, top_opp_actions=2):
    """For our action, project worst-case opponent reply.
    Each enemy planet within reach of our_action's target tries to launch a
    counter-snipe. Returns the WORST (lowest from our POV) Melis score among
    those counter-snipe scenarios.

    Used to penalize our actions that invite easy counter-snipes.
    """
    target_id = our_action["target_id"]
    tgt = world.planet_by_id.get(target_id)
    if tgt is None:
        return 0.0

    # Call forward_project once outside the loop since it only depends on our_action and world
    proj = forward_project(
        world,
        our_capture_target=our_action["target_id"],
        our_capture_turn=our_action["arrival_turn"],
        our_capture_ships=our_action["ships"],
        horizon=FWD_SIM_HORIZON + 6,
        project_opponent_moves=True,
        opponent_emit_fraction=0.30,
    )
    end_owner, end_ships = proj.get(target_id, (-1, 0))

    worst_delta = 0.0
    candidates_evaluated = 0
    for ep in world.planets:
        if ep.owner == world.player or ep.owner == -1:
            continue
        if int(ep.ships) < 9:
            continue
        d = ((tgt.x - ep.x) ** 2 + (tgt.y - ep.y) ** 2) ** 0.5
        if d > 30.0:
            continue
        
        opp_ships = max(8, int(ep.ships) - 5)
        ratio = math.log(max(2, opp_ships)) / math.log(1000.0)
        speed = 1.0 + (MAX_SPEED - 1.0) * (ratio ** 1.5)
        opp_eta = max(1, int(math.ceil(d / speed)))
        if opp_eta > FWD_SIM_HORIZON + 4:
            continue
        
        if end_owner != world.player and opp_ships > end_ships:
            worst_delta = min(worst_delta, -opp_ships)
        candidates_evaluated += 1
        if candidates_evaluated >= top_opp_actions:
            break
    return worst_delta


def search_step_action(world, max_per_source=3, max_actions_to_eval=10,
                       use_depth2=False):
    """Depth-1 alpha-beta over step actions.

    1. Generate candidate step actions via generate_step_actions.
    2. Evaluate each via melis_evaluate (sim+score).
    3. Return list sorted by score (highest first), up to `max_actions_to_eval`.

    Each action has additional key "score". Caller picks top action(s) and
    commits via _commit_fleet.
    """
    actions = generate_step_actions(world, max_per_source=max_per_source)
    if not actions:
        return []
    baseline_score = melis_evaluate(world, our_step_action=None)
    
    
    apply_decay = world.is_2p
    scored = []
    for act in actions[:max_actions_to_eval]:
        act_score = melis_evaluate(world, our_step_action=act)
        gain = act_score - baseline_score
        if apply_decay and gain > 0:
            gain *= 0.97 ** int(act["arrival_turn"])
        act["score"] = gain
        scored.append(act)
    scored.sort(key=lambda a: (-a["score"], a.get("raw_dist", 0.0)))
    if use_depth2:
        
        for act in scored[:3]:
            act["score"] += _depth2_penalty(world, act)
        scored.sort(key=lambda a: (-a["score"], a.get("raw_dist", 0.0)))
    
    
    if MELIS_SANITY_ENABLED and world.is_2p and scored and scored[0]["score"] < MELIS_SANITY_THETA:
        return []
    return scored


def generate_step_actions(world, max_per_source=3):
    """Generate candidate "step actions" â€" Melis style. Each step action is
    a single capture targeting one planet, sourced from one of our planets.

    Returns list of dicts: {"target_id", "source_id", "angle", "arrival_turn",
                            "ships", "raw_dist"}.

    Pruning:
      - Skip targets that aren't reachable within max_travel + 4
      - Skip neutral targets blocked by NEUTRAL_HARD_CAP
      - Take top `max_per_source` per source (closest by raw distance)
    """
    actions = []
    if not world.my_planets:
        return actions
    
    is_opening = world.is_opening
    if is_opening:
        max_travel = world.mode_params.get(
            "expand_max_travel_opening", EXPAND_MAX_TRAVEL_OPENING)
    else:
        max_travel = world.mode_params["expand_max_travel_mid"]

    for src in world.my_planets:
        avail = max(0, int(src.ships))
        if avail < MIN_DISPATCH_SHIPS:
            continue
        targets = []
        for t in world.planets:
            if t.owner == world.player:
                continue
            if not is_targetable(world, t):
                continue
            if _neutral_blocked_by_cap(world, t):
                continue
            raw = dist(src.x, src.y, t.x, t.y)
            if raw / MAX_SPEED > max_travel + 4:
                continue
            targets.append((raw, t))
        targets.sort(key=lambda x: x[0])
        
        if F16_DIVERSITY_ENABLED:
            n_close = min(F16_CLOSEST_PICKS, max_per_source)
            picks = list(targets[:n_close])
            picked_ids = {p[1].id for p in picks}
            extras = [(raw, t) for raw, t in targets if t.id not in picked_ids]
            extras.sort(key=lambda x: (-int(x[1].production), x[0]))
            picks.extend(extras[:F16_PROD_PICKS])
        else:
            picks = targets[:max_per_source]
        for raw, t in picks:
            plan = plan_solo_capture(world, src, t, avail, max_travel)
            if plan is None:
                continue
            angle, turns, ships = plan
            actions.append({
                "target_id": int(t.id),
                "source_id": int(src.id),
                "angle": float(angle),
                "arrival_turn": int(turns),
                "ships": int(ships),
                "raw_dist": float(raw),
            })
    actions.sort(key=lambda a: (-world.planet_by_id[a["target_id"]].production, a["raw_dist"]))
    return actions


def melis_evaluate(world, our_step_action=None, horizon=12, future_horizon=8,
                   opp_emit=0.20):
    """Melis full-attack-future evaluator.

    Inputs:
      world â€" current World snapshot.
      our_step_action â€" optional dict {"target_id", "arrival_turn", "ships"}.
        If provided, simulates our planned capture as part of the projection.
      horizon â€" short-term sim horizon for our action's effect.
      future_horizon â€" additional "all-attack-future" projection turns where
        every planet (us + opponents) keeps emitting surplus toward closest
        non-friendly. Captures position quality beyond the immediate move.
      opp_emit â€" fraction of surplus opponents launch in projection. 0.30
        is the calibrated default; lower = more capture-friendly.

    Returns: scalar score from our player's POV (higher = better).
    """
    target = arrival = ships = None
    if our_step_action is not None:
        target = our_step_action.get("target_id")
        arrival = our_step_action.get("arrival_turn")
        ships = our_step_action.get("ships")
    H = horizon + future_horizon
    n = 2 if world.is_2p else 4
    if FWD_SCORE_AGG_ENABLED:
        snap_turns = tuple(t for t in FWD_SCORE_AGG_TURNS if t <= H)
        if not snap_turns:
            snap_turns = (H,)
        final, snaps = forward_project(
            world,
            our_capture_target=target,
            our_capture_turn=arrival,
            our_capture_ships=ships,
            horizon=H,
            project_opponent_moves=True,
            opponent_emit_fraction=opp_emit,
            snapshot_turns=snap_turns,
        )
        total = 0.0
        count = 0
        for t in snap_turns:
            snap = snaps.get(t)
            if snap is None:
                continue
            total += forward_score(snap, world.player, n, world)
            count += 1
        if H not in snap_turns:
            total += forward_score(final, world.player, n, world)
            count += 1
        return total / max(1, count)
    state = forward_project(
        world,
        our_capture_target=target,
        our_capture_turn=arrival,
        our_capture_ships=ships,
        horizon=H,
        project_opponent_moves=True,
        opponent_emit_fraction=opp_emit,
    )
    return forward_score(state, world.player, n, world)


def forward_score(state, player, n_seats, world=None):
    """Score a forward-projected state from `player`'s POV.

    Combines: ship advantage + 5Ã—planet-count advantage + 8Ã—production advantage.
    Weights chosen so an extra owned planet is worth ~5 ships (a typical garrison)
    and an extra production unit is worth ~8 ships (â‰ˆ2 turns of growth)."""
    n_planets = [0] * n_seats
    n_prod = [0] * n_seats
    n_ships = [0] * n_seats
    for pid, (o, s) in state.items():
        if 0 <= o < n_seats:
            n_ships[o] += s
            n_planets[o] += 1
            if world is not None:
                p = world.planet_by_id.get(pid)
                if p is not None:
                    n_prod[o] += int(p.production)
    if n_seats <= 1:
        return n_ships[player]
    others = [i for i in range(n_seats) if i != player]
    leader_ships = max(n_ships[i] for i in others)
    leader_planets = max(n_planets[i] for i in others)
    leader_prod = max(n_prod[i] for i in others)
    return ((n_ships[player] - leader_ships)
            + 5 * (n_planets[player] - leader_planets)
            + 8 * (n_prod[player] - leader_prod))


class World:
    def __init__(self, obs, inferred_step=None):
        
        
        global COALITION_MIN_PER_CONTRIBUTOR, DEFENSE_OVERSEND, PSM_OPENING_TURN, SO1_STATIC_BONUS
        self.player = _read(obs, "player", 0)
        obs_step = _read(obs, "step", 0) or 0
        self.step = max(obs_step, inferred_step or 0)
        raw_planets = _read(obs, "planets", []) or []
        raw_fleets = _read(obs, "fleets", []) or []
        raw_init = _read(obs, "initial_planets", []) or []
        self.ang_vel = _read(obs, "angular_velocity", 0.0) or 0.0

        self.planets = [Planet(*p) for p in raw_planets]
        self.fleets = [Fleet(*f) for f in raw_fleets]
        self.initial_by_id = {Planet(*p).id: Planet(*p) for p in raw_init}

        
        raw_comet_ids = _read(obs, "comet_planet_ids", []) or []
        self.comet_ids = set(int(x) for x in raw_comet_ids)
        
        
        self.comet_remaining = {}
        raw_comet_groups = _read(obs, "comets", []) or []
        
        
        self.comets = raw_comet_groups
        for grp in raw_comet_groups:
            try:
                idx = int(grp.get("path_index", 0))
                pids = grp.get("planet_ids", []) or []
                paths = grp.get("paths", []) or []
                for i, pid in enumerate(pids):
                    if i < len(paths):
                        rem = max(0, len(paths[i]) - idx)
                        self.comet_remaining[int(pid)] = rem
            except (AttributeError, TypeError, IndexError):
                continue

        self.planet_by_id = {p.id: p for p in self.planets}
        self.my_planets = [p for p in self.planets if p.owner == self.player]
        self.enemy_planets = [p for p in self.planets if p.owner not in (-1, self.player)]
        self.neutral_planets = [p for p in self.planets if p.owner == -1]

        self.remaining_steps = max(1, TOTAL_STEPS - self.step)
        self.is_opening = self.step < PSM_OPENING_TURN
        self.is_late = self.remaining_steps < LATE_FLUSH_REMAINING_TURNS

        
        self.owner_strength = defaultdict(int)
        self.owner_production = defaultdict(int)
        for p in self.planets:
            if p.owner != -1:
                self.owner_strength[p.owner] += int(p.ships)
                self.owner_production[p.owner] += int(p.production)
        for f in self.fleets:
            self.owner_strength[f.owner] += int(f.ships)

        self.my_prod = self.owner_production.get(self.player, 0)
        self.total_prod = sum(self.owner_production.values())
        self.my_prod_share = (self.my_prod / self.total_prod) if self.total_prod else 0.0
        
        if self.remaining_steps < 80 and self.my_prod_share > 0.55:
            self.is_late = True

        
        self.leader_id = None
        self.contest_leader = False

        
        self.owner_planet_count = defaultdict(int)
        for p in self.planets:
            if p.owner not in (-1,):
                self.owner_planet_count[p.owner] += 1
        self.weakest_enemy = None
        self.weakest_enemy_prod_share = 0.0
        if self.total_prod > 0:
            best_score = None
            for owner in self.owner_production.keys():
                if owner in (-1, self.player):
                    continue
                score = (
                    self.owner_production.get(owner, 0) * 0.5
                    + self.owner_strength.get(owner, 0) * 0.3
                    + self.owner_planet_count.get(owner, 0) * 0.2
                )
                if best_score is None or score < best_score:
                    best_score = score
                    self.weakest_enemy = owner
            if self.weakest_enemy is not None:
                their_prod = self.owner_production.get(self.weakest_enemy, 0)
                self.weakest_enemy_prod_share = (
                    their_prod / self.total_prod if self.total_prod else 0.0
                )

        
        self.arrivals_by_planet = defaultdict(list)
        for f in self.fleets:
            target, eta = fleet_target_planet(f, self.planets, self.initial_by_id, self.ang_vel)
            if target is None:
                continue
            self.arrivals_by_planet[target.id].append((eta, int(f.owner), int(f.ships)))

        
        self.enemy_race_eta = _compute_enemy_race_eta(self) if RACE_ENABLED else {}
        
        
        global _game_num_players
        if _game_num_players is None and self.planets:
            _game_num_players = self.num_players
        self.is_2p = (_game_num_players == 2)

        
        if self.is_2p:
            COALITION_MIN_PER_CONTRIBUTOR = COALITION_MIN_PER_CONTRIBUTOR_2P
            DEFENSE_OVERSEND = DEFENSE_OVERSEND_2P
            PSM_OPENING_TURN = PSM_OPENING_TURN_2P
            SO1_STATIC_BONUS = SO1_STATIC_BONUS_2P
        else:
            COALITION_MIN_PER_CONTRIBUTOR = COALITION_MIN_PER_CONTRIBUTOR_4P
            DEFENSE_OVERSEND = DEFENSE_OVERSEND_4P
            PSM_OPENING_TURN = PSM_OPENING_TURN_4P
            SO1_STATIC_BONUS = SO1_STATIC_BONUS_4P

        
        if LEADER_BASH_ENABLED and not self.is_2p:
            lead_scores = {}
            for owner in self.owner_production.keys():
                if owner == -1:
                    continue
                lead_scores[owner] = (
                    self.owner_strength.get(owner, 0) * 0.5
                    + self.owner_production.get(owner, 0) * 0.5
                )
            if lead_scores:
                top_owner = max(lead_scores, key=lambda k: lead_scores[k])
                self.leader_id = top_owner
                my_score = lead_scores.get(self.player, 0)
                top_score = lead_scores.get(top_owner, 0)
                if (
                    top_owner != self.player
                    and my_score > 0
                    and (top_score / my_score) >= LEADER_BASH_RATIO
                ):
                    self.contest_leader = True

        
        self.mode = _detect_mode(self) if PERSONALITY_ENABLED else "patient"
        
        
        if TERMINAL_PHASE_ENABLED and self.remaining_steps < TERMINAL_PHASE_TURNS:
            self.mode = "pressure"
        params_table = MODE_PARAMS_2P if self.is_2p else MODE_PARAMS
        self.mode_params = params_table[self.mode]

        
        self.stop_expanding_2p = (
            STOP_EXPAND_2P_ENABLED
            and self.is_2p
            and self.step >= STOP_EXPAND_TURN_MIN_2P
            and self.my_prod_share >= STOP_EXPAND_PROD_SHARE_2P
        )

        
        self.in_combat_contact = False
        if COMBAT_STOP_EXPAND_ENABLED:
            my_ids = {p.id for p in self.my_planets}
            enemy_ids = {p.id for p in self.enemy_planets}
            for pid, arrs in self.arrivals_by_planet.items():
                if pid in my_ids:
                    for _eta, owner, ships in arrs:
                        if owner != self.player and owner != -1 and ships >= COMBAT_CONTACT_MIN_SHIPS:
                            self.in_combat_contact = True
                            break
                elif pid in enemy_ids:
                    for _eta, owner, ships in arrs:
                        if owner == self.player and ships >= COMBAT_CONTACT_MIN_SHIPS:
                            self.in_combat_contact = True
                            break
                if self.in_combat_contact:
                    break
        self.combat_stop_expand = (
            COMBAT_STOP_EXPAND_ENABLED
            and self.in_combat_contact
            and self.step >= COMBAT_STOP_EXPAND_TURN_MIN
            and (not COMBAT_STOP_EXPAND_4P_ONLY or not self.is_2p)
        )

        
        prod_lag_thresh = (
            PROD_LAG_STOP_EXPAND_THRESH_2P if self.is_2p
            else PROD_LAG_STOP_EXPAND_THRESH_4P
        )
        self.prod_lag_stop_expand = (
            PROD_LAG_STOP_EXPAND_ENABLED
            and self.step >= PROD_LAG_STOP_EXPAND_TURN_MIN
            and self.my_prod_share < prod_lag_thresh
        )

        
        self.enemy_tempo_stop_expand = (
            ENEMY_TEMPO_STOP_EXPAND_ENABLED
            and self.step >= ENEMY_TEMPO_STOP_EXPAND_TURN_MIN
            and FLEET_INTENT_ENABLED
            and len(_enemy_recently_launched) >= ENEMY_TEMPO_STOP_EXPAND_MIN_LAUNCHES
        )

        
        self.easy_enemy_stop_expand = False
        if EASY_ENEMY_STOP_EXPAND_ENABLED and self.step >= EASY_ENEMY_STOP_EXPAND_TURN_MIN:
            easy_count = 0
            for ep in self.enemy_planets:
                if int(ep.ships) > EASY_ENEMY_MAX_GARRISON:
                    continue
                for mp in self.my_planets:
                    if dist(mp.x, mp.y, ep.x, ep.y) <= EASY_ENEMY_MAX_DIST:
                        easy_count += 1
                        break
                if easy_count >= EASY_ENEMY_MIN_COUNT:
                    break
            self.easy_enemy_stop_expand = (easy_count >= EASY_ENEMY_MIN_COUNT)

        
        self.stockpile_stop_expand = False
        if STOCKPILE_STOP_EXPAND_ENABLED and self.step >= STOCKPILE_STOP_EXPAND_TURN_MIN:
            for mp in self.my_planets:
                if int(mp.ships) >= STOCKPILE_STOP_EXPAND_MAX_GARRISON:
                    self.stockpile_stop_expand = True
                    break

        
        self.prod_lead_stop_expand_4p = (
            PROD_LEAD_STOP_EXPAND_4P_ENABLED
            and not self.is_2p
            and self.step >= PROD_LEAD_STOP_EXPAND_4P_TURN_MIN
            and self.my_prod_share >= PROD_LEAD_STOP_EXPAND_4P_THRESH
        )

        
        self.turn_cutoff_stop_expand = (
            TURN_CUTOFF_STOP_EXPAND_ENABLED
            and self.step >= TURN_CUTOFF_STOP_EXPAND_TURN
        )

        
        self.neutral_saturation_stop_expand = False
        if (
            NEUTRAL_SATURATION_STOP_EXPAND_ENABLED
            and self.step >= NEUTRAL_SATURATION_TURN_MIN
            and (not NEUTRAL_SATURATION_2P_ONLY or self.is_2p)
        ):
            any_cheap = False
            for n in self.planets:
                if n.owner != -1 or n.id in self.comet_ids:
                    continue
                if int(n.ships) > NEUTRAL_SATURATION_CHEAP_GARRISON:
                    continue
                for mp in self.my_planets:
                    if dist(mp.x, mp.y, n.x, n.y) <= NEUTRAL_SATURATION_REACH_DIST:
                        any_cheap = True
                        break
                if any_cheap:
                    break
            self.neutral_saturation_stop_expand = not any_cheap

        
        self.stop_expand_lax = (
            self.combat_stop_expand
            or self.prod_lag_stop_expand
            or self.enemy_tempo_stop_expand
            or self.easy_enemy_stop_expand
            or self.neutral_saturation_stop_expand
            or self.stockpile_stop_expand
        )

        
        self.focus_enemy_2p = None
        if F14_4A_2P_FOCUS_ENABLED and self.is_2p:
            for o in self.owner_production.keys():
                if o not in (-1, self.player):
                    self.focus_enemy_2p = o
                    break

        self.home_center = None
        self.home_half_axis = None
        self.home_side_x = 0
        self.home_side_y = 0
        self.home_radius = 30.0
        self.home_sector_defined = False
        self._define_home_sector()

    @property
    def num_players(self):
        owners = set()
        for p in self.planets:
            if p.owner != -1:
                owners.add(p.owner)
        for f in self.fleets:
            owners.add(f.owner)
        return max(2, len(owners))

    def _define_home_sector(self):
        if not self.my_planets:
            return
        if self.step != 0:
            return
        xs = [p.x for p in self.my_planets]
        ys = [p.y for p in self.my_planets]
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)
        self.home_center = (cx, cy)
        dx = cx - CENTER_X
        dy = cy - CENTER_Y
        self.home_side_x = -1 if dx < 0 else 1
        self.home_side_y = -1 if dy < 0 else 1
        if self.is_2p:
            if abs(dx) >= abs(dy):
                self.home_half_axis = "x"
            else:
                self.home_half_axis = "y"
        else:
            self.home_half_axis = "xy"
        self.home_sector_defined = True

    def home_sector_contains(self, planet):
        if not self.home_sector_defined:
            return True
        if self.home_half_axis == "x":
            return (planet.x - CENTER_X) * self.home_side_x > 0
        if self.home_half_axis == "y":
            return (planet.y - CENTER_Y) * self.home_side_y > 0
        return ((planet.x - CENTER_X) * self.home_side_x > 0
                and (planet.y - CENTER_Y) * self.home_side_y > 0)

    def home_distance(self, planet):
        if self.home_center is None:
            return 0.0
        return dist(planet.x, planet.y, self.home_center[0], self.home_center[1])

    def home_penalty(self, planet):
        if self.home_sector_contains(planet):
            return 0.0
        return 10.0 if self.is_2p else 20.0


def _read(obs, key, default=None):
    if isinstance(obs, dict):
        return obs.get(key, default)
    return getattr(obs, key, default)


def _compute_enemy_race_eta(world):
    """For each neutral, return earliest turn an enemy could land a capturing
    fleet. Considers (a) enemy fleets already in flight aimed at this neutral,
    and (b) enemy planets that have enough ships and are within reach.
    Returns {neutral_id: eta_int}. Neutrals with no credible threat omitted.

    Used to prioritize uncontested-but-soon-to-be-contested neutrals AND to
    skip targets we'd lose the race for (saving ships for next turn).
    """
    out = {}
    if not world.neutral_planets:
        return out

    for n in world.neutral_planets:
        needed = int(n.ships) + 1
        earliest = None

        
        for eta, owner, ships in world.arrivals_by_planet.get(n.id, []):
            if owner == world.player or owner == -1:
                continue
            if ships < needed:
                continue
            if earliest is None or eta < earliest:
                earliest = int(eta)

        
        for ep in world.enemy_planets:
            if int(ep.ships) < needed:
                continue
            d = dist(ep.x, ep.y, n.x, n.y)
            if d > RACE_MAX_NEUTRAL_DIST:
                continue
            
            
            if safe_geometry(ep.x, ep.y, ep.radius, n.x, n.y, n.radius) is None:
                continue
            
            
            min_turns = max(1, int(math.ceil(d / fleet_speed(int(ep.ships)))))
            if min_turns > RACE_HORIZON_TURNS:
                continue
            if earliest is None or min_turns < earliest:
                earliest = min_turns

        if earliest is not None:
            out[n.id] = earliest
    return out


def _detect_mode(world):
    """Pick a personality mode from the current snapshot.

    Aggression score = (enemy ships in flight) / (total enemy ships, in flight
    or on planets). A high ratio means enemies are committing to attacks; a
    low ratio means they're stockpiling / quiet. We stay PATIENT during the
    opening since initial expansions look like aggression but aren't.

    V12.2 R2: in 2P, sustained PATIENT with no production-share gain forces
    escalation (10 turns â†' OPPORTUNISTIC, 20 turns â†' PRESSURE). This is the
    Bocsimacko "value action over inaction" principle â€" patient-vs-patient
    1v1 is a stable equilibrium the bot otherwise can't leave.
    """
    if world.is_opening:
        if world.is_2p:
            _record_2p_progress(world.my_prod_share, intended_patient=True, reset=True)
        return "patient"

    enemy_planet_ships = 0
    for p in world.planets:
        if p.owner not in (-1, world.player):
            enemy_planet_ships += int(p.ships)
    enemy_fleet_ships = 0
    for f in world.fleets:
        if f.owner != world.player and f.owner != -1:
            enemy_fleet_ships += int(f.ships)

    enemy_total = enemy_planet_ships + enemy_fleet_ships
    if enemy_total < PERSONALITY_MIN_SAMPLE:
        intended = "patient"
    else:
        aggression = enemy_fleet_ships / float(enemy_total)
        if aggression >= PERSONALITY_AGG_HIGH:
            intended = "pressure"
        elif aggression <= PERSONALITY_AGG_LOW:
            intended = "opportunistic"
        else:
            intended = "patient"

    if not world.is_2p:
        return intended

    
    _record_2p_progress(world.my_prod_share, intended_patient=(intended == "patient"))
    return "pressure"


def _record_2p_progress(my_prod_share, intended_patient, reset=False):
    """Track production-share trend in 2P. Increment streak whenever the bot
    intends to stay PATIENT and prod-share hasn't grown >EPS over the rolling
    window. Reset streak on opening, on non-PATIENT intent, or on real progress.
    Returns current streak length.
    """
    global _2p_patient_streak, _2p_prod_share_history
    if reset:
        _2p_patient_streak = 0
        _2p_prod_share_history = []
        return 0
    _2p_prod_share_history.append(float(my_prod_share))
    if len(_2p_prod_share_history) > TWO_P_PROD_SHARE_HISTORY:
        _2p_prod_share_history.pop(0)
    if not intended_patient:
        _2p_patient_streak = 0
        return 0
    if len(_2p_prod_share_history) >= TWO_P_PROD_SHARE_HISTORY:
        delta = _2p_prod_share_history[-1] - _2p_prod_share_history[0]
        if delta > TWO_P_PROD_SHARE_PROGRESS_EPS:
            _2p_patient_streak = 0
            return 0
    _2p_patient_streak += 1
    return _2p_patient_streak


_agent_step = 0
_game_num_players = None
_home_quadrant = None       # fixed home quadrant (set at step 0)
_parent_ids = []            # fixed parent planet IDs (set at step 0)
_parent_quads = set()       # anchored quadrants (our territory); grows up to PARENT_MAX
_drift_start = {}           # planet id -> step it drifted out of our territory
_drift_count = {}           # planet id -> reclaims done since it drifted
_late_latched = False       # True once the board is >= BOARD_FILL_SWITCH claimed (leave early phase)
_opp_aggression = 0.0       # smoothed estimate of how aggressive the opponent is (0-1)
_starting_max_prod = None   # max production of starting planets (set at step 0)
_idle_streak = {}           # planet_id -> consecutive turns with no target
_2p_patient_streak = 0
_2p_prod_share_history = []


_neutral_prev_ships = {}
_neutral_wounded = set()


_enemy_prev_ships = {}
_enemy_recently_launched = set()  


_planet_prev_owner = {}        
_freshly_lost_planets = set()  


_freshly_captured_planets = set()  
_planet_capture_age = {}      


_pending_commitments = []


OPP_PROFILE_WINDOW = 20
_opp_profile = {}


def _update_opp_profile_4p(world):
    """V12.8et: collect rolling per-enemy behavioral signals. 4P-only;
    caller must check world.is_2p first to avoid 2P side effects.
    """
    global _opp_profile
    if world.step == 0:
        _opp_profile = {}

    plan_ships = defaultdict(int)
    plan_max = defaultdict(int)
    plan_count = defaultdict(int)
    for p in world.planets:
        if p.owner == world.player or p.owner == -1:
            continue
        s = int(p.ships)
        plan_ships[p.owner] += s
        plan_count[p.owner] += 1
        if s > plan_max[p.owner]:
            plan_max[p.owner] = s
    fleet_ships = defaultdict(int)
    for f in world.fleets:
        if f.owner == world.player or f.owner == -1:
            continue
        fleet_ships[f.owner] += int(f.ships)

    enemies = set(plan_count.keys()) | set(fleet_ships.keys())
    for owner in enemies:
        ps = plan_ships.get(owner, 0)
        fs = fleet_ships.get(owner, 0)
        total = ps + fs
        emit = (fs / total) if total else 0.0
        prof = _opp_profile.setdefault(owner, {"emit": [], "stock": [], "plan": []})
        prof["emit"].append(emit)
        prof["stock"].append(plan_max.get(owner, 0))
        prof["plan"].append(plan_count.get(owner, 0))
        if len(prof["emit"]) > OPP_PROFILE_WINDOW:
            prof["emit"] = prof["emit"][-OPP_PROFILE_WINDOW:]
            prof["stock"] = prof["stock"][-OPP_PROFILE_WINDOW:]
            prof["plan"] = prof["plan"][-OPP_PROFILE_WINDOW:]

    world.opp_profile = _opp_profile


def predict_defender_at_arrival(world, target, arrival_turn):
    """Owner + ship count on `target` at `arrival_turn` (turns from now), using
    the same combat rules as the env: each turn growth, then resolve arrivals."""
    arrivals = world.arrivals_by_planet.get(target.id, [])
    by_turn = defaultdict(list)
    for eta, owner, ships in arrivals:
        if ships <= 0:
            continue
        by_turn[eta].append((owner, ships))

    owner = target.owner
    garrison = float(target.ships)
    horizon = max(1, int(math.ceil(arrival_turn)))

    for t in range(1, horizon + 1):
        if owner != -1:
            garrison += float(target.production)  # fractional production rate
        group = by_turn.get(t)
        if group:
            owner, garrison = _resolve_combat(owner, garrison, group)
    return owner, max(0.0, garrison)


def _resolve_combat(owner, garrison, arrivals):
    """Match the env's resolve rule: top-attacker minus second-attacker wins; ties = neutral."""
    by_owner = defaultdict(int)
    for o, s in arrivals:
        by_owner[o] += s
    if not by_owner:
        return owner, max(0.0, garrison)
    sorted_o = sorted(by_owner.items(), key=lambda kv: kv[1], reverse=True)
    top_o, top_s = sorted_o[0]
    if len(sorted_o) > 1 and top_s == sorted_o[1][1]:
        survivor_o, survivor_s = -1, 0
    elif len(sorted_o) > 1:
        survivor_o, survivor_s = top_o, top_s - sorted_o[1][1]
    else:
        survivor_o, survivor_s = top_o, top_s

    if survivor_s <= 0:
        return owner, max(0.0, garrison)
    if owner == survivor_o:
        return owner, garrison + survivor_s
    garrison -= survivor_s
    if garrison < 0:
        return survivor_o, -garrison
    return owner, garrison


FWD_SIM_ENABLED = os.environ.get("V128_FWD_SIM", "1") != "0"
FWD_LOOKAHEAD_HORIZON = 25
FWD_LOOKAHEAD_TOP_K = 6          
FWD_MAX_FLEETS = 80


def _fwd_clone(world):
    planet_ids = []
    planet_owner = {}
    planet_ships = {}
    planet_xy = {}
    planet_radius = {}
    planet_prod = {}
    orbital = {}
    for p in world.planets:
        if p.id in world.comet_ids:
            continue
        planet_ids.append(p.id)
        planet_owner[p.id] = int(p.owner)
        planet_ships[p.id] = float(p.ships)
        planet_xy[p.id] = (float(p.x), float(p.y))
        planet_radius[p.id] = float(p.radius)
        planet_prod[p.id] = int(p.production)
        init = world.initial_by_id.get(p.id)
        if init is not None:
            dx = float(init.x) - CENTER_X
            dy = float(init.y) - CENTER_Y
            r = math.sqrt(dx * dx + dy * dy)
            if r + p.radius < ROTATION_LIMIT:
                orbital[p.id] = (r, math.atan2(dy, dx))
    fleets = []
    next_id = 0
    for f in world.fleets:
        fleets.append([int(f.id), int(f.owner), float(f.x), float(f.y),
                       float(f.angle), int(f.ships)])
        next_id = max(next_id, int(f.id))
    return {
        "planet_ids": planet_ids,
        "planet_owner": planet_owner,
        "planet_ships": planet_ships,
        "planet_xy": planet_xy,
        "planet_radius": planet_radius,
        "planet_prod": planet_prod,
        "orbital": orbital,
        "fleets": fleets,
        "step": int(world.step),
        "ang_vel": float(world.ang_vel),
        "next_fleet_id": next_id + 1,
    }


def _fwd_inject_launch(state, src_id, angle, ships):
    if src_id not in state["planet_xy"]:
        return False
    if state["planet_ships"][src_id] < ships:
        return False
    state["planet_ships"][src_id] -= ships
    radius = state["planet_radius"][src_id]
    sx, sy = state["planet_xy"][src_id]
    fx = sx + math.cos(angle) * (radius + 0.1)
    fy = sy + math.sin(angle) * (radius + 0.1)
    owner = state["planet_owner"][src_id]
    state["fleets"].append([state["next_fleet_id"], int(owner), fx, fy,
                            float(angle), int(ships)])
    state["next_fleet_id"] += 1
    return True


def _fwd_step(state):
    for pid in state["planet_ids"]:
        if state["planet_owner"][pid] != -1:
            state["planet_ships"][pid] += state["planet_prod"][pid]
    combat = {pid: [] for pid in state["planet_ids"]}
    surviving = []
    radii = state["planet_radius"]
    xy = state["planet_xy"]
    pids = state["planet_ids"]
    for fl in state["fleets"]:
        ships = fl[5]
        if ships <= 0:
            continue
        speed = fleet_speed(ships)
        old_x, old_y = fl[2], fl[3]
        new_x = old_x + math.cos(fl[4]) * speed
        new_y = old_y + math.sin(fl[4]) * speed
        fl[2] = new_x
        fl[3] = new_y
        if not (0.0 <= new_x <= BOARD and 0.0 <= new_y <= BOARD):
            continue
        if point_to_segment_distance(CENTER_X, CENTER_Y, old_x, old_y, new_x, new_y) < SUN_R:
            continue
        hit_pid = -1
        for pid in pids:
            px, py = xy[pid]
            if point_to_segment_distance(px, py, old_x, old_y, new_x, new_y) < radii[pid]:
                hit_pid = pid
                break
        if hit_pid >= 0:
            combat[hit_pid].append(fl)
        else:
            surviving.append(fl)
    state["step"] += 1
    new_xy = dict(xy)
    for pid, (r, a0) in state["orbital"].items():
        a = a0 + state["ang_vel"] * state["step"]
        new_xy[pid] = (CENTER_X + r * math.cos(a), CENTER_Y + r * math.sin(a))
    still = []
    for fl in surviving:
        hit_pid = -1
        for pid in pids:
            if pid not in state["orbital"]:
                continue
            old_px, old_py = xy[pid]
            new_px, new_py = new_xy[pid]
            if point_to_segment_distance(fl[2], fl[3], old_px, old_py, new_px, new_py) < radii[pid]:
                hit_pid = pid
                break
        if hit_pid >= 0:
            combat[hit_pid].append(fl)
        else:
            still.append(fl)
    state["planet_xy"] = new_xy
    state["fleets"] = still
    for pid, arrivals in combat.items():
        if not arrivals:
            continue
        per_owner = defaultdict(int)
        for fl in arrivals:
            per_owner[fl[1]] += fl[5]
        sorted_o = sorted(per_owner.items(), key=lambda kv: kv[1], reverse=True)
        top_o, top_s = sorted_o[0]
        if len(sorted_o) > 1:
            second_s = sorted_o[1][1]
            if top_s == second_s:
                surv_s, surv_o = 0, -1
            else:
                surv_s, surv_o = top_s - second_s, top_o
        else:
            surv_o, surv_s = top_o, top_s
        if surv_s > 0:
            cur = state["planet_owner"][pid]
            if cur == surv_o:
                state["planet_ships"][pid] += surv_s
            else:
                state["planet_ships"][pid] -= surv_s
                if state["planet_ships"][pid] < 0:
                    state["planet_owner"][pid] = surv_o
                    state["planet_ships"][pid] = -state["planet_ships"][pid]


def _fwd_simulate(state, horizon):
    for _ in range(horizon):
        if len(state["fleets"]) > FWD_MAX_FLEETS:
            break
        _fwd_step(state)
    return state


def _fwd_my_score(state, player):
    total = 0.0
    for pid in state["planet_ids"]:
        if state["planet_owner"][pid] == player:
            total += state["planet_ships"][pid]
    for fl in state["fleets"]:
        if fl[1] == player:
            total += fl[5]
    return total


def _fwd_capture_holds_2p(world, src, target, angle, turns, ships, my_player):
    """V12.8av: simulate launching this fleet now; verify the captured
    target is still ours `turns + FWD_STAB_HORIZON` turns later. Returns
    True if capture sticks, False if predicted to flip."""
    state = _fwd_clone(world)
    if not _fwd_inject_launch(state, src.id, angle, int(ships)):
        return True  
    horizon = int(turns) + 15  
    _fwd_simulate(state, horizon)
    return state["planet_owner"].get(target.id) == my_player


def is_targetable(world, target):
    """Comets travel along non-orbital elliptical paths that aim_at_target can't
    predict. Aiming at them produces fleets that wander and often hit the sun.
    Skip them entirely as expansion / hammer targets.

    V12.9 redundant-launch fix: also skip NEUTRAL targets where one of OUR
    fleets is already in flight with enough ships to flip the planet on
    arrival. Prevents wasted small follow-up fleets piling on a neutral that
    is already being captured.

    V12.9 cap55: enforce the neutral hard cap (2P >=55, 4P legacy) here so
    every targeting code path obeys it â€" the previous per-call check at
    generate_step_actions/handle_expand missed cheap-pickup, multiprong, and
    other paths."""
    if target.id in world.comet_ids:
        return False
    if target.owner == -1:
        
        
        my_arrivals = sorted(
            ((eta, ships) for eta, owner, ships
             in world.arrivals_by_planet.get(target.id, [])
             if owner == world.player),
            key=lambda x: x[0],
        )
        if my_arrivals:
            total_ships = sum(s for _, s in my_arrivals)
            last_eta = my_arrivals[-1][0]
            if total_ships > garrison_at_arrival(target, last_eta):
                return False
        if _neutral_blocked_by_cap(world, target):
            return False
        
        
        if (LOW_PROD_NEUTRAL_SKIP_ENABLED
                and int(target.production) <= LOW_PROD_NEUTRAL_SKIP_PROD
                and int(target.ships) >= LOW_PROD_NEUTRAL_SKIP_GARRISON):
            return False
    return True


def _update_neutral_watchlist(world):
    """V12.8c: rebuild the wounded-neutral set from this turn's deltas.
    A neutral that lost >= NEUTRAL_WATCHLIST_MIN_DROP ships since last
    turn is considered wounded â€" someone else attacked it, so it's now
    cheaper for us to take. _neutral_prev_ships is then refreshed.

    V13.3 F1: also track enemy planet ship-drops as 'recently launched'
    signal. A drop > FLEET_INTENT_MIN_DROP indicates the source committed
    a fleet outward; the source is in a brief vulnerable state."""
    _neutral_wounded.clear()
    if NEUTRAL_HARD_CAP_ENABLED:
        for p in world.neutral_planets:
            prev = _neutral_prev_ships.get(p.id)
            cur = int(p.ships)
            if prev is not None and (prev - cur) >= NEUTRAL_WATCHLIST_MIN_DROP:
                _neutral_wounded.add(p.id)
    _neutral_prev_ships.clear()
    for p in world.neutral_planets:
        _neutral_prev_ships[p.id] = int(p.ships)
    
    if FLEET_INTENT_ENABLED:
        _enemy_recently_launched.clear()
        for p in world.enemy_planets:
            prev = _enemy_prev_ships.get(p.id)
            cur = int(p.ships)
            if prev is not None:
                
                
                expected = prev + int(p.production)
                if expected - cur >= FLEET_INTENT_MIN_DROP:
                    _enemy_recently_launched.add(p.id)
        _enemy_prev_ships.clear()
        for p in world.enemy_planets:
            _enemy_prev_ships[p.id] = int(p.ships)
    
    
    if R1_RECAPTURE_PRIORITY_ENABLED:
        _freshly_lost_planets.clear()
        _freshly_captured_planets.clear()
        for p in world.planets:
            prev_owner = _planet_prev_owner.get(p.id)
            if prev_owner == world.player and p.owner != -1 and p.owner != world.player:
                _freshly_lost_planets.add(p.id)
            
            if (
                FRESH_CAPTURE_INHERITANCE_ENABLED
                and prev_owner is not None
                and prev_owner != world.player
                and p.owner == world.player
            ):
                _freshly_captured_planets.add(p.id)
                _planet_capture_age[p.id] = 0
        
        if FRESH_CAPTURE_INHERITANCE_ENABLED:
            for pid in list(_planet_capture_age.keys()):
                if pid in _freshly_captured_planets:
                    continue
                pp = world.planet_by_id.get(pid)
                if pp is None or pp.owner != world.player:
                    del _planet_capture_age[pid]
                else:
                    _planet_capture_age[pid] += 1
                    if _planet_capture_age[pid] > FRESH_CAPTURE_MAX_AGE:
                        del _planet_capture_age[pid]
        _planet_prev_owner.clear()
        for p in world.planets:
            _planet_prev_owner[p.id] = int(p.owner)


def _neutral_blocked_by_cap(world, target):
    """V12.9 cap55: ignore neutrals with high garrison. V13.3 N4: use
    effective_garrison_at_arrival projection (estimated 10-turn lookahead)
    so a 60-ship neutral about to be hit by enemy 8 â†' effective 52 â†' unblocks."""
    if not NEUTRAL_HARD_CAP_ENABLED:
        return False
    if target.owner != -1:
        return False
    
    if NEUTRAL_CAP_USES_EFFECTIVE_GARRISON:
        eff_owner, eff_ships = effective_garrison_at_arrival(target, NEUTRAL_CAP_LOOKAHEAD, world)
        if eff_owner != -1:
            
            return False
        if world.is_2p:
            return eff_ships >= NEUTRAL_HARD_CAP_2P
        if eff_ships <= NEUTRAL_HARD_CAP_4P:
            return False
        return target.id not in _neutral_wounded
    
    if world.is_2p:
        return int(target.ships) >= NEUTRAL_HARD_CAP_2P
    if int(target.ships) <= NEUTRAL_HARD_CAP_4P:
        return False
    return target.id not in _neutral_wounded


def _neutral_tempo_ok(world, target, ships, turns):
    """V12.8cq: skip neutral captures whose expected production gain over
    remaining turns doesn't beat the ship cost by NEUTRAL_TEMPO_THRESHOLD.
    4P-only (2P duels make every neutral worth it). Refuses captures that
    repay slowly even if technically positive (kovi-inspired patience)."""
    if not NEUTRAL_TEMPO_FILTER_ENABLED:
        return True
    if world.is_2p:
        return True
    if target.owner != -1:
        return True
    remaining_after = max(0, int(world.remaining_steps) - int(turns))
    net = float(target.production) * remaining_after - float(ships)
    return net >= NEUTRAL_TEMPO_THRESHOLD


def _ti1_extra_margin(world):
    """V13.3 TI1: returns extra margin to require on captures when we're
    trailing the leader in the late game. Tie counts as a win (engine reward=1
    for max-sum players); low-margin failed attacks drop our absolute sum but
    not our enemies' enough to help. Conserve when behind."""
    if not TI1_TIE_FOR_WIN_ENABLED:
        return 0
    if world.remaining_steps > TI1_HORIZON_TURNS:
        return 0
    my_sum = world.owner_strength.get(world.player, 0)
    leader_sum = my_sum
    for owner, ships in world.owner_strength.items():
        if owner == world.player or owner == -1:
            continue
        if ships > leader_sum:
            leader_sum = ships
    if leader_sum - my_sum < TI1_TRAILING_GAP_MIN:
        return 0  
    return TI1_REQUIRED_EXTRA_MARGIN


def _endgame_roi_ok(world, target, ships, turns):
    """V12.8b: in the last ENDGAME_ROI_TURNS (4P only), refuse neutral captures
    whose expected production growth doesn't repay the ships spent. 4P-only
    because in 2P the differential-value of denying the neutral to the single
    opponent makes marginal late grabs still net-positive at this threshold;
    n=384 test of the un-gated version showed -38 wins 2P, +17pp 4P. Hostile
    targets always allowed. Returns True if firing is OK."""
    if not ENDGAME_ROI_ENABLED:
        return True
    if world.is_2p:
        return True
    if target.owner != -1:
        return True
    if world.step < TOTAL_STEPS - ENDGAME_ROI_TURNS:
        return True
    remaining_after = max(0, int(world.remaining_steps) - int(turns))
    expected_growth = float(target.production) * remaining_after
    
    
    threshold = float(target.ships) if E2_USE_GARRISON_THRESHOLD else float(ships)
    return expected_growth > threshold


def friendly_already_committed(world, target_id):
    """Patient ethos: ONE main fleet per target â€" UNLESS the target is enemy
    and our in-flight fleet undershoots its growing garrison.

    Neutrals don't grow, so a correctly-sized fleet wins or loses on arrival;
    a follow-up there is wasted ships (Bocsimacko/zvold canonical rule). For
    enemy targets, the planet grows by its production rate every turn the
    fleet is in flight, so a single source from long range can fail to
    capture; allow a sequenced follow-up only when no single pending fleet
    is sufficient at its own arrival turn.
    """
    target = world.planet_by_id.get(target_id)
    if target is None:
        return False
    pending = [c for c in _pending_commitments if c["target_id"] == target_id]
    if not pending:
        return False
    
    if target.owner == -1 or target.owner == world.player:
        return sum(c["ships"] for c in pending) > 0
    
    
    for c in pending:
        eta = int(c["arrival_abs"]) - int(world.step)
        if eta <= 0:
            continue
        if int(c["ships"]) >= needed_to_capture(target, eta):
            return True
    return False


def _commit_fleet(world, moves, spent, target_locked,
                  src_id, target_id, angle, turns, ships, allow_long=False):
    """Single point of truth for firing a fleet.
    Hard rules enforced here regardless of caller:
    - Minimum MIN_DISPATCH_SHIPS ships
    - Enemy/neutral targets must be in approaching direction (not chasing)
    - Turn limit SEGMENT_MAX_TURNS for enemy/neutral targets
    allow_long=True bypasses the turn-limit and direction check (used when a
    planet has had no target for several turns and must reach farther).
    """
    min_ships = EARLY_MIN_SHIPS if world.step < EARLY_GAME_TURNS else MIN_DISPATCH_SHIPS
    if int(ships) < min_ships:
        return
    # Cap fleet at 1000 — speed maxes out there, extra ships are wasted
    ships = min(int(ships), 1000)
    tgt_obj = world.planet_by_id.get(int(target_id))
    if tgt_obj is not None and tgt_obj.owner != world.player and not allow_long:
        if int(turns) > SEGMENT_MAX_TURNS:
            return
        src_obj = world.planet_by_id.get(int(src_id))
        if src_obj is not None:
            init = world.initial_by_id.get(tgt_obj.id)
            is_static = (init is not None and _init_is_static(init))
            in_home = (_home_quadrant is not None and
                       _get_quadrant(tgt_obj) == _home_quadrant)
            is_comet = int(target_id) in world.comet_ids
            # Skip the direction check (judged at launch position) only for:
            #  - static targets in our home territory (any time), or
            #  - static targets during the early land-grab (before turn 50), or
            #  - comets (they ride elliptical paths, not the rotation flow).
            # MOVING targets are always direction-checked (no chasing), incl. early.
            skip_dir = (is_static and in_home) or (world.step < 50 and is_static) or is_comet
            if not skip_dir:
                if not is_in_approaching_direction(src_obj, tgt_obj, world.ang_vel):
                    return
    moves.append([src_id, float(angle), int(ships)])
    spent[src_id] += int(ships)
    target_locked.add(target_id)
    
    target_obj = world.planet_by_id.get(int(target_id))
    owner_at_commit = int(target_obj.owner) if target_obj is not None else -2
    _pending_commitments.append({
        "target_id": int(target_id),
        "ships": int(ships),
        "arrival_abs": int(world.step) + int(turns),
        "owner_at_commit": owner_at_commit,
    })
    if os.environ.get("ORBIT_TRACE"):
        try:
            with open(os.environ["ORBIT_TRACE"], "a") as fh:
                fh.write(
                    f"t={world.step} src={src_id} tgt={target_id} ships={ships} eta={turns}\n"
                )
        except Exception:
            pass


def plan_solo_capture(world, src, tgt, max_avail, max_travel):
    """Plan a single-fleet capture (angle, turns, ships) honoring all the
    fleet-quality rules. Returns None if no viable shot exists.

    Critical: aiming uses fleet_speed(ships), so a different ship count than
    we end up sending produces a wrong angle and the fleet wanders / hits the
    sun. We aim, decide ships, then RE-AIM with the exact ship count.
    """
    
    
    raw_dist = dist(src.x, src.y, tgt.x, tgt.y)
    if F3_THREE_BUCKET_ENABLED:
        if tgt.owner == -1 and raw_dist < F3_SAFE_DIST:
            min_floor = F3_SAFE_FLOOR
        elif (tgt.owner != -1 and tgt.owner != world.player
              and int(tgt.ships) >= F3_HARD_GARRISON):
            min_floor = F3_HARD_FLOOR
        else:
            min_floor = MIN_DISPATCH_SHIPS
    else:
        min_floor = MIN_DISPATCH_SHIPS
    if max_avail < min_floor:
        return None
    aim = aim_at_target(src, tgt, max_avail, world.initial_by_id, world.ang_vel,
                        world=world, check_approach=True)
    if aim is None:
        return None
    angle, turns = aim
    if turns > max_travel:
        return None
    need = effective_needed_to_capture(tgt, turns, world)  
    margin = EXPAND_MIN_MARGIN_4P if not world.is_2p else EXPAND_MIN_MARGIN
    
    
    extra = X8B_2P_EXTRA if world.is_2p else 0
    
    
    extra += _ti1_extra_margin(world)
    preferred = max(min_floor, need + margin + extra)
    
    
    if SP1_SPEED_AWARE_ENABLED:
        raw_dist = dist(src.x, src.y, tgt.x, tgt.y)
        if raw_dist >= SP1_LONG_DIST_THRESHOLD:
            preferred = max(preferred, min(SP1_LONG_DIST_SHIPS, max_avail))
    if preferred <= max_avail:
        ships = preferred
    else:
        ships = max(min_floor, need + margin)
        if ships > max_avail:
            ships = max(min_floor, need)  
    if ships < min_floor or ships > max_avail:
        return None
    aim2 = aim_at_target(src, tgt, ships, world.initial_by_id, world.ang_vel,
                         world=world, check_approach=True)
    if aim2 is None:
        return None
    angle, turns = aim2
    if turns > max_travel:
        return None
    need2 = effective_needed_to_capture(tgt, turns, world)
    if ships < need2 + margin:
        ships = need2 + margin
        if ships > max_avail:
            return None
        aim3 = aim_at_target(src, tgt, ships, world.initial_by_id, world.ang_vel,
                             world=world, check_approach=True)
        if aim3 is None:
            return None
        angle, turns = aim3
        if turns > max_travel:
            return None
    
    
    if AS1_ANTI_SECOND_ENABLED and not world.is_2p:
        for eta, owner, e_ships in world.arrivals_by_planet.get(tgt.id, []):
            if int(eta) != int(turns):
                continue
            if owner == world.player or owner == -1:
                continue
            if int(e_ships) >= int(ships):
                return None  
    
    
    if FWD_SIM_FILTER_ENABLED and not world.is_2p and tgt.owner == -1:
        proj = forward_project(
            world,
            our_capture_target=tgt.id,
            our_capture_turn=int(turns),
            our_capture_ships=int(ships),
            horizon=FWD_SIM_HORIZON,
            project_opponent_moves=True,
            opponent_emit_fraction=0.30,
        )
        end_owner, end_ships = proj.get(tgt.id, (-1, 0))
        
        
        if end_owner != world.player and end_owner != -1 and end_ships > 5:
            return None
    return angle, turns, int(ships)


def handle_defense(world, rescue_needs, available, spent, target_locked,
                   moves, mode_log):
    """Rescue siblings flagged by absorb. Single source preferred; 2-source
    coalition fallback. Each rescuer respects its own reserve and arrives by
    deadline. Locked rescue targets prevent over-rescue.

    V14.2 (Phase 3.8): preemptive doom-evac. When total incoming enemy
    ships overwhelm garrison+future_production, the planet is definitely
    doomed even with rescue. Skip rescue (which wastes ships) and evac
    directly. User-observed scenario: 40 garrison, 10+49 incoming â†' solo
    rescue would send a sub-need fleet and still lose; better to evac.
    """
    if not rescue_needs:
        return

    # Defend by what we'd lose, most valuable first: a high-production planet
    # hurts most to lose, so when rescuers are scarce it gets first claim.
    ordered = sorted(rescue_needs.items(),
                     key=lambda kv: (-float(kv[1][2].production), -int(kv[1][2].ships)))
    for victim_id, (deficit, deadline, victim) in ordered:
        if victim_id in target_locked:
            continue
        need = deficit + DEFENSE_OVERSEND
        
        
        if PREEMPTIVE_DOOM_EVAC_ENABLED and (not PREEMPTIVE_DOOM_EVAC_2P_ONLY or world.is_2p):
            enemy_arrivals = [
                (eta, owner, int(ships)) for eta, owner, ships in world.arrivals_by_planet.get(victim_id, [])
                if owner != world.player and owner != -1
            ]
            if world.is_2p or not PREEMPTIVE_EVAC_USE_LARGEST_SINGLE_ENEMY_4P:
                threat_metric = sum(ships for _eta, _owner, ships in enemy_arrivals)
            else:
                
                by_owner = defaultdict(int)
                for _eta, owner, ships in enemy_arrivals:
                    by_owner[owner] += ships
                threat_metric = max(by_owner.values()) if by_owner else 0
            window = deadline if deadline is not None else PREEMPTIVE_EVAC_DEFAULT_WINDOW
            garrison_at_deadline = float(victim.ships) + float(victim.production) * int(window)
            if threat_metric > garrison_at_deadline * PREEMPTIVE_EVAC_DOOM_RATIO:
                if _try_doom_evac(world, victim, available, spent, target_locked, moves, mode_log):
                    continue
                
                
        solo = []
        for src in world.my_planets:
            if src.id == victim_id:
                continue
            avail = available[src.id] - spent[src.id]
            if avail < need:
                continue
            if avail < MIN_DISPATCH_SHIPS:
                continue
            aim = aim_at_target(src, victim, avail, world.initial_by_id, world.ang_vel, world=world)
            if aim is None:
                continue
            angle, turns = aim
            if turns > SEGMENT_MAX_TURNS:
                continue
            if deadline is not None and turns > deadline:
                continue
            solo.append((turns, src.id, src, angle, avail))

        if solo:
            solo.sort()  
            
            
            fired_solo = False
            last_fail = None
            for _t, src_id, src, _angle_est, avail in solo:
                send = min(avail, need)
                send = max(send, deficit + 1)
                if send < MIN_DISPATCH_SHIPS:
                    send = MIN_DISPATCH_SHIPS if avail >= MIN_DISPATCH_SHIPS else 0
                if send <= 0:
                    last_fail = "doomed-too-poor"
                    continue
                aim_final = aim_at_target(src, victim, send, world.initial_by_id, world.ang_vel, world=world)
                if aim_final is None:
                    last_fail = "doomed-aim-blocked"
                    continue
                angle, turns = aim_final
                if deadline is not None and turns > deadline:
                    last_fail = "doomed-too-slow"
                    continue
                
                
                if FWD_SIM_DEFENSE_CHECK and not world.is_2p:
                    proj = forward_project(
                        world,
                        our_capture_target=victim_id,
                        our_capture_turn=int(turns),
                        our_capture_ships=int(send),
                        horizon=FWD_SIM_HORIZON,
                        project_opponent_moves=True,
                        opponent_emit_fraction=0.30,
                    )
                    end_owner, _ = proj.get(victim_id, (-1, 0))
                    if end_owner != world.player:
                        last_fail = "fwd-sim-victim-still-lost"
                        continue
                _commit_fleet(world, moves, spent, target_locked,
                              src_id, victim_id, angle, turns, int(send))
                mode_log[victim_id] = "defended-by-solo"
                mode_log[src_id] = "defense"
                fired_solo = True
                break
            if fired_solo:
                continue
            if last_fail is not None:
                mode_log[victim_id] = last_fail
                

        if not COALITION_ENABLED:
            
            if _try_doom_evac(world, victim, available, spent, target_locked, moves, mode_log):
                continue
            mode_log[victim_id] = "doomed"
            continue
        coalition = _find_defense_coalition(
            world, victim, deadline, need, available, spent
        )
        if coalition is None:
            
            if _try_doom_evac(world, victim, available, spent, target_locked, moves, mode_log):
                continue
            mode_log[victim_id] = "doomed"
            continue
        for src_id, src, angle, ships, turns in coalition:
            _commit_fleet(world, moves, spent, target_locked,
                          src_id, victim_id, angle, turns, int(ships))
            mode_log[src_id] = "defense-coalition"
        mode_log[victim_id] = "defended-by-coalition"


def _try_doom_evac(world, victim, available, spent, target_locked, moves, mode_log):
    """V14.1b (Phase 3.2 V2): doomed planet evacuation.

    When rescue attempts have failed and the planet is about to flip, send
    its garrison to our highest-production friendly within reach. Preserves
    ships that would otherwise be captured. User-observed scenario: 40 garrison, 10+49 incoming â†' solo
    rescue would send a sub-need fleet and still lose; better to evac.

    V14.2 (Phase 3.6, Idea 5): attack-fallback. If no friendly destination,
    try sending the garrison to a winnable enemy/neutral target instead of
    letting the ships die with the planet. Prioritizes enemy planets in
    _enemy_recently_launched (they just emptied â†' weakly defended).
    """
    if not DOOM_EVAC_ENABLED:
        return False
    garrison = available[victim.id] - spent[victim.id]
    if garrison < DOOM_EVAC_MIN_SHIPS:
        return False

    
    friendly_candidates = []
    for dst in world.my_planets:
        if dst.id == victim.id:
            continue
        aim = aim_at_target(victim, dst, garrison, world.initial_by_id,
                            world.ang_vel, world=world)
        if aim is None:
            continue
        angle, turns = aim
        if turns > DOOM_EVAC_MAX_TRAVEL:
            continue
        
        
        score = int(dst.ships) + int(dst.production) * 5
        friendly_candidates.append((-score, int(turns), dst, angle))
    if friendly_candidates:
        friendly_candidates.sort()
        _score, turns, dst, angle = friendly_candidates[0]
        _commit_fleet(world, moves, spent, target_locked,
                      victim.id, dst.id, angle, turns, int(garrison))
        mode_log[victim.id] = "doom-evac-launched"
        mode_log[dst.id] = "doom-evac-recipient"
        return True

    
    if not DOOM_EVAC_ATTACK_FALLBACK_ENABLED:
        return False
    if DOOM_EVAC_ATTACK_FALLBACK_4P_ONLY and world.is_2p:
        return False
    attack_candidates = []
    for dst in world.planets:
        if dst.id == victim.id or dst.owner == world.player:
            continue
        if dst.id in target_locked:
            continue
        if not is_targetable(world, dst):
            continue
        aim = aim_at_target(victim, dst, garrison, world.initial_by_id,
                            world.ang_vel, world=world, check_approach=True)
        if aim is None:
            continue
        angle, turns = aim
        if turns > DOOM_EVAC_MAX_TRAVEL:
            continue
        
        
        is_enemy = dst.owner != -1
        prod = float(dst.production) if is_enemy else 0.0  # fractional rate
        arrival_garrison = float(dst.ships) + prod * int(turns)
        required = arrival_garrison + DOOM_EVAC_ATTACK_OVERKILL
        if int(garrison) < required:
            continue
        
        recently_launched_bonus = (
            -DOOM_EVAC_ATTACK_PREFER_LAUNCHED_BONUS
            if (is_enemy and dst.id in _enemy_recently_launched) else 0
        )
        rank = (
            recently_launched_bonus,
            -int(dst.production),
            int(turns),
            int(required),
        )
        attack_candidates.append((rank, dst, angle, turns))
    if not attack_candidates:
        return False
    attack_candidates.sort(key=lambda x: x[0])
    _rank, dst, angle, turns = attack_candidates[0]
    _commit_fleet(world, moves, spent, target_locked,
                  victim.id, dst.id, angle, turns, int(garrison))
    mode_log[victim.id] = "doom-evac-attack"
    mode_log[dst.id] = "doom-evac-attack-target"
    return True


def _find_defense_coalition(world, victim, deadline, need, available, spent):
    """Pick the closest pair of siblings whose combined ships meet `need`, both
    arrive by `deadline`, AND each contributes >= COALITION_MIN_PER_CONTRIBUTOR.
    Re-aims each contributor with its exact ship count.
    Returns [(src_id, src, angle, ships), ...] or None.
    """
    options = []
    for src in world.my_planets:
        if src.id == victim.id:
            continue
        avail = available[src.id] - spent[src.id]
        if avail < COALITION_MIN_PER_CONTRIBUTOR:
            continue
        aim = aim_at_target(src, victim, avail, world.initial_by_id, world.ang_vel, world=world)
        if aim is None:
            continue
        _angle_est, turns = aim
        if turns > SEGMENT_MAX_TURNS:
            continue
        if deadline is not None and turns > deadline:
            continue
        options.append((turns, src.id, src, avail))

    if len(options) < 2:
        return None
    options.sort()  

    for i in range(len(options)):
        for j in range(i + 1, len(options)):
            t_i, sid_i, s_i, a_i = options[i]
            t_j, sid_j, s_j, a_j = options[j]
            if a_i + a_j < need:
                continue
            ratio = a_i / float(a_i + a_j)
            ship_i = max(COALITION_MIN_PER_CONTRIBUTOR,
                         min(a_i, int(round(need * ratio))))
            ship_j = max(COALITION_MIN_PER_CONTRIBUTOR,
                  min(a_j, need - ship_i))
            while ship_i + ship_j < need:
                if ship_i < a_i:
                    ship_i += 1
                elif ship_j < a_j:
                    ship_j += 1
                else:
                    break
            if (ship_i + ship_j < need
                    or ship_i < COALITION_MIN_PER_CONTRIBUTOR
                    or ship_j < COALITION_MIN_PER_CONTRIBUTOR):
                continue
            
            aim_i = aim_at_target(s_i, victim, ship_i, world.initial_by_id, world.ang_vel, world=world)
            aim_j = aim_at_target(s_j, victim, ship_j, world.initial_by_id, world.ang_vel, world=world)
            if aim_i is None or aim_j is None:
                continue
            ang_i, turns_i = aim_i
            ang_j, turns_j = aim_j
            if (deadline is not None
                    and (turns_i > deadline or turns_j > deadline)):
                continue
            return [
                (sid_i, s_i, ang_i, ship_i, turns_i),
                (sid_j, s_j, ang_j, ship_j, turns_j),
            ]
    return None


def handle_comet_evac(world, available, spent, target_locked, moves, mode_log):
    """For each owned comet about to expire, send ALL its ships to the nearest
    non-comet friendly planet (or neutral fallback). Ships left on a comet
    that exits the system are lost permanently â€" evacuation preserves them.
    """
    if not world.comet_remaining:
        return
    
    own_non_comet = [p for p in world.my_planets if p.id not in world.comet_ids]
    if not own_non_comet:
        
        own_non_comet = [p for p in world.planets
                         if p.owner == -1 and p.id not in world.comet_ids]
        if not own_non_comet:
            return
    for src in world.my_planets:
        rem = world.comet_remaining.get(src.id)
        if rem is None or rem > COMET_EVAC_REMAINING_TURNS:
            continue
        if src.id in mode_log:
            continue
        avail = max(0, available[src.id] - spent.get(src.id, 0))
        if avail < COMET_EVAC_MIN_SHIPS:
            continue
        
        
        best = None
        best_d = float("inf")
        for dst in own_non_comet:
            if dst.id == src.id:
                continue
            d_now = dist(src.x, src.y, dst.x, dst.y)
            est_turns = max(1, int(math.ceil(d_now / fleet_speed(max(1, int(avail))))))
            dst_px, dst_py = predict_target_position(dst, world, est_turns)
            d = dist(src.x, src.y, dst_px, dst_py)
            if d < best_d:
                best_d = d
                best = dst
        if best is None:
            continue
        aim = aim_at_target(src, best, avail, world.initial_by_id, world.ang_vel, world=world)
        if aim is None:
            continue
        angle, turns = aim
        
        
        if turns >= rem:
            
            
            pass
        _commit_fleet(world, moves, spent, target_locked,
                      src.id, best.id, angle, turns, int(avail))
        mode_log[src.id] = "comet-evac"


def handle_comet_capture(world, available, spent, target_locked, moves, mode_log):
    """Grab neutral/enemy comets for their temporary +1/turn production, but only
    when we'd own one long enough to profit: ownership time (remaining life minus
    flight) must be >= COMET_CAPTURE_MIN_LIFE AND >= the capture cost (so the
    production we harvest beats the ships we spend). The existing comet-evac pulls
    those ships back off before the comet leaves the board."""
    if not world.comet_remaining:
        return
    comets = []
    for cid, rem in world.comet_remaining.items():
        if rem <= COMET_EVAC_REMAINING_TURNS or cid in target_locked:
            continue
        c = world.planet_by_id.get(cid)
        if c is None or c.owner == world.player:
            continue
        comets.append((c, rem))
    if not comets:
        return
    comets.sort(key=lambda cr: -cr[1])  # most life left first (most to harvest)
    for c, rem in comets:
        if c.id in target_locked:
            continue
        for src in sorted(world.my_planets, key=lambda p: dist(p.x, p.y, c.x, c.y)):
            if mode_log.get(src.id):
                continue
            keep = _safe_reserve(world, src)
            spare = (available[src.id] - spent[src.id]) - keep
            if spare < MIN_DISPATCH_SHIPS:
                continue
            aim = aim_at_target(src, c, spare, world.initial_by_id, world.ang_vel, world=world)
            if aim is None:
                continue
            _a0, turns0 = aim
            need = effective_needed_to_capture(c, turns0, world)
            ownership = rem - int(turns0)
            if ownership < COMET_CAPTURE_MIN_LIFE or ownership < need:
                continue  # not enough ownership time to profit
            send = max(MIN_DISPATCH_SHIPS, need)
            if spare < send:
                continue
            re_aim = aim_at_target(src, c, send, world.initial_by_id, world.ang_vel, world=world)
            if re_aim is None:
                continue
            angle, turns = re_aim
            _commit_fleet(world, moves, spent, target_locked,
                          src.id, c.id, angle, turns, int(send))
            mode_log[src.id] = "comet-capture"
            mode_log[c.id] = "comet-capture-target"
            break


def _handle_search_expand_4p(world, available, spent, target_locked, moves, mode_log):
    """V12.9 Melis search-based expansion (4P only). Generates candidate step
    actions via generate_step_actions, ranks by melis_evaluate gain, commits
    top SEARCH_MAX_ACTIONS_TO_PICK that don't conflict (different targets +
    sources). Returns list of committed source ids so caller can skip them.
    """
    max_to_pick = SEARCH_MAX_ACTIONS_TO_PICK_2P if world.is_2p else SEARCH_MAX_ACTIONS_TO_PICK
    actions = search_step_action(
        world, max_per_source=SEARCH_MAX_PER_SOURCE,
        max_actions_to_eval=30,
        use_depth2=SEARCH_DEPTH2_ENABLED,
    )
    committed_sources = set()
    committed_targets = set()
    for act in actions[:max_to_pick * 2]:
        if act["score"] <= 0:
            continue
        src_id = act["source_id"]
        tgt_id = act["target_id"]
        if src_id in committed_sources or tgt_id in committed_targets:
            continue
        if tgt_id in target_locked:
            continue
        
        src_status = mode_log.get(src_id)
        if src_status == "brain-reserved-lead":
            continue
        avail = available[src_id] - spent[src_id]
        if avail < act["ships"]:
            continue
        
        
        tgt = world.planet_by_id.get(tgt_id)
        
        if (world.stop_expanding_2p or world.prod_lead_stop_expand_4p or world.turn_cutoff_stop_expand) and tgt is not None and tgt.owner == -1:
            continue
        
        if world.stop_expand_lax and tgt is not None and tgt.owner == -1:
            continue
        if tgt is not None and tgt.owner == -1:
            turns_act = int(act["arrival_turn"])
            ships_act = int(act["ships"])
            if not _capture_holds_against_snipe(world, tgt, turns_act, ships_act):
                continue
            if not _endgame_roi_ok(world, tgt, ships_act, turns_act):
                continue
            if not _neutral_tempo_ok(world, tgt, ships_act, turns_act):
                continue
        _commit_fleet(world, moves, spent, target_locked,
                      src_id, tgt_id, act["angle"], act["arrival_turn"], act["ships"])
        mode_log[src_id] = "search-expand"
        committed_sources.add(src_id)
        committed_targets.add(tgt_id)
        if len(committed_sources) >= max_to_pick:
            break
    return committed_sources


def _home_zone_clear(world):
    """Return True if no enemy/neutral planets exist inside our home zone."""
    if world.home_center is None:
        return True
    hx, hy = world.home_center
    dist_limit = HOME_RETURN_DIST_2P if world.is_2p else HOME_RETURN_DIST_4P
    for p in world.planets:
        if p.owner == world.player:
            continue
        if dist(p.x, p.y, hx, hy) <= dist_limit:
            return False
    return True


def _effective_target_dist(src, tgt, world):
    """V12.4a rotation-aware distance proxy for target prefilter ranking.

    Predicts target position at expected travel time and returns distance
    to that future position. Static planets unchanged. Orbital planets
    rotating toward us get a shorter effective distance (promote);
    rotating away get longer (demote). One-step approximation â€" cheap;
    real arrival is computed later by aim_at_target inside plan_solo_capture.
    Affects WHICH targets get inspected when K is small, not which fleets fly.
    """
    raw = dist(src.x, src.y, tgt.x, tgt.y)
    if not ROT_AWARE_RANK_ENABLED:
        return raw
    init = world.initial_by_id.get(tgt.id)
    if init is None:
        return raw
    if _init_is_static(init):
        return raw
    speed = fleet_speed(50)
    travel = max(1, int(math.ceil(raw / speed)))
    if travel > 60:
        return raw
    px, py = predict_planet_position(tgt, world.initial_by_id, world.ang_vel, travel)
    return dist(src.x, src.y, px, py)


def _score_target(src, tgt, world):
    """Score a target 0-30 using three equal-weight criteria (0-10 each):
    1. Distance/position: closer is better; bonus if static in home zone or
       rotating planet enters home zone within 5 turns.
    2. Production: higher is better.
    3. Cost: lower garrison is better (cheaper to capture).
    """
    # --- 1. Distance / position score (0-10) ---
    eff_dist = _effective_target_dist(src, tgt, world)
    # Normalize: 0 units = 10pts, SEGMENT_MAX_TURNS*MAX_SPEED units = 0pts
    max_dist = float(SEGMENT_MAX_TURNS * MAX_SPEED)
    dist_score = max(0.0, 10.0 * (1.0 - eff_dist / max_dist))

    # Position bonus: static planet inside home zone (+3)
    # OR rotating planet that will enter home zone within 5 turns (+3)
    if world.home_center is not None:
        hx, hy = world.home_center
        dlimit = HOME_RETURN_DIST_2P if world.is_2p else HOME_RETURN_DIST_4P
        init = world.initial_by_id.get(tgt.id)
        is_static = (init is not None and
                     _init_is_static(init))
        if is_static:
            if dist(tgt.x, tgt.y, hx, hy) <= dlimit:
                dist_score = min(10.0, dist_score + 3.0)
        else:
            for t in range(1, 6):
                px, py = predict_planet_position(tgt, world.initial_by_id, world.ang_vel, t)
                if dist(px, py, hx, hy) <= dlimit:
                    dist_score = min(10.0, dist_score + 3.0)
                    break

    # --- 2. Production score (0-10) ---
    prod_score = min(10.0, float(int(tgt.production)) * 2.0)

    # --- 3. Cost score (0-10): lower garrison = higher score ---
    garrison = int(tgt.ships)
    max_garrison = max(1, ATTACK_MAX_SHIPS - 1)
    cost_score = max(0.0, 10.0 * (1.0 - garrison / max_garrison))

    # Before turn 50: no direction score (pure land grab)
    if world.step < 50:
        if world.step < EARLY_GAME_TURNS:
            return dist_score * 4 + prod_score * 3 + cost_score * 4
        return dist_score + prod_score + cost_score

    # --- 4. Direction score: static 8, against-flow 10, chasing 3 ---
    init = world.initial_by_id.get(tgt.id)
    if init is not None and _init_is_static(init):
        dir_score = 8.0   # static: no chasing concern
    elif is_in_approaching_direction(src, tgt, world.ang_vel):
        dir_score = 10.0  # approaching (against flow): best
    else:
        dir_score = 3.0   # would chase the target

    # Early game weighting: distance x4, production x3, cost x4, direction x4
    if world.step < EARLY_GAME_TURNS:
        return dist_score * 4 + prod_score * 3 + cost_score * 4 + dir_score * 4

    # Mid/late: production matters MORE than early — weight it x6.
    # Interior priority: favour capturing inside our anchored quadrants, mildly
    # avoid reaching outside (clear weakened enemies are handled separately by the
    # unrestricted opportunistic-attack pass, so good chances outside are still taken).
    interior = 0.0
    if _parent_quads:
        interior = (INTERIOR_CAPTURE_BONUS if _get_quadrant(tgt) in _parent_quads
                    else -INTERIOR_OUTSIDE_PENALTY)
    return dist_score * 4 + prod_score * 6 + cost_score * 4 + dir_score * 4 + interior


def _counter_snipe_candidates(world, src, max_travel, target_locked):
    """V12.4c: neutrals where a known enemy fleet will capture before us, and
    we can re-flip cheaply on a short follow-up. Returns [(target, raw_dist)]
    sorted by re-flip cost ascending. 2P-only â€" see COUNTER_SNIPE_2P_ONLY note.
    """
    if not COUNTER_SNIPE_ENABLED:
        return []
    if COUNTER_SNIPE_2P_ONLY and not world.is_2p:
        return []
    out = []
    for n in world.neutral_planets:
        if n.id in target_locked:
            continue
        if not is_targetable(world, n):
            continue
        enemy_eta = None
        enemy_remaining = None
        needed = int(n.ships) + 1
        for eta, owner, ships in world.arrivals_by_planet.get(n.id, []):
            if owner == world.player or owner == -1:
                continue
            if ships < needed:
                continue
            if enemy_eta is None or eta < enemy_eta:
                enemy_eta = int(eta)
                enemy_remaining = ships - int(n.ships)
        if enemy_eta is None:
            continue
        d = dist(src.x, src.y, n.x, n.y)
        speed = fleet_speed(50)
        my_eta_est = max(1, int(math.ceil(d / speed)))
        if my_eta_est > max_travel + 4:
            continue
        delay = my_eta_est - enemy_eta
        if delay < COUNTER_SNIPE_MIN_DELAY or delay > COUNTER_SNIPE_MAX_DELAY:
            continue
        prod = max(0.0, float(n.production))  # fractional production rate
        defender_at_my_arrival = max(0, int(enemy_remaining)) + prod * delay
        flip_cost = int(math.floor(defender_at_my_arrival)) + 1
        if flip_cost > COUNTER_SNIPE_MAX_COST:
            continue
        out.append((flip_cost, n, d))
    out.sort(key=lambda kv: kv[0])
    return [(n, d) for _cost, n, d in out]


def _plan_counter_snipe(world, src, tgt, max_avail, max_travel):
    """V12.4c: size a small fleet to re-flip a neutral AFTER a known enemy
    fleet captures it. Returns (angle, turns, ships) or None. 2P-only.
    """
    if not COUNTER_SNIPE_ENABLED or tgt.owner != -1:
        return None
    if COUNTER_SNIPE_2P_ONLY and not world.is_2p:
        return None
    if max_avail < MIN_DISPATCH_SHIPS:
        return None
    enemy_eta = None
    enemy_remaining = None
    needed_to_take = int(tgt.ships) + 1
    for eta, owner, ships in world.arrivals_by_planet.get(tgt.id, []):
        if owner == world.player or owner == -1:
            continue
        if ships < needed_to_take:
            continue
        if enemy_eta is None or eta < enemy_eta:
            enemy_eta = int(eta)
            enemy_remaining = ships - int(tgt.ships)
    if enemy_eta is None:
        return None

    aim = aim_at_target(src, tgt, max_avail, world.initial_by_id, world.ang_vel, world=world)
    if aim is None:
        return None
    angle, turns = aim
    if turns > max_travel:
        return None
    delay = turns - enemy_eta
    if delay < COUNTER_SNIPE_MIN_DELAY or delay > COUNTER_SNIPE_MAX_DELAY:
        return None
    prod = max(0.0, float(tgt.production))  # fractional production rate
    defender = max(0, int(enemy_remaining)) + prod * delay
    ships = max(MIN_DISPATCH_SHIPS, int(math.floor(defender)) + 1)
    if ships > max_avail or ships > COUNTER_SNIPE_MAX_COST:
        return None
    aim2 = aim_at_target(src, tgt, ships, world.initial_by_id, world.ang_vel, world=world)
    if aim2 is None:
        return None
    angle, turns = aim2
    if turns > max_travel:
        return None
    delay2 = turns - enemy_eta
    if delay2 < COUNTER_SNIPE_MIN_DELAY or delay2 > COUNTER_SNIPE_MAX_DELAY:
        return None
    defender2 = max(0, int(enemy_remaining)) + prod * delay2
    if ships < int(math.floor(defender2)) + 1:
        ships = int(math.floor(defender2)) + 1
        if ships > max_avail or ships > COUNTER_SNIPE_MAX_COST:
            return None
        aim3 = aim_at_target(src, tgt, ships, world.initial_by_id, world.ang_vel, world=world)
        if aim3 is None:
            return None
        angle, turns = aim3
        if turns > max_travel:
            return None
    return angle, turns, int(ships)


def _capture_holds_against_snipe(world, target, arrival_turn, ships_sent):
    """V12.4b: returns True if our post-capture garrison stays >0 through every
    KNOWN enemy fleet arriving within ANTI_SNIPE_HORIZON. Walks surplus +
    production growth between events; subtracts each enemy fleet at its eta;
    refuses if balance ever drops <=0. Friendly follow-ups credited.

    Gated to 2P only (ANTI_SNIPE_2P_ONLY): in 4P with 3 enemies the veto
    fires too often, starving expansion (192-game test: 55 third-place
    finishes vs 12_4a's 4). 2P has only one snipe source so the veto
    targets actual snipe traps without paralyzing expansion.
    """
    if not ANTI_SNIPE_ENABLED:
        return True
    if ANTI_SNIPE_2P_ONLY and not world.is_2p:
        return True
    if target.owner != -1:
        return True
    arrivals = world.arrivals_by_planet.get(target.id, [])
    enemy_after = []
    friendly_after = []
    for eta, owner, ships in arrivals:
        if ships <= 0:
            continue
        if eta <= arrival_turn:
            continue
        if eta - arrival_turn > ANTI_SNIPE_HORIZON:
            continue
        if owner == world.player:
            friendly_after.append((eta, ships))
        elif owner != -1:
            enemy_after.append((eta, ships))

    
    if REACTIVE_SNIPE_PROJECTION_ENABLED:
        for enemy_p in world.enemy_planets:
            e_ships = int(enemy_p.ships)
            if e_ships < REACTIVE_MIN_ENEMY_SHIPS:
                continue
            
            
            if SUN_SHADOW_REACTIVE_FILTER and not world.is_2p and segment_hits_sun(
                enemy_p.x, enemy_p.y, target.x, target.y
            ):
                continue
            d = dist(enemy_p.x, enemy_p.y, target.x, target.y)
            projected_force = max(REACTIVE_MIN_PROJECTED, int(e_ships * REACTIVE_EMIT_FRAC))
            speed = fleet_speed(projected_force)
            travel = max(1, int(math.ceil(d / speed)))
            
            snipe_eta = travel
            if snipe_eta <= arrival_turn:
                continue  
            if snipe_eta - arrival_turn > ANTI_SNIPE_HORIZON:
                continue
            enemy_after.append((snipe_eta, projected_force))

    if not enemy_after:
        return True

    
    if N6_USE_EFFECTIVE_PRE_GARRISON:
        _, pre_garrison = effective_garrison_at_arrival(target, arrival_turn, world)
    else:
        pre_garrison = garrison_at_arrival(target, arrival_turn)
    if ships_sent <= pre_garrison:
        return True
    surplus = ships_sent - pre_garrison
    prod = max(0.0, float(target.production))  # fractional production rate
    by_turn = defaultdict(int)
    for eta, ships in enemy_after:
        by_turn[eta] -= ships
    for eta, ships in friendly_after:
        by_turn[eta] += ships

    bal = surplus
    last_t = arrival_turn
    for eta in sorted(by_turn):
        bal += prod * (eta - last_t)
        bal += by_turn[eta]
        if bal <= 0:
            return False
        last_t = eta
    return True


def _tiebreak_hash(world, src_id, target_id):
    """Deterministic, replayable hash for breaking near-equal-distance ties.
    salts on (player, step, src, target) so different turns / sources don't
    produce identical perturbations. Multiplicative mix instead of Python's
    hash() because PYTHONHASHSEED randomizes hash() across processes."""
    h = (int(world.player) * 2654435761) & 0xFFFFFFFF
    h ^= (int(world.step) * 1664525) & 0xFFFFFFFF
    h ^= (int(src_id) * 16777619) & 0xFFFFFFFF
    h ^= (int(target_id) * 2246822519) & 0xFFFFFFFF
    return h & 0xFFFF


def _nearest_targets(src, world, K, max_travel, target_locked):
    """Top-K nearest non-friendly, non-comet planets, plus any race-winnable
    contested neutrals appended at the FRONT regardless of K (V12.1a).

    Final travel-time and capture cost happen inside plan_solo_capture; the
    race-loss skip in handle_expand vetoes any target where we'd arrive after
    the enemy.

    V12.3c5 (2.5): in 2P, near-equal-distance candidates (within
    TIEBREAK_EPS_FRAC of best) are reordered by a deterministic
    (player, step, src, target) hash. Cracks symmetric-Nash mirror lock
    where two PATIENT bots otherwise pick the same target deterministically.
    Replayable via hash construction.
    """
    
    
    _f31_has_better = (
        world.is_2p
        and EXPAND_MIN_PROD_2P >= 2
        and any(int(n.production) >= EXPAND_MIN_PROD_2P for n in world.neutral_planets
                if n.id not in target_locked)
    )
    candidates = []
    for t in world.planets:
        if t.owner == world.player:
            continue
        if t.id in target_locked:
            continue
        if not is_targetable(world, t):
            continue
        if _neutral_blocked_by_cap(world, t):
            continue
        
        if _f31_has_better and t.owner == -1 and int(t.production) < EXPAND_MIN_PROD_2P:
            continue
        
        
        raw = dist(src.x, src.y, t.x, t.y)
        if raw / MAX_SPEED > max_travel + 4:
            continue
        eff = _effective_target_dist(src, t, world)
        
        
        weight = VALUE_WEIGHT_2P if world.is_2p else VALUE_WEIGHT_4P
        weighted = eff - max(0, int(t.production)) * weight
        
        
        if F1B_EXPAND_BONUS_ENABLED and t.owner != world.player and t.owner != -1:
            if t.id in _enemy_recently_launched:
                weighted -= F1B_EXPAND_BONUS
        
        
        if SO1_STATIC_PREFERENCE_ENABLED:
            init_t = world.initial_by_id.get(t.id)
            if init_t is not None:
                r_t = dist(init_t.x, init_t.y, CENTER_X, CENTER_Y)
                if r_t + init_t.radius >= ROTATION_LIMIT:
                    weighted -= SO1_STATIC_BONUS
        
        
        if (
            LEADER_BASH_ENABLED
            and not world.is_2p
            and world.contest_leader
            and world.step >= LEADER_BASH_MIN_STEP
            and world.leader_id is not None
            and t.owner == world.leader_id
        ):
            weighted -= LEADER_BASH_BONUS
        
        
        if (
            not world.is_2p
            and t.owner != -1
            and t.owner != world.player
            and world.opp_profile
            and t.owner in world.opp_profile
        ):
            prof = world.opp_profile[t.owner]
            if len(prof["emit"]) >= 5:
                avg_emit = sum(prof["emit"]) / len(prof["emit"])
                if avg_emit > 0.35:
                    weighted -= 5.0  
        
        
        if (
            WEAKEST_TARGET_ENABLED
            and not world.is_2p
            and world.step >= WEAKEST_TARGET_MIN_STEP
            and world.mode == "pressure"
            and world.weakest_enemy is not None
            and t.owner == world.weakest_enemy
        ):
            if world.weakest_enemy_prod_share < WEAKEST_DONT_FINISH_SHARE:
                weighted += WEAKEST_DONT_FINISH_PENALTY
            else:
                weighted -= WEAKEST_TARGET_BONUS
        
        if (
            F14_4A_2P_FOCUS_ENABLED
            and world.is_2p
            and world.focus_enemy_2p is not None
            and t.owner == world.focus_enemy_2p
        ):
            weighted -= F14_4A_2P_FOCUS_DIST_BONUS
        
        if R1_RECAPTURE_PRIORITY_ENABLED and t.id in _freshly_lost_planets:
            weighted -= R1_RECAPTURE_HAMMER_BONUS * 1.5

        # Idea 6: strongly prioritize neutrals the enemy is about to capture
        if t.owner == -1 and RACE_ENABLED:
            enemy_eta = world.enemy_race_eta.get(t.id)
            if enemy_eta is not None and enemy_eta <= 5:
                weighted -= 15.0  # urgent: enemy is very close

        if not world.home_sector_defined:
            home_penalty = 0.0
        else:
            home_penalty = world.home_penalty(t)
        if home_penalty > 0:
            weighted += home_penalty

        candidates.append((t, weighted, raw))
    if not candidates:
        return []
    candidates.sort(key=lambda kv: kv[1])
    
    
    if (FWD_SIM_RANK_BONUS_4P > 0 and not world.is_2p and len(candidates) > 1):
        baseline_proj = forward_project(
            world, horizon=FWD_SIM_HORIZON,
            project_opponent_moves=True, opponent_emit_fraction=0.30
        )
        baseline_score = forward_score(baseline_proj, world.player, 4, world)
        rerank = []
        topN = min(K + 2, len(candidates))
        for idx, (t, w, raw) in enumerate(candidates[:topN]):
            est_eta = max(1, int(math.ceil(raw / MAX_SPEED)))
            est_ships = needed_to_capture(t, est_eta) + 1
            proj = forward_project(
                world, our_capture_target=t.id, our_capture_turn=est_eta,
                our_capture_ships=est_ships, horizon=FWD_SIM_HORIZON,
                project_opponent_moves=True, opponent_emit_fraction=0.30
            )
            score_gain = forward_score(proj, world.player, 4, world) - baseline_score
            adjusted = w - FWD_SIM_RANK_BONUS_4P * score_gain
            rerank.append((t, adjusted, raw))
        candidates = rerank + candidates[topN:]
        candidates.sort(key=lambda kv: kv[1])
    if world.is_2p and TIEBREAK_ENABLED and len(candidates) > 1:
        best_d = candidates[0][1]
        eps = max(TIEBREAK_EPS_MIN, TIEBREAK_EPS_FRAC * best_d)
        def _k(kv):
            tgt, weighted_d, _raw = kv
            bucket = int(weighted_d / eps) if eps > 0 else 0
            return (bucket, _tiebreak_hash(world, src.id, tgt.id), weighted_d)
        candidates.sort(key=_k)

    counter_snipe = _counter_snipe_candidates(world, src, max_travel, target_locked)

    if not RACE_ENABLED or not world.enemy_race_eta:
        head = counter_snipe + [(t, raw) for t, _eff, raw in candidates[:K]]
        return _dedupe_targets(head)

    race_priority = []
    normal = []
    for t, _eff, raw in candidates:
        enemy_eta = world.enemy_race_eta.get(t.id)
        if enemy_eta is None or t.owner != -1:
            normal.append((t, raw))
            continue
        my_min = max(1, int(math.ceil(raw / fleet_speed(max(1, int(src.ships))))))
        if my_min <= enemy_eta:
            race_priority.append((t, raw))
        else:
            normal.append((t, raw))

    return _dedupe_targets(counter_snipe + race_priority + normal[:K])


def _dedupe_targets(seq):
    """V12.4c: preserve order, drop duplicates by target id (counter-snipe and
    race-priority can overlap with the K window)."""
    seen = set()
    out = []
    for tgt, d in seq:
        if tgt.id in seen:
            continue
        seen.add(tgt.id)
        out.append((tgt, d))
    return out


def _try_coalition_expand(world, src, tgt, max_travel, available, spent,
                          target_locked, moves, mode_log):
    """src can't take tgt alone; find a partner whose combined ships flip it.
    Each contributor must send >= COALITION_MIN_PER_CONTRIBUTOR (no tiny
    pieces). For tiny targets we DON'T split â€" the patient ethos prefers
    waiting for a solo fleet over showering a small target with two halves.
    """
    src_avail = available[src.id] - spent[src.id]
    if src_avail < COALITION_MIN_PER_CONTRIBUTOR:
        return False
    
    
    if int(tgt.ships) < COALITION_MIN_TARGET_SHIPS:
        return False

    
    partners = []
    for p in world.my_planets:
        if p.id == src.id:
            continue
        avail = available[p.id] - spent[p.id]
        if avail < COALITION_MIN_PER_CONTRIBUTOR:
            continue
        if not is_in_approaching_direction(p, tgt, world.ang_vel):
            continue
        est = aim_at_target(p, tgt, avail, world.initial_by_id, world.ang_vel, world=world)
        if est is None:
            continue
        _, est_turns = est
        if est_turns > max_travel:
            continue
        partners.append((est_turns, p, avail))
    if not partners:
        return False
    partners.sort(key=lambda kv: kv[0])

    
    for est_turns, p, p_avail in partners:
        combined = src_avail + p_avail
        
        
        est_src = aim_at_target(src, tgt, src_avail, world.initial_by_id, world.ang_vel, world=world)
        if est_src is None:
            continue
        worst = max(est_src[1], est_turns)
        total_needed = needed_to_capture(tgt, worst)
        if combined < total_needed:
            continue

        
        ratio = src_avail / float(combined)
        s_src = max(COALITION_MIN_PER_CONTRIBUTOR,
                    min(src_avail, int(round(total_needed * ratio))))
        s_p = max(COALITION_MIN_PER_CONTRIBUTOR,
                  min(p_avail, total_needed - s_src))
        while s_src + s_p < total_needed:
            if s_src < a_i:
                s_src += 1
            elif s_p < p_avail:
                s_p += 1
            else:
                break
        if s_src + s_p < total_needed:
            continue
        if s_src < COALITION_MIN_PER_CONTRIBUTOR or s_p < COALITION_MIN_PER_CONTRIBUTOR:
            continue
        if s_src > src_avail or s_p > p_avail:
            continue

        
        aim_src = aim_at_target(src, tgt, s_src, world.initial_by_id, world.ang_vel,
                               world=world, check_approach=True)
        aim_p = aim_at_target(p, tgt, s_p, world.initial_by_id, world.ang_vel,
                              world=world, check_approach=True)
        if aim_src is None or aim_p is None:
            continue
        a_src, t_src = aim_src
        a_p, t_p = aim_p
        if t_src > max_travel or t_p > max_travel:
            continue

        
        if world.is_2p and abs(t_src - t_p) > 1:
            continue

        
        post_eta = max(t_src, t_p)
        post_needed = needed_to_capture(tgt, post_eta)
        if s_src + s_p < post_needed:
            continue

        _commit_fleet(world, moves, spent, target_locked,
                      src.id, tgt.id, a_src, t_src, int(s_src))
        _commit_fleet(world, moves, spent, target_locked,
                      p.id, tgt.id, a_p, t_p, int(s_p))
        mode_log[src.id] = "expand-coalition"
        mode_log[p.id] = "expand-coalition"
        return True

    return False


def _get_quadrant(planet):
    """Return 0-3: NW=0, SW=1, NE=2, SE=3."""
    return _get_quadrant_from_pos(planet.x, planet.y)


# Clockwise rotation: SE(3)→NE(2)→NW(0)→SW(1)→SE(3)
_CW_NEXT  = {3: 2, 2: 0, 0: 1, 1: 3}
# Counter-clockwise: SE(3)→SW(1)→NW(0)→NE(2)→SE(3)
_CCW_NEXT = {3: 1, 1: 0, 0: 2, 2: 3}


def _frontier_quadrant(q, ang_vel):
    """One step ahead in the rotation direction = the frontier."""
    if abs(ang_vel) < 1e-9:
        return q
    return _CW_NEXT[q] if ang_vel < 0 else _CCW_NEXT[q]


def _incoming_enemy(world, planet_id):
    """Total hostile ships currently inbound to this planet, plus the earliest
    hostile ETA. Returns (total, earliest_eta) — earliest_eta is None if none."""
    total = 0
    earliest = None
    for eta, owner, ships in world.arrivals_by_planet.get(planet_id, []):
        if owner != world.player and owner != -1 and ships > 0:
            total += int(ships)
            if earliest is None or eta < earliest:
                earliest = int(eta)
    return total, earliest


def _incoming_friendly(world, planet_id):
    """Total friendly ships currently inbound to this planet."""
    return sum(
        int(ships) for eta, owner, ships in world.arrivals_by_planet.get(planet_id, [])
        if owner == world.player and ships > 0
    )


def _safe_reserve(world, planet):
    """Ships to keep so the planet survives incoming enemy.
    = enemy_in - own_production_by_first_hit - friendly_in + 1, floored at 0.
    """
    enemy_in, eta = _incoming_enemy(world, planet.id)
    if enemy_in <= 0:
        return 0
    # Fractional production rate; floor the gain so we never under-reserve.
    prod_gain = int(math.floor(float(planet.production) * int(eta))) if eta else 0
    friendly_in = _incoming_friendly(world, planet.id)
    return max(0, enemy_in - prod_gain - friendly_in + 1)


def _threatened_planets(world):
    """Our planets where incoming enemy beats our defense (garrison + production
    buffer + inbound friendly reinforcements) by THREAT_RATIO. Sorted by what we
    stand to lose, most valuable first: production (a high-output planet hurts
    most to lose), then how badly it is being overwhelmed."""
    out = []
    for p in world.my_planets:
        enemy_in, eta = _incoming_enemy(world, p.id)
        if enemy_in <= 0:
            continue
        friendly_in = _incoming_friendly(world, p.id)
        defense = float(p.ships) + float(p.production) * 2 + friendly_in
        if enemy_in > defense * THREAT_RATIO:
            out.append((p, enemy_in - defense))
    out.sort(key=lambda pe: (-float(pe[0].production), -pe[1]))
    return [p for p, _overshoot in out]


def _roi_ok(world, target, turns):
    """Late game only: skip neutral targets whose production is too low to be
    worth the ships (production over remaining turns must beat the cost)."""
    if world.step < EARLY_GAME_TURNS:
        return True
    if target.owner != -1:
        return True  # enemy targets always worth it
    return int(target.production) >= ROI_MIN_PROD


RELAY_TRIGGER_TURNS = 5        # direct ETA above this -> try relaying
RELAY_MAX_RATIO = 1.5          # relay only if total time <= direct * this


def _resolve_relay(world, src, tgt, ships):
    """Return the planet to actually fire at: either a relay (a friendly planet
    closer to tgt that shortens each hop) or tgt itself.

    Relay when direct ETA > RELAY_TRIGGER_TURNS and a friendly relay exists whose
    (src->relay) + 1 + (relay->tgt) <= direct * RATIO. Far targets relay even if
    static — consolidates ships forward and keeps fleets big (=faster). Short
    shots go direct. Returns (dest_planet, aim) for src->dest, or None.
    """
    direct = aim_at_target(src, tgt, ships, world.initial_by_id,
                           world.ang_vel, world=world, check_approach=True)
    if direct is None:
        return None, None
    _, direct_eta = direct
    if direct_eta <= RELAY_TRIGGER_TURNS:
        return tgt, direct  # already close -> direct

    best_relay = None
    best_total = direct_eta * RELAY_MAX_RATIO
    for rp in world.my_planets:
        if rp.id == src.id or rp.id == tgt.id:
            continue
        # relay must be meaningfully closer to the target
        if dist(rp.x, rp.y, tgt.x, tgt.y) >= dist(src.x, src.y, tgt.x, tgt.y):
            continue
        a1 = aim_at_target(src, rp, ships, world.initial_by_id,
                           world.ang_vel, world=world)
        if a1 is None:
            continue
        _, eta1 = a1
        if eta1 > RELAY_TRIGGER_TURNS:
            continue  # first hop itself should be short
        a2 = aim_at_target(rp, tgt, ships, world.initial_by_id,
                           world.ang_vel, world=world)
        if a2 is None:
            continue
        _, eta2 = a2
        total = eta1 + 1 + eta2  # +1 turnaround at the relay
        if total <= best_total:
            best_total = total
            best_relay = (rp, a1)
    if best_relay is not None:
        return best_relay[0], best_relay[1]
    return tgt, direct  # no good relay -> direct (option B)


def _standing(world):
    """Are we winning? Combined lead vs the strongest opponent, production-weighted.
    Returns 'winning', 'even', or 'losing'."""
    pid = world.player
    def _lead(getter, total):
        mine = getter(pid)
        best_enemy = 0
        for o in world.owner_production.keys():
            if o in (-1, pid):
                continue
            best_enemy = max(best_enemy, getter(o))
        return (mine - best_enemy) / max(total, 1)

    total_prod = max(1, world.total_prod)
    total_fleet = max(1, sum(world.owner_strength.values()))
    total_planets = max(1, sum(world.owner_planet_count.values()))
    prod_lead = _lead(lambda o: world.owner_production.get(o, 0), total_prod)
    fleet_lead = _lead(lambda o: world.owner_strength.get(o, 0), total_fleet)
    planet_lead = _lead(lambda o: world.owner_planet_count.get(o, 0), total_planets)
    lead = 0.5 * prod_lead + 0.25 * fleet_lead + 0.25 * planet_lead
    if lead > 0.10:
        return "winning"
    if lead < -0.10:
        return "losing"
    return "even"


def _fwd_rerank(world, src, candidates, baseline, budget, gain_floor=0.0):
    """Level-2 lookahead: re-rank the top-K candidates by board forward-sim gain.

    For each of the top-K (by _score_target) candidates, estimate a capture and
    measure how much the whole-board projected score improves vs `baseline`.
    Keeps only candidates with positive gain (drops captures that get retaken),
    sorted by gain desc, then appends the untouched tail. `budget` is a mutable
    [int] capping total forward-sims this turn. Falls back to the input order
    on any error or exhausted budget.
    """
    if not FWD_LOOKAHEAD_ENABLED or baseline is None or budget[0] <= 0:
        return candidates
    head = candidates[:FWD_LOOKAHEAD_TOPK]
    tail = candidates[FWD_LOOKAHEAD_TOPK:]
    scored = []
    for tgt in head:
        if budget[0] <= 0:
            scored.append((0.0, tgt))
            continue
        # provisional eta via a quick aim with the needed ships
        need = effective_needed_to_capture(tgt, 1, world)
        aim = aim_at_target(src, tgt, max(1, int(need)), world.initial_by_id,
                            world.ang_vel, world=world)
        if aim is None:
            continue  # unreachable -> drop
        _, eta = aim
        ships = effective_needed_to_capture(tgt, int(eta), world)
        try:
            action = {"target_id": int(tgt.id), "arrival_turn": int(eta),
                      "ships": int(ships)}
            gain = o_melis_evaluate(world, our_step_action=action) - baseline
            budget[0] -= 1
        except Exception:
            return candidates  # fall back on any incompatibility
        if gain > gain_floor:
            scored.append((gain, tgt))
    scored.sort(key=lambda gt: -gt[0])
    return [t for _g, t in scored] + tail


def _build_circuit(planets, world):
    """Build a greedy nearest-neighbor tour through the given planets.
    Returns list of planet IDs.
    """
    if not planets:
        return []
    remaining = list(planets)
    first = remaining.pop(0)
    circuit = [first.id]
    while remaining:
        last_p = world.planet_by_id[circuit[-1]]
        nearest = min(remaining, key=lambda p: dist(p.x, p.y, last_p.x, last_p.y))
        circuit.append(nearest.id)
        remaining.remove(nearest)
    return circuit


def handle_intercept(world, available, spent, target_locked, moves, mode_log):
    """Idea 3: when an enemy fleet is heading to one of our planets, attack the
    source planet while its garrison is thin (they just launched from there).
    """
    attacked = set()
    for pid, arrivals in world.arrivals_by_planet.items():
        p = world.planet_by_id.get(pid)
        if p is None or p.owner != world.player:
            continue
        for _eta, owner, ships in arrivals:
            if owner == world.player or owner == -1 or ships <= 0:
                continue
            # Find the enemy fleet(s) heading here and their source planet
            for f in world.fleets:
                if f.owner != owner:
                    continue
                src_planet = world.planet_by_id.get(int(f.from_planet_id))
                if src_planet is None or src_planet.owner != owner:
                    continue
                if src_planet.id in attacked or src_planet.id in target_locked:
                    continue
                # Attack the weakened source planet from our nearest planet
                for my_p in sorted(world.my_planets,
                                   key=lambda mp: dist(mp.x, mp.y, src_planet.x, src_planet.y)):
                    avail = available[my_p.id] - spent[my_p.id]
                    need = int(src_planet.ships) + 1
                    send = max(MIN_DISPATCH_SHIPS, min(need, ATTACK_MAX_SHIPS))
                    if avail < send or need > ATTACK_MAX_SHIPS:
                        continue
                    if not is_in_approaching_direction(my_p, src_planet, world.ang_vel):
                        continue
                    aim = aim_at_target(my_p, src_planet, send, world.initial_by_id,
                                        world.ang_vel, world=world, check_approach=True)
                    if aim is None:
                        continue
                    angle, turns = aim
                    _commit_fleet(world, moves, spent, target_locked,
                                  my_p.id, src_planet.id, angle, turns, int(send))
                    mode_log[my_p.id] = "intercept"
                    mode_log[src_planet.id] = "intercept-target"
                    attacked.add(src_planet.id)
                    break


def _sequential_capture_ok(garrison_now, production, contribs):
    """Will the combined fleets capture the target? Fleets fight the garrison in
    arrival order; between arrivals the garrison grows by production. We capture
    the first time an arriving fleet exceeds the (grown) garrison; otherwise it
    just softens it. contribs = list of (eta, ships)."""
    garrison = float(garrison_now)
    prev_t = 0
    for eta, ships in sorted(contribs, key=lambda c: c[0]):
        garrison += max(0.0, float(production)) * (eta - prev_t)
        prev_t = eta
        if ships > garrison:
            return True
        garrison -= ships
    return False


def handle_opportunistic_attack(world, available, spent, target_locked, moves, mode_log):
    """Hit enemy planets that just launched a fleet while their garrison is thin
    RELATIVE TO THEIR VALUE: eligible if current ships <= OPP_BASE +
    production*OPP_PER_PROD (a high-output planet is worth taking even when
    stocked; a low-output one only when nearly empty). Fire from the nearest
    planet(s) with spare ships (each keeping its defensive reserve); if a single
    planet can't crack it, combine up to OPP_MAX_COALITION nearby planets,
    sequential-combat verified. Targets ranked by a value/cost/distance score."""
    if not _enemy_recently_launched:
        return
    cands = []
    for tgt_id in _enemy_recently_launched:
        if tgt_id in target_locked:
            continue
        tgt = world.planet_by_id.get(tgt_id)
        if tgt is None or tgt.owner == world.player or tgt.owner == -1:
            continue
        if not is_targetable(world, tgt):
            continue
        if int(tgt.ships) > OPP_BASE + float(tgt.production) * OPP_PER_PROD:
            continue  # not thin enough for its value
        nd = min((dist(p.x, p.y, tgt.x, tgt.y) for p in world.my_planets), default=1e9)
        score = (OPP_W_PROD * float(tgt.production)
                 - OPP_W_COST * int(tgt.ships)
                 - OPP_W_DIST * nd)
        cands.append((score, tgt))
    if not cands:
        return
    cands.sort(key=lambda st: -st[0])
    for _score, tgt in cands:
        if tgt.id in target_locked:
            continue
        contribs = []   # (src, angle, turns, send)
        captured = False
        for src in sorted(world.my_planets, key=lambda p: dist(p.x, p.y, tgt.x, tgt.y)):
            if mode_log.get(src.id):
                continue
            keep = _safe_reserve(world, src)
            spare = (available[src.id] - spent[src.id]) - keep
            if spare < MIN_DISPATCH_SHIPS:
                continue
            aim = aim_at_target(src, tgt, spare, world.initial_by_id,
                                world.ang_vel, world=world, check_approach=True)
            if aim is None:
                continue
            _a0, turns0 = aim
            need = effective_needed_to_capture(tgt, turns0, world) + _reaction_margin(turns0)
            send = min(spare, max(MIN_DISPATCH_SHIPS, need))
            re_aim = aim_at_target(src, tgt, send, world.initial_by_id,
                                   world.ang_vel, world=world, check_approach=True)
            if re_aim is None:
                continue
            angle, turns = re_aim
            contribs.append((src, angle, turns, send))
            if _sequential_capture_ok(int(tgt.ships), tgt.production,
                                      [(t, s) for _s, _a, t, s in contribs]):
                captured = True
                break
            if len(contribs) >= OPP_MAX_COALITION:
                break
        if not captured:
            continue
        for src, angle, turns, send in contribs:
            _commit_fleet(world, moves, spent, target_locked,
                          src.id, tgt.id, angle, turns, int(send))
            mode_log[src.id] = "opportunistic-attack"
        mode_log[tgt.id] = "opportunistic-target"


def handle_waypoint_capture(world, available, spent, target_locked, moves, mode_log):
    """Idea 9: capture neutral planets that lie between us and enemy territory
    as stepping stones / bridgeheads for future attacks.
    """
    if not world.enemy_planets or not world.neutral_planets:
        return
    for src in world.my_planets:
        if mode_log.get(src.id):
            continue
        avail = available[src.id] - spent[src.id]
        if avail < MIN_DISPATCH_SHIPS:
            continue
        nearest_enemy = min(world.enemy_planets,
                            key=lambda e: dist(src.x, src.y, e.x, e.y))
        our_dist = dist(src.x, src.y, nearest_enemy.x, nearest_enemy.y)
        # Neutrals closer to the enemy than we are (between us and enemy)
        waypoints = [
            n for n in world.neutral_planets
            if n.id not in target_locked
            and not _neutral_blocked_by_cap(world, n)
            and dist(n.x, n.y, nearest_enemy.x, nearest_enemy.y) < our_dist
            and is_in_approaching_direction(src, n, world.ang_vel)
        ]
        for n in sorted(waypoints, key=lambda p: dist(src.x, src.y, p.x, p.y)):
            plan = plan_solo_capture(world, src, n, avail, SEGMENT_MAX_TURNS)
            if plan is None:
                continue
            angle, turns, ships = plan
            _commit_fleet(world, moves, spent, target_locked,
                          src.id, n.id, angle, turns, int(ships))
            mode_log[src.id] = "waypoint-capture"
            break


def handle_home_sweep(world, available, spent, target_locked, moves, mode_log):
    """After HOME_SWEEP_TURN (30): capture ALL non-friendly planets inside home quadrant."""
    if world.step < HOME_SWEEP_TURN:
        return
    if _home_quadrant is None:
        return

    home_targets = sorted(
        [p for p in world.planets
         if p.owner != world.player
         and p.id not in target_locked
         and is_targetable(world, p)
         and _get_quadrant(p) == _home_quadrant],
        key=lambda p: int(p.ships)  # easiest first
    )
    for tgt in home_targets:
        for src in sorted(world.my_planets,
                          key=lambda p: dist(p.x, p.y, tgt.x, tgt.y)):
            if mode_log.get(src.id):
                continue
            avail = available[src.id] - spent[src.id]
            need = int(tgt.ships) + 1
            send = max(MIN_DISPATCH_SHIPS, min(need, ATTACK_MAX_SHIPS))
            if avail < send + GARRISON_TARGET:
                continue
            aim = aim_at_target(src, tgt, send, world.initial_by_id,
                                world.ang_vel, world=world, check_approach=True)
            if aim is None:
                continue
            angle, turns = aim
            _commit_fleet(world, moves, spent, target_locked,
                          src.id, tgt.id, angle, turns, int(send))
            mode_log[src.id] = "home-sweep"
            mode_log[tgt.id] = "home-sweep-target"
            break


def handle_home_defense(world, available, spent, target_locked, moves, mode_log):
    """Watch incoming hostile fleets on home-quadrant planets. If a home planet
    is predicted to be captured, reinforce it from the nearest home planet so
    it survives.
    """
    if _home_quadrant is None:
        return
    home_planets = [p for p in world.my_planets
                    if _get_quadrant(p) == _home_quadrant]
    if len(home_planets) < 2:
        return

    # Defend the most valuable home planet first (production, then garrison).
    for victim in sorted(home_planets,
                         key=lambda p: (-float(p.production), -int(p.ships))):
        if victim.id in target_locked:
            continue
        arrivals = world.arrivals_by_planet.get(victim.id, [])
        # Earliest hostile arrival and the total hostile force by then
        hostile = sorted(
            [(eta, ships) for eta, owner, ships in arrivals
             if owner != world.player and owner != -1 and ships > 0],
            key=lambda x: x[0],
        )
        if not hostile:
            continue
        # Predict defender at the last hostile arrival; if we lose it, reinforce
        last_eta = hostile[-1][0]
        owner_at, ships_at = predict_defender_at_arrival(world, victim, last_eta)
        if owner_at == world.player:
            continue  # holds on its own

        deficit = int(ships_at) + 1  # ships needed to flip it back / hold
        # Reinforce from nearest home planet with surplus
        for src in sorted(home_planets,
                          key=lambda p: dist(p.x, p.y, victim.x, victim.y)):
            if src.id == victim.id or mode_log.get(src.id):
                continue
            avail = available[src.id] - spent[src.id]
            send = max(MIN_DISPATCH_SHIPS, deficit)
            if avail < send:
                continue
            aim = aim_at_target(src, victim, send, world.initial_by_id,
                                world.ang_vel, world=world)
            if aim is None:
                continue
            angle, turns = aim
            if turns > last_eta:
                continue  # too slow to help
            _commit_fleet(world, moves, spent, target_locked,
                          src.id, victim.id, angle, turns, int(send))
            mode_log[src.id] = "home-defense"
            mode_log[victim.id] = "home-defended"
            break


def handle_home_attack(world, available, spent, target_locked, moves, mode_log):
    """Attack enemy planets inside our home zone with priority."""
    if world.home_center is None or not world.enemy_planets:
        return
    hx, hy = world.home_center
    dist_limit = HOME_RETURN_DIST_2P if world.is_2p else HOME_RETURN_DIST_4P
    home_enemies = [p for p in world.enemy_planets
                    if dist(p.x, p.y, hx, hy) <= dist_limit
                    and p.id not in target_locked]
    if not home_enemies:
        return
    home_enemies.sort(key=lambda p: int(p.ships))
    for tgt in home_enemies:
        for src in sorted(world.my_planets,
                          key=lambda p: dist(p.x, p.y, tgt.x, tgt.y)):
            if mode_log.get(src.id):
                continue
            avail = available[src.id] - spent[src.id]
            need = int(tgt.ships) + 1
            if avail < max(need, MIN_DISPATCH_SHIPS):
                continue
            send = max(need, MIN_DISPATCH_SHIPS)
            aim = aim_at_target(src, tgt, send, world.initial_by_id,
                                world.ang_vel, world=world, check_approach=True)
            if aim is None:
                continue
            angle, turns = aim
            _commit_fleet(world, moves, spent, target_locked,
                          src.id, tgt.id, angle, turns, int(send))
            mode_log[src.id] = "home-attack"
            mode_log[tgt.id] = "home-attack-target"
            break


def _send_friendly_toward(world, src, pool, ships, target_locked, moves, spent, mode_log, label):
    """Send `ships` from src toward a planet in `pool`, preferring the MOST
    pressured (stressed) destination, relaying through a closer friendly planet
    when that shortens the trip. Friendly transport, so no direction/turn gates.

    Skips destinations that already acted this turn (don't pour into a planet
    we're already launching from / defending) and destinations the do-nothing
    projection shows we lose before the fleet arrives (those are handled by the
    defense pass, not marshalling). Returns True if a fleet was committed."""
    # idea: role mutex -- don't reinforce a planet that already acted this turn.
    dests = [p for p in pool
             if p.id != src.id and p.id not in target_locked
             and not mode_log.get(p.id)]
    if not dests:
        return False
    # idea: pressure gradient -- most-stressed first, nearest as the tiebreak.
    dests.sort(key=lambda p: (-_planet_pressure(world, p),
                              dist(src.x, src.y, p.x, p.y)))
    for dest in dests:
        dest_d = dist(src.x, src.y, dest.x, dest.y)
        relay = None
        for rp in sorted(world.my_planets, key=lambda p: dist(src.x, src.y, p.x, p.y)):
            if rp.id == src.id or rp.id in target_locked:
                continue
            if dist(rp.x, rp.y, dest.x, dest.y) < dest_d:
                relay = rp
                break
        tgt = relay if relay is not None else dest
        if tgt.id == src.id or tgt.id in target_locked:
            continue
        aim = aim_at_target(src, tgt, ships, world.initial_by_id, world.ang_vel, world=world)
        if aim is None:
            continue
        angle, turns = aim
        # idea: ownership at arrival -- skip a destination the do-nothing
        # projection loses before our ships could get there (estimated at the
        # direct ETA to the destination). Don't feed a planet we won't hold.
        dest_eta = max(1, int(math.ceil(dest_d / fleet_speed(max(1, int(ships))))))
        owner_at, _ships_at = predict_defender_at_arrival(world, dest, dest_eta)
        if owner_at != world.player:
            continue
        _commit_fleet(world, moves, spent, target_locked, src.id, tgt.id, angle, turns, int(ships))
        mode_log[src.id] = label
        mode_log.setdefault(dest.id, "reinforced")  # protect dest from draining
        return True
    return False


def _reaction_margin(turns):
    """Extra ships to add to a capture, scaled by flight time. A near target
    (<= REACT_FREE_TURNS) gets 0 -- the enemy can't reinforce in time. Beyond
    that, the margin ramps linearly to REACT_MARGIN_SHIPS over REACT_SCALE_TURNS,
    covering reinforcements the enemy can route in during a long flight."""
    if turns <= REACT_FREE_TURNS:
        return 0
    ramp = min(1.0, (turns - REACT_FREE_TURNS) / max(1, REACT_SCALE_TURNS))
    return int(round(ramp * REACT_MARGIN_SHIPS))


def _reachable_enemy_mass(world, planet, horizon):
    """Distance-decayed sum of enemy garrison that could straight-line reach this
    planet within `horizon` turns. A nearer / bigger (=faster) enemy planet
    counts for more. Anticipates pressure before the enemy has even launched."""
    total = 0.0
    for ep in world.enemy_planets:
        ships = int(ep.ships)
        if ships <= 0:
            continue
        reach = fleet_speed(max(1, ships)) * horizon
        if reach <= 1e-6:
            continue
        decay = 1.0 - dist(ep.x, ep.y, planet.x, planet.y) / reach
        if decay > 0.0:
            total += ships * decay
    return total


def _planet_pressure(world, planet):
    """How stressed a planet is = (in-flight enemy ships + a share of the enemy
    mass that could reach it within the horizon) minus its own defense (garrison
    + a 2-turn production buffer + inbound friendlies). Higher = more under
    pressure; used to flow surplus toward the planets that need it. The reachable
    term makes the signal react to where the enemy IS, not just to launched fleets."""
    enemy_in, _eta = _incoming_enemy(world, planet.id)
    friendly_in = _incoming_friendly(world, planet.id)
    defense = float(planet.ships) + float(planet.production) * 2 + friendly_in
    reachable = _reachable_enemy_mass(world, planet, PRESSURE_REACH_HORIZON)
    return enemy_in + PRESSURE_REACH_WEIGHT * reachable - defense


def _enemy_pressure_quadrant(world):
    """Quadrant of our planets taking the bulk of incoming enemy fire, if one
    direction clearly dominates: top quadrant >= PRESSURE_FOCUS_SHARE of all
    incoming enemy ships, with a minimum absolute volume so noise doesn't
    trigger it. Else None (-> caller defaults to the frontier). The decision
    collapses to "stay on the frontier vs divert to the attacked direction":
    when the top quadrant is itself the frontier, the caller targets it anyway.
    """
    pressure = defaultdict(int)
    total = 0
    for p in world.my_planets:
        enemy_in, _eta = _incoming_enemy(world, p.id)
        if enemy_in > 0:
            pressure[_get_quadrant(p)] += enemy_in
            total += enemy_in
    if total < PRESSURE_FOCUS_MIN_SHIPS or not pressure:
        return None
    top_q = max(pressure, key=pressure.get)
    if pressure[top_q] >= total * PRESSURE_FOCUS_SHARE:
        return top_q
    return None


def handle_frontier_concentration(world, available, spent, target_locked, moves, mode_log):
    """Mass leftover surplus toward one direction. If a single quadrant is
    taking the bulk of incoming enemy fire, concentrate there (reinforce +
    stage a counter). Otherwise default to the frontier. Inside/home planets
    drain forward; planets already in the target quadrant keep their ships.
    Replaces the old home-evacuation (no pulling back to base)."""
    if _home_quadrant is None:
        return
    fq = _frontier_quadrant(_home_quadrant, world.ang_vel)
    focus_q = _enemy_pressure_quadrant(world)
    target_q = focus_q if focus_q is not None else fq
    pool = [p for p in world.my_planets if _get_quadrant(p) == target_q]
    if not pool:  # no friendly planet in the pressured quadrant -> use frontier
        target_q = fq
        pool = [p for p in world.my_planets if _get_quadrant(p) == target_q]
    label = "to-pressure" if (focus_q is not None and target_q == focus_q) else "to-frontier"
    # fallback destinations (relay waypoints) if the target pool is empty
    nonfront = [p for p in world.my_planets
                if _get_quadrant(p) != target_q and _get_quadrant(p) != _home_quadrant]

    for src in sorted(world.my_planets,
                      key=lambda p: -(available[p.id] - spent[p.id])):
        if mode_log.get(src.id):
            continue
        if _get_quadrant(src) == target_q:
            continue  # target-quadrant planets keep ships for attack/defense
        # Only interior (anchored-quadrant) surplus flows forward; planets that
        # drifted outside our territory are handled by the reclaim pass.
        if _parent_quads and _get_quadrant(src) not in _parent_quads:
            continue
        keep = _safe_reserve(world, src)
        surplus = (available[src.id] - spent[src.id]) - keep
        if surplus < MIN_DISPATCH_SHIPS:
            continue
        # Send the WHOLE surplus toward the target. Other planets are used only
        # as relay waypoints (handled inside _send_friendly_toward).
        _send_friendly_toward(world, src, pool or nonfront, surplus,
                              target_locked, moves, spent, mode_log, label)


def handle_steady_fire(world, available, spent, target_locked, moves, mode_log):
    """Fire when garrison > 20, send exactly what's needed (10-20 ships).
    In opening, prioritize nearby planets to form a cluster.
    """
    home_clear = _home_zone_clear(world)
    hx = hy = None
    dist_limit = None
    if not home_clear and world.home_center is not None:
        hx, hy = world.home_center
        dist_limit = HOME_RETURN_DIST_2P if world.is_2p else HOME_RETURN_DIST_4P

    is_early = world.step < EARLY_GAME_TURNS

    # Level-2 lookahead (late game only): baseline board score + a per-turn budget
    # on forward-sims, computed once.
    fwd_baseline = None
    fwd_budget = [0]
    if not is_early and FWD_LOOKAHEAD_ENABLED:
        try:
            fwd_baseline = o_melis_evaluate(world, our_step_action=None)
            fwd_budget = [40]  # cap total forward-sims this turn
        except Exception:
            fwd_baseline = None

    # Standing-aware risk: winning -> only clearly-good captures (gain>1);
    # losing -> take risks (gain>-2); even -> gain>0. Late-flush -> all-out.
    late_flush = world.remaining_steps <= 70
    standing = _standing(world)
    if late_flush or standing == "losing":
        gain_floor = -2.0
    elif standing == "winning":
        gain_floor = 1.0
    else:
        gain_floor = 0.0

    # Statuses that mean the planet must NOT launch (defending/absorbing/evacuating)
    _block = ("defense", "defended-by-solo", "defended-by-coalition",
              "doom-evac-launched", "comet-evac", "home-evac")

    for src in world.my_planets:
        status = mode_log.get(src.id)
        if is_early:
            # Early game: only block defenders/evacuees; planets that merely
            # RECEIVED reinforcements may still launch their surplus (speed).
            if status and (status.startswith("absorb") or status in _block):
                continue
        else:
            if status:
                continue
        avail = available[src.id] - spent[src.id]
        if is_early:
            if avail <= GARRISON_TARGET:  # keep 10, fire the rest
                continue
        else:
            if avail <= GARRISON_TARGET * 2:  # fire when > 20
                continue

        # Capturable targets. Early game: any garrison (no cap), no home-zone
        # restriction (grab nearest reachable; score weights distance x4).
        candidates = sorted(
            [p for p in world.planets
             if p.owner != world.player
             and p.id not in target_locked
             and is_targetable(world, p)
             and (is_early or int(p.ships) < ATTACK_MAX_SHIPS)
             and (is_early or home_clear
                  or (hx is not None and dist(p.x, p.y, hx, hy) <= dist_limit))],
            key=lambda p: -_score_target(src, p, world)
        )
        # Late game: re-rank top candidates by whole-board forward-sim gain
        if not is_early:
            candidates = _fwd_rerank(world, src, candidates, fwd_baseline, fwd_budget,
                                     gain_floor=gain_floor)
        for tgt in candidates:
            # Don't fire if a sufficient fleet is already in flight to this target
            if friendly_already_committed(world, tgt.id):
                continue
            # safe_drain: keep only enough to survive incoming enemy (not fixed 10).
            # Late-flush: keep nothing — throw everything at the enemy.
            keep = 0 if late_flush else _safe_reserve(world, src)
            if is_early:
                min_send = EARLY_MIN_SHIPS
                send = max(min_send, int(tgt.ships) + 1)
            else:
                min_send = MIN_DISPATCH_SHIPS
                send = max(min_send, min(int(tgt.ships) + 1, ATTACK_MAX_SHIPS))
            avail = available[src.id] - spent[src.id]
            if avail < send + keep:
                if is_early:
                    continue  # try a cheaper target
                break
            # ROI gate (late game): skip low-value neutral grabs
            if not _roi_ok(world, tgt, 1):
                continue
            aim = aim_at_target(src, tgt, send, world.initial_by_id,
                                world.ang_vel, world=world, check_approach=True)
            if aim is None:
                continue
            angle, turns = aim
            # Enemy planets grow each turn — need garrison AT ARRIVAL, not now.
            # Only fire if we can guarantee capture; never send a partial fleet.
            if tgt.owner != -1:
                # Exact garrison-at-arrival + a flight-time-scaled buffer for
                # reinforcements the enemy can route in during a long flight.
                need_arrival = (effective_needed_to_capture(tgt, turns, world)
                                + _reaction_margin(turns))
                if avail < need_arrival + keep:
                    continue  # not enough to surely take it -> skip
                send = max(send, need_arrival)
                re_aim = aim_at_target(src, tgt, send, world.initial_by_id,
                                       world.ang_vel, world=world, check_approach=True)
                if re_aim is None:
                    continue
                angle, turns = re_aim
            # Relay: if the target is far (>5 turns) and moving, advance the
            # fleet to a closer friendly planet instead (re-decided next turn).
            dest, dest_aim = _resolve_relay(world, src, tgt, int(send))
            if dest is None:
                continue
            d_angle, d_turns = dest_aim
            _commit_fleet(world, moves, spent, target_locked,
                          src.id, dest.id, d_angle, d_turns, int(send))
            mode_log[src.id] = "steady-fire"
            # Early game: keep firing from this rich planet at more targets
            if not is_early:
                break

        # Only planets with NO target this turn proceed (those that fired skip).
        # Before turn 50: act immediately (no wait).
        # From turn 50: wait 2 idle turns before the long-capture / frontier push.
        if mode_log.get(src.id):
            _idle_streak[src.id] = 0
            continue

        _idle_streak[src.id] = _idle_streak.get(src.id, 0) + 1
        if world.step >= 50 and _idle_streak[src.id] < 2:
            continue

        avail = available[src.id] - spent[src.id]
        if avail <= GARRISON_TARGET:
            continue

        # 1) Capture the best-score target anywhere (no distance limit)
        far_targets = sorted(
            [p for p in world.planets
             if p.owner != world.player
             and p.id not in target_locked
             and is_targetable(world, p)
             and not friendly_already_committed(world, p.id)
             and int(p.ships) + 1 <= avail],
            key=lambda p: -_score_target(src, p, world)
        )
        captured = False
        for tgt in far_targets:
            send = max(MIN_DISPATCH_SHIPS, int(tgt.ships) + 1)
            if avail < send:
                continue
            aim = aim_at_target(src, tgt, send, world.initial_by_id,
                                world.ang_vel, world=world)
            if aim is None:
                continue
            angle, turns = aim
            # Enemy planets grow; need garrison at arrival. Skip if can't take.
            if tgt.owner != -1:
                need_arrival = effective_needed_to_capture(tgt, turns, world)
                if avail < need_arrival:
                    continue
                send = max(send, need_arrival)
                re_aim = aim_at_target(src, tgt, send, world.initial_by_id,
                                       world.ang_vel, world=world)
                if re_aim is None:
                    continue
                angle, turns = re_aim
            _commit_fleet(world, moves, spent, target_locked,
                          src.id, tgt.id, angle, turns, int(send),
                          allow_long=True)
            mode_log[src.id] = "idle-long-capture"
            _idle_streak[src.id] = 0
            captured = True
            break
        if captured:
            continue

        # 2) No capturable target -> send ALL ships toward the frontier
        frontier_q = _frontier_quadrant(_get_quadrant(src), world.ang_vel)
        frontier_planets = sorted(
            [p for p in world.my_planets
             if _get_quadrant(p) == frontier_q
             and p.id != src.id
             and p.id not in target_locked],
            key=lambda p: dist(src.x, src.y, p.x, p.y)
        )
        for fp in frontier_planets:
            aim = aim_at_target(src, fp, avail, world.initial_by_id,
                                world.ang_vel, world=world)
            if aim is None:
                continue
            angle, turns = aim
            _commit_fleet(world, moves, spent, target_locked,
                          src.id, fp.id, angle, turns, int(avail),
                          allow_long=True)
            mode_log[src.id] = "idle-to-frontier"
            _idle_streak[src.id] = 0
            break


def _get_quadrant_from_pos(x, y):
    """Return quadrant 0-3 for a given (x,y) position."""
    x_half = 1 if x >= CENTER_X else 0
    y_half = 1 if y >= CENTER_Y else 0
    return x_half * 2 + y_half


def _wall_dist_in_quadrant(p):
    """Distance from the nearest quadrant boundary wall."""
    q = _get_quadrant(p)
    if q == 0:   # NW: x<50, y<50
        return min(p.x, CENTER_X - p.x, p.y, CENTER_Y - p.y)
    elif q == 1: # SW: x<50, y>=50
        return min(p.x, CENTER_X - p.x, p.y - CENTER_Y, BOARD - p.y)
    elif q == 2: # NE: x>=50, y<50
        return min(p.x - CENTER_X, BOARD - p.x, p.y, CENTER_Y - p.y)
    else:        # SE: x>=50, y>=50
        return min(p.x - CENTER_X, BOARD - p.x, p.y - CENTER_Y, BOARD - p.y)


def _select_parents(world):
    """Return fixed parent planets (set once at PARENT_START_TURN) still owned.
    Returns empty list if parents haven't been fixed yet."""
    if not _parent_ids:
        return []
    return [world.planet_by_id[pid] for pid in _parent_ids
            if pid in world.planet_by_id and world.planet_by_id[pid].owner == world.player]


def _compute_parent_candidates(world):
    """Compute the best static parent in the home quadrant (most central).
    Used once at PARENT_START_TURN to fix parents."""
    home_static = [p for p in world.my_planets
                   if _get_quadrant(p) == _home_quadrant and is_static_planet(p)]
    if not home_static:
        return []
    home_static.sort(key=lambda p: -_wall_dist_in_quadrant(p))
    return home_static[:1]


def _planet_initial_quadrant(planet, world):
    """Return the quadrant the planet started in (using initial_by_id)."""
    init = world.initial_by_id.get(planet.id)
    if init is None:
        return _get_quadrant(planet)
    return _get_quadrant_from_pos(init.x, init.y)


def _parent_anchor(world, q):
    """The anchor planet of quadrant q = our most central (corner-ward),
    static-preferred owned planet currently in it. None if we own none there."""
    cand = [p for p in world.my_planets if _get_quadrant(p) == q]
    if not cand:
        return None
    cand.sort(key=lambda p: (0 if is_static_planet(p) else 1, -_wall_dist_in_quadrant(p)))
    return cand[0]


def _update_parent_quads(world):
    """Maintain the set of anchored quadrants (our territory). Start with the
    home quadrant plus, in 2P, the next most-owned quadrant (aim for half the
    board); 4P starts with home only. Drop quadrants we no longer occupy (and
    refill from where we're now strongest), and grow up to PARENT_MAX as we
    secure new quadrants (own >= PARENT_GROW_FRACTION of that quadrant's planets)."""
    owned = defaultdict(int)
    total = defaultdict(int)
    for p in world.my_planets:
        owned[_get_quadrant(p)] += 1
    for p in world.planets:
        if p.id not in world.comet_ids:
            total[_get_quadrant(p)] += 1
    occupied = [q for q in range(4) if owned[q] > 0]
    keep = {q for q in _parent_quads if q in occupied}
    _parent_quads.clear()
    _parent_quads.update(keep)
    if not occupied:
        return
    baseline = 2 if world.is_2p else 1
    # home first, then most-owned (so a lost home falls back to where we're strong)
    pr = sorted(occupied, key=lambda q: (q != _home_quadrant, -owned[q]))
    for q in pr:
        if len(_parent_quads) >= baseline:
            break
        _parent_quads.add(q)
    # growth: a quadrant becomes an anchor once we own >= 40% of its planets
    for q in sorted(occupied, key=lambda q: -owned[q]):
        if len(_parent_quads) >= PARENT_MAX:
            break
        if q not in _parent_quads and total[q] > 0 and owned[q] >= PARENT_GROW_FRACTION * total[q]:
            _parent_quads.add(q)


def _opponent_aggression(world):
    """Smoothed estimate (0-1) of how aggressive the opponent is = the share of
    enemy force that is IN FLIGHT (vs sitting on planets). Updated once per turn;
    high = they are attacking, low = they are hoarding. Works in 2P and 4P."""
    global _opp_aggression
    in_flight = sum(int(f.ships) for f in world.fleets
                    if f.owner != world.player and f.owner != -1 and int(f.ships) > 0)
    on_planet = sum(int(p.ships) for p in world.enemy_planets)
    total = in_flight + on_planet
    inst = (in_flight / total) if total > 0 else 0.0
    _opp_aggression = AGGRESSION_EMA * inst + (1.0 - AGGRESSION_EMA) * _opp_aggression
    return _opp_aggression


def handle_proactive_defense(world, available, spent, target_locked, moves, mode_log):
    """One move ahead of the reactive defense: when the opponent is AGGRESSIVE,
    pre-thicken the planets most worth protecting before the enemy even launches.
    Candidates are owned planets whose net pressure (in-flight + reachable enemy
    mass - own defense) clears PROACTIVE_PRESSURE_MIN; among those we defend the
    most VALUABLE (highest production) first, up to PROACTIVE_MAX_TARGETS, pulling
    a capped top-up from the nearest safe (low-pressure) planet. Skipped entirely
    against a passive opponent (focus offense instead)."""
    if not world.enemy_planets:
        return
    if _opponent_aggression(world) < AGGRESSION_THRESHOLD:
        return  # passive opponent -> don't tie up ships pre-defending
    pres = {p.id: _planet_pressure(world, p) for p in world.my_planets}
    victims = [p for p in world.my_planets
               if pres[p.id] >= PROACTIVE_PRESSURE_MIN and not mode_log.get(p.id)]
    if not victims:
        return
    # value first (production), then how badly pressured
    victims.sort(key=lambda p: (-float(p.production), -pres[p.id]))
    for victim in victims[:PROACTIVE_MAX_TARGETS]:
        need = min(int(math.ceil(pres[victim.id])), PROACTIVE_MAX_SEND)
        if need < MIN_DISPATCH_SHIPS:
            continue
        for src in sorted(world.my_planets, key=lambda s: dist(s.x, s.y, victim.x, victim.y)):
            if src.id == victim.id or mode_log.get(src.id):
                continue
            if pres.get(src.id, 0.0) >= PROACTIVE_PRESSURE_MIN:
                continue  # don't strip another threatened planet
            keep = _safe_reserve(world, src)
            spare = (available[src.id] - spent[src.id]) - keep
            if spare < MIN_DISPATCH_SHIPS:
                continue
            send = min(spare, need)
            aim = aim_at_target(src, victim, send, world.initial_by_id, world.ang_vel, world=world)
            if aim is None:
                continue
            angle, turns = aim
            if turns > SEGMENT_MAX_TURNS:
                continue  # too far to help in time
            _commit_fleet(world, moves, spent, target_locked,
                          src.id, victim.id, angle, turns, int(send))
            mode_log[src.id] = "proactive-defense"
            mode_log[victim.id] = "proactive-defended"
            break


def handle_reclaim_drift(world, available, spent, target_locked, moves, mode_log):
    """Pull ships from planets that have drifted OUT of our anchored quadrants
    back to the nearest anchor, keeping our force coherent. A drifted planet
    reclaims immediately and once more after DRIFT_RECLAIM_SECOND_DELAY turns,
    then stops (it keeps its production and acts normally). High-production
    planets (>= DRIFT_RECLAIM_KEEP_PROD) keep a defensive reserve; others send
    everything."""
    if not _parent_quads:
        return
    anchors = [a for a in (_parent_anchor(world, q) for q in _parent_quads) if a is not None]
    if not anchors:
        return
    for p in world.my_planets:
        q = _get_quadrant(p)
        if q in _parent_quads:
            _drift_start.pop(p.id, None)   # back inside -> reset drift state
            _drift_count.pop(p.id, None)
            continue
        if mode_log.get(p.id):
            continue
        if p.id not in _drift_start:
            _drift_start[p.id] = world.step
            _drift_count[p.id] = 0
        cnt = _drift_count.get(p.id, 0)
        since = world.step - _drift_start[p.id]
        if cnt == 0:
            pass                                   # immediate reclaim
        elif cnt == 1 and since >= DRIFT_RECLAIM_SECOND_DELAY:
            pass                                   # the +DELAY reclaim
        else:
            continue                               # between reclaims, or done (>=2)
        keep = _safe_reserve(world, p) if float(p.production) >= DRIFT_RECLAIM_KEEP_PROD else 0
        send = (available[p.id] - spent[p.id]) - keep
        if send < MIN_DISPATCH_SHIPS:
            continue
        dest = min((a for a in anchors if a.id != p.id),
                   key=lambda a: dist(p.x, p.y, a.x, a.y), default=None)
        if dest is None:
            continue
        aim = aim_at_target(p, dest, send, world.initial_by_id, world.ang_vel, world=world)
        if aim is None:
            continue
        angle, turns = aim
        _commit_fleet(world, moves, spent, target_locked,
                      p.id, dest.id, angle, turns, int(send))
        mode_log[p.id] = "reclaim-drift"
        _drift_count[p.id] = cnt + 1


def handle_parent_evac(world, available, spent, target_locked, moves, mode_log):
    """If a parent planet has rotated out of its initial quadrant, evacuate
    all its ships back to a planet in its original quadrant.
    """
    if not PARENT_ENABLED or world.step < PARENT_START_TURN:
        return
    parent_ids = {p.id for p in _select_parents(world)}
    for src in world.my_planets:
        if src.id not in parent_ids:
            continue
        if mode_log.get(src.id):
            continue
        initial_q = _planet_initial_quadrant(src, world)
        current_q = _get_quadrant(src)
        if initial_q == current_q:
            continue  # hasn't drifted
        # Drifted: evacuate all ships to a planet in the original quadrant
        avail = available[src.id] - spent[src.id]
        if avail <= 0:
            continue
        home_q_planets = [p for p in world.my_planets
                         if _get_quadrant(p) == initial_q and p.id != src.id
                         and p.id not in target_locked]
        if not home_q_planets:
            continue
        dst = min(home_q_planets, key=lambda p: dist(src.x, src.y, p.x, p.y))
        aim = aim_at_target(src, dst, avail, world.initial_by_id,
                            world.ang_vel, world=world)
        if aim is None:
            continue
        angle, turns = aim
        _commit_fleet(world, moves, spent, target_locked,
                      src.id, dst.id, angle, turns, int(avail))
        mode_log[src.id] = "parent-evac"


def handle_parent_collect(world, available, spent, target_locked, moves, mode_log):
    """Non-parent planets send surplus (>20) toward parents via relay.
    Relay = nearest friendly planet that is closer to the parent than the source.
    This creates a cascade chain that batches ships as they flow.
    """
    if not PARENT_ENABLED or world.step < PARENT_START_TURN:
        return
    parents = _select_parents(world)
    if not parents:
        return
    parent_ids = {p.id for p in parents}

    # Determine frontier quadrants to exclude (they should attack, not feed back)
    frontier_qs = set()
    for p in parents:
        frontier_qs.add(_frontier_quadrant(_get_quadrant(p), world.ang_vel))

    for src in sorted(world.my_planets,
                      key=lambda p: -(available[p.id] - spent[p.id])):
        if src.id in parent_ids:
            continue
        if _get_quadrant(src) in frontier_qs:
            continue  # frontier planets use ships for attack, not feeding parent
        if mode_log.get(src.id):
            continue
        avail = available[src.id] - spent[src.id]
        if avail <= GARRISON_TARGET * 2:
            continue
        surplus = avail - GARRISON_TARGET

        # Find nearest parent to target
        target_parent = min(parents, key=lambda p: dist(src.x, src.y, p.x, p.y))
        parent_dist = dist(src.x, src.y, target_parent.x, target_parent.y)

        # Try relay: nearest friendly planet that is closer to parent than src
        relay = None
        relay_candidates = sorted(
            [p for p in world.my_planets
             if p.id != src.id
             and p.id not in target_locked
             and dist(p.x, p.y, target_parent.x, target_parent.y) < parent_dist],
            key=lambda p: dist(src.x, src.y, p.x, p.y)
        )
        for rp in relay_candidates:
            aim = aim_at_target(src, rp, surplus, world.initial_by_id,
                                world.ang_vel, world=world)
            if aim is None:
                continue
            _, turns = aim
            if turns <= SEGMENT_MAX_TURNS:
                relay = rp
                break

        # Fall back to direct parent if no relay
        dst = relay if relay is not None else target_parent
        if dst.id in target_locked:
            continue
        aim = aim_at_target(src, dst, surplus, world.initial_by_id,
                            world.ang_vel, world=world)
        if aim is None:
            continue
        angle, turns = aim
        if turns > SEGMENT_MAX_TURNS:
            continue
        _commit_fleet(world, moves, spent, target_locked,
                      src.id, dst.id, angle, turns, int(surplus))
        mode_log[src.id] = "to-parent"


def handle_parent_attack(world, available, spent, target_locked, moves, mode_log):
    """Parent planets attack best target. If not enough ships, send surplus
    to another parent to accumulate (parent coordination).
    """
    if not PARENT_ENABLED or world.step < PARENT_START_TURN:
        return
    parents = _select_parents(world)
    if not parents:
        return

    for parent in parents:
        if mode_log.get(parent.id):
            continue
        avail = available[parent.id] - spent[parent.id]
        if avail <= GARRISON_TARGET:
            continue

        # Attackable targets: can we win right now?
        all_targets = [p for p in world.planets
                       if p.owner != world.player
                       and p.id not in target_locked
                       and is_targetable(world, p)
                       and not friendly_already_committed(world, p.id)]

        surplus = avail - GARRISON_TARGET

        # Sort: nearest in frontier direction first, then by score
        my_q = _get_quadrant(parent)
        frontier_q = _frontier_quadrant(my_q, world.ang_vel)
        attackable = [t for t in all_targets if int(t.ships) + 1 <= surplus]
        attackable.sort(key=lambda p: (
            0 if _get_quadrant(p) == frontier_q else 1,  # frontier targets first
            -_score_target(parent, p, world)
        ))

        attacked = False
        for tgt in attackable:
            # Send ALL surplus (shooting star style: overwhelming force)
            aim = aim_at_target(parent, tgt, surplus, world.initial_by_id,
                                world.ang_vel, world=world, check_approach=True)
            if aim is None:
                continue
            angle, turns = aim
            _commit_fleet(world, moves, spent, target_locked,
                          parent.id, tgt.id, angle, turns, int(surplus))
            mode_log[parent.id] = "parent-attack"
            attacked = True
            break

        if attacked:
            continue

        surplus = avail - GARRISON_TARGET
        if surplus < MIN_DISPATCH_SHIPS:
            continue

        # Can't attack: try pooling with another parent
        # Only pool with other parents that are in frontier direction and have room
        frontier_q = _frontier_quadrant(_get_quadrant(parent), world.ang_vel)
        other_parents = [p for p in parents
                         if p.id != parent.id
                         and p.id not in target_locked
                         and not mode_log.get(p.id)
                         and _get_quadrant(p) == frontier_q]
        pooled = False
        for dst in sorted(other_parents,
                          key=lambda p: dist(parent.x, parent.y, p.x, p.y)):
            aim = aim_at_target(parent, dst, surplus, world.initial_by_id,
                                world.ang_vel, world=world)
            if aim is None:
                continue
            angle, turns = aim
            if turns > SEGMENT_MAX_TURNS:
                continue
            _commit_fleet(world, moves, spent, target_locked,
                          parent.id, dst.id, angle, turns, int(surplus))
            mode_log[parent.id] = "parent-pool"
            pooled = True
            break

        if not pooled:
            my_q = _get_quadrant(parent)
            frontier_q = _frontier_quadrant(my_q, world.ang_vel)
            is_frontier_parent = (my_q == frontier_q)

            if not is_frontier_parent:
                # Non-frontier parent: send all ships to nearest frontier parent
                frontier_parents = sorted(
                    [p for p in parents
                     if p.id != parent.id
                     and _get_quadrant(p) == frontier_q
                     and p.id not in target_locked],
                    key=lambda p: dist(parent.x, parent.y, p.x, p.y)
                )
                for fp in frontier_parents:
                    aim = aim_at_target(parent, fp, surplus, world.initial_by_id,
                                        world.ang_vel, world=world)
                    if aim is None:
                        continue
                    angle, turns = aim
                    # Allow longer range since this is intentional relay
                    if turns <= SEGMENT_MAX_TURNS * 3:
                        _commit_fleet(world, moves, spent, target_locked,
                                      parent.id, fp.id, angle, turns, int(surplus))
                        mode_log[parent.id] = "parent-to-frontier-parent"
                        pooled = True
                        break

            if not pooled:
                # Frontier parent or no frontier parent: send to any frontier planet
                all_frontier = []
                occupied_qs = set(_get_quadrant(p) for p in world.my_planets)
                for oq in occupied_qs:
                    fq = _frontier_quadrant(oq, world.ang_vel)
                    all_frontier.extend([
                        p for p in world.my_planets
                        if _get_quadrant(p) == fq
                        and p.id not in target_locked
                        and available[p.id] - spent[p.id] < GARRISON_TARGET * 2
                    ])
                all_frontier.sort(key=lambda p: dist(parent.x, parent.y, p.x, p.y))
                for fp in all_frontier:
                    aim = aim_at_target(parent, fp, surplus, world.initial_by_id,
                                        world.ang_vel, world=world)
                    if aim is None:
                        continue
                    angle, turns = aim
                    if turns <= SEGMENT_MAX_TURNS * 2:
                        _commit_fleet(world, moves, spent, target_locked,
                                      parent.id, fp.id, angle, turns, int(surplus))
                        mode_log[parent.id] = "parent-to-frontier"
                        break


def _assault_quadrant_ok(world, tgt):
    """4P: only assault targets in a quadrant we occupy or adjacent to one (a
    clockwise neighbour); skip the diagonally-opposite quadrant -- too far, across
    the board. (2P callers bypass this.)"""
    our_quads = {_get_quadrant(p) for p in world.my_planets}
    if not our_quads:
        return False
    tq = _get_quadrant(tgt)
    for q in our_quads:
        if tq == q or tq == _CW_NEXT[q] or tq == _CCW_NEXT[q]:
            return True
    return False


def handle_enemy_assault(world, available, spent, target_locked, moves, mode_log):
    """All-out attack when we have overwhelming force.
    2P: fire when our total deployable >= ENEMY_ASSAULT_RATIO x the (single)
        enemy's garrison; hit all its planets.
    4P: pick the WEAKEST enemy; fire when our deployable >= ratio x its garrison,
        and only hit its planets in our-occupied-or-adjacent quadrants (not the
        diagonal one).
    Highest production first; combine the nearest planets (no reserve kept --
    we're dominant) until the sequential-combat sim confirms capture, so big
    planets get cracked by several planets at once."""
    if not world.enemy_planets:
        return
    my_available = sum(max(0, available[p.id] - spent[p.id]) for p in world.my_planets)
    if world.is_2p:
        targets = list(world.enemy_planets)
        quad_filter = False
    else:
        by_owner = defaultdict(list)
        for p in world.enemy_planets:
            by_owner[p.owner].append(p)
        targets = min(by_owner.values(), key=lambda ps: sum(int(p.ships) for p in ps))
        quad_filter = True
    enemy_garrison = sum(int(p.ships) for p in targets)
    if enemy_garrison <= 0 or my_available < enemy_garrison * ENEMY_ASSAULT_RATIO:
        return

    for tgt in sorted(targets, key=lambda p: -float(p.production)):
        if tgt.id in target_locked or not is_targetable(world, tgt):
            continue
        if quad_filter and not _assault_quadrant_ok(world, tgt):
            continue
        contribs = []   # (src, angle, turns, send)
        captured = False
        for src in sorted(world.my_planets, key=lambda p: dist(p.x, p.y, tgt.x, tgt.y)):
            if mode_log.get(src.id):
                continue
            spare = available[src.id] - spent[src.id]   # dominant -> no reserve kept
            if spare < MIN_DISPATCH_SHIPS:
                continue
            aim = aim_at_target(src, tgt, spare, world.initial_by_id, world.ang_vel,
                                world=world, check_approach=True)
            if aim is None:
                continue
            _a0, turns0 = aim
            need = effective_needed_to_capture(tgt, turns0, world) + _reaction_margin(turns0)
            send = min(spare, max(MIN_DISPATCH_SHIPS, need))
            re_aim = aim_at_target(src, tgt, send, world.initial_by_id, world.ang_vel,
                                   world=world, check_approach=True)
            if re_aim is None:
                continue
            angle, turns = re_aim
            contribs.append((src, angle, turns, send))
            if _sequential_capture_ok(int(tgt.ships), tgt.production,
                                      [(t, s) for _s, _a, t, s in contribs]):
                captured = True
                break
            if len(contribs) >= ASSAULT_MAX_COALITION:
                break
        if not captured:
            continue
        for src, angle, turns, send in contribs:
            _commit_fleet(world, moves, spent, target_locked,
                          src.id, tgt.id, angle, turns, int(send))
            mode_log[src.id] = "assault"
        mode_log[tgt.id] = "assault-target"


def plan_moves(world, deadline=None):
    global _pending_commitments

    def _commitment_viable(c):
        if c["arrival_abs"] <= world.step:
            return False
        target = world.planet_by_id.get(c["target_id"])
        if target is None:
            return False
        if target.owner == world.player:
            return False
        if FAILTOLERANT_ENABLED:
            owner_at_commit = c.get("owner_at_commit")
            if owner_at_commit is not None and int(target.owner) != int(owner_at_commit):
                return False
        return True
    _pending_commitments[:] = [c for c in _pending_commitments if _commitment_viable(c)]

    _update_neutral_watchlist(world)

    moves = []
    spent = defaultdict(int)
    target_locked = set()
    mode_log = {}

    rescue_needs = {}
    available = {}
    for p in world.my_planets:
        arrivals = world.arrivals_by_planet.get(p.id, [])
        reserve, holds, deficit, dline = compute_planet_reserve(
            p, arrivals, world.player
        )
        available[p.id] = max(0, int(p.ships) - reserve)
        if not holds:
            rescue_needs[p.id] = (deficit, dline, p)
            mode_log[p.id] = "absorb-need-rescue"
        else:
            # Only mark 'absorb' when HOSTILE fleets incoming (need to hold ships).
            # Friendly arrivals must NOT block this planet from launching.
            hostile_incoming = any(
                owner != world.player and owner != -1 and ships > 0
                for _eta, owner, ships in arrivals
            )
            if hostile_incoming:
                mode_log[p.id] = "absorb"

    def _over_budget():
        return deadline is not None and time.perf_counter() >= deadline

    # --- Focused late-game pipeline (3 pieces) ---
    # Defense: rescue doomed planets + reinforce threatened ones.
    handle_comet_evac(world, available, spent, target_locked, moves, mode_log)
    handle_defense(world, rescue_needs, available, spent, target_locked, moves, mode_log)
    if not _over_budget():
        handle_home_defense(world, available, spent, target_locked, moves, mode_log)

    # Proactive defense: vs an AGGRESSIVE opponent, pre-thicken the most valuable
    # threatened planets before they're hit. Skipped vs a passive opponent.
    if not _over_budget():
        handle_proactive_defense(world, available, spent, target_locked, moves, mode_log)

    # Tempo strikes BEFORE the general capture pass, so they claim weakened /
    # finishable enemies first: hit planets that just launched (thin), then go
    # all-out when we hold an overwhelming force advantage.
    if not _over_budget():
        handle_opportunistic_attack(world, available, spent, target_locked, moves, mode_log)
    if not _over_budget():
        handle_enemy_assault(world, available, spent, target_locked, moves, mode_log)

    # Piece 2 — coordinated strike: steady_fire picks the best target by board
    # forward-sim and (for enemies) sends enough to capture. Frontier planets are
    # rich (fed by concentration), so this becomes the decisive concentrated blow.
    if not _over_budget():
        handle_steady_fire(world, available, spent, target_locked, moves, mode_log)

    # Economy: grab worthwhile comets for their temporary production (evac pulls
    # the ships back before the comet leaves).
    if not _over_budget():
        handle_comet_capture(world, available, spent, target_locked, moves, mode_log)

    # Reclaim: pull ships from planets that drifted outside our anchored
    # territory back to the nearest anchor (keeps our force coherent). Runs
    # before frontier concentration so drifted planets go home, not forward.
    if not _over_budget():
        handle_reclaim_drift(world, available, spent, target_locked, moves, mode_log)

    # Frontier concentration: drain INTERIOR (anchored-quadrant) surplus toward
    # the frontier / most-pressured direction. (Drifted planets are reclaimed.)
    if not _over_budget():
        handle_frontier_concentration(world, available, spent, target_locked, moves, mode_log)

    return moves


# ===== Fused opponent-bot logic (o_ prefix), used for early game =====
MIMIC_OLD_UNTIL = 100


o_F14_4A_2P_FOCUS_ENABLED = True
o_F14_4A_2P_FOCUS_DIST_BONUS = 18.0
o_F14_4A_2P_FOCUS_HAMMER_BONUS = 20.0
o_F14_4A_2P_FOCUS_MEGA_BONUS = 100

o_BOARD = 100.0
o_CENTER_X = 50.0
o_CENTER_Y = 50.0
o_SUN_R = 10.0
o_SUN_SAFETY = 1.5
o_ROTATION_LIMIT = 50.0
o_LAUNCH_CLEARANCE = 0.1
o_MAX_SPEED = 6.0
o_TOTAL_STEPS = 500
o_SIM_HORIZON = 110
o_FWD_SIM_FILTER_ENABLED = True
o_FWD_SIM_HORIZON = 7
o_FWD_SIM_DEFENSE_CHECK = True
o_FWD_SIM_RANK_BONUS_4P = 0.0

o_SEARCH_EXPAND_4P_ENABLED = True


o_SEARCH_EXPAND_2P_ENABLED = True
o_SEARCH_MAX_PER_SOURCE = 3
o_SEARCH_MAX_ACTIONS_TO_PICK = 5
o_SEARCH_MAX_ACTIONS_TO_PICK_2P = 7
o_SEARCH_DISABLES_CHEAP_PICKUP = True
o_HAMMER_MELIS_VERIFY = True
o_SEARCH_DEPTH2_ENABLED = True


o_NEUTRAL_CAP_USES_EFFECTIVE_GARRISON = True
o_NEUTRAL_CAP_LOOKAHEAD = 10

o_N6_USE_EFFECTIVE_PRE_GARRISON = True

o_TERMINAL_PHASE_ENABLED = True
o_TERMINAL_PHASE_TURNS = 30

o_FLEET_INTENT_ENABLED = True
o_FLEET_INTENT_MIN_DROP = 8
o_FLEET_INTENT_HAMMER_BONUS = 5.0


o_F1B_EXPAND_BONUS_ENABLED = True
o_F1B_EXPAND_BONUS = 3.0


o_R1_RECAPTURE_PRIORITY_ENABLED = True
o_R1_RECAPTURE_HAMMER_BONUS = 8.0

o_E2_USE_GARRISON_THRESHOLD = True


o_SO1_STATIC_PREFERENCE_ENABLED = True
o_SO1_STATIC_BONUS = 2.179862
o_SO1_STATIC_BONUS_2P = 2.179862
o_SO1_STATIC_BONUS_4P = 2.95474


o_SP1_SPEED_AWARE_ENABLED = True
o_SP1_LONG_DIST_THRESHOLD = 27.637375
o_SP1_LONG_DIST_SHIPS = 22


o_TI1_TIE_FOR_WIN_ENABLED = True
o_TI1_HORIZON_TURNS = 25
o_TI1_REQUIRED_EXTRA_MARGIN = 5
o_TI1_TRAILING_GAP_MIN = 10


o_AS1_ANTI_SECOND_ENABLED = True


o_FAILTOLERANT_ENABLED = True


o_MELIS_SANITY_ENABLED = True
o_MELIS_SANITY_THETA = 3.0


o_F16_DIVERSITY_ENABLED = True
o_F16_CLOSEST_PICKS = 2
o_F16_PROD_PICKS = 1


o_FWD_SCORE_AGG_ENABLED = True
o_FWD_SCORE_AGG_TURNS = (4, 8, 14, 20)


o_PSM_OPENING_TURN = 14
o_PSM_OPENING_TURN_2P = 14
o_PSM_OPENING_TURN_4P = 10


o_ABSORB_MIN_THREAT = 3
o_ABSORB_PROJECTION_MARGIN = 0


o_DEFENSE_OVERSEND = 1
o_DEFENSE_OVERSEND_2P = 1
o_DEFENSE_OVERSEND_4P = 0
o_DEFENSE_COALITION_MAX = 2


o_MIN_DISPATCH_SHIPS = 8


o_F3_THREE_BUCKET_ENABLED = True
o_F3_SAFE_FLOOR = 5
o_F3_SAFE_DIST = 12.0
o_F3_HARD_FLOOR = 14
o_F3_HARD_GARRISON = 14


o_EXPAND_K_OPENING = 2
o_EXPAND_K_MID = 1
o_EXPAND_MAX_TRAVEL_OPENING = 20
o_EXPAND_MAX_TRAVEL_MID = 14
o_EXPAND_MIN_MARGIN = 0
o_EXPAND_MIN_MARGIN_4P = 3


o_X8B_2P_EXTRA = 3
o_EXPAND_MIN_SHIPS = o_MIN_DISPATCH_SHIPS


o_EXPAND_MIN_PROD_2P = 2


o_TIEBREAK_ENABLED = True
o_TIEBREAK_EPS_FRAC = 0.005
o_TIEBREAK_EPS_MIN = 1.439234


o_ROT_AWARE_RANK_ENABLED = os.environ.get("V124_ROT_AWARE", "1") != "0"


o_VALUE_WEIGHT_2P = 4.86118
o_VALUE_WEIGHT_4P = float(os.environ.get("V126_VALUE_WEIGHT_4P", "2.0"))


o_ANTI_SNIPE_ENABLED = os.environ.get("V124_ANTI_SNIPE", "1") != "0"
o_ANTI_SNIPE_HORIZON = 25
o_ANTI_SNIPE_2P_ONLY = False


o_REACTIVE_SNIPE_PROJECTION_ENABLED = True
o_REACTIVE_EMIT_FRAC = 0.49629
o_REACTIVE_MIN_ENEMY_SHIPS = 5
o_REACTIVE_MIN_PROJECTED = 3


o_SUN_SHADOW_REACTIVE_FILTER = True


o_COUNTER_SNIPE_ENABLED = os.environ.get("V124_COUNTER_SNIPE", "1") != "0"
o_COUNTER_SNIPE_2P_ONLY = False
o_COUNTER_SNIPE_MAX_COST = 30
o_COUNTER_SNIPE_MIN_DELAY = 1
o_COUNTER_SNIPE_MAX_DELAY = 12


o_CHEAP_PICKUP_ENABLED = os.environ.get("V124_CHEAP_PICKUP", "1") != "0"
o_CHEAP_PICKUP_4P_ONLY = False  # enabled in 2P too (early planet-count boost)
o_CHEAP_PICKUP_MAX_GARRISON = 25

o_CHEAP_PICKUP_MIN_PROD = int(os.environ.get("F32_CP_MIN_PROD", "2"))


o_ENDGAME_ROI_ENABLED = os.environ.get("V128_ENDGAME_ROI", "1") != "0"
o_ENDGAME_ROI_TURNS = 30


o_NEUTRAL_TEMPO_FILTER_ENABLED = os.environ.get("V128_TEMPO_FILTER", "1") != "0"
o_NEUTRAL_TEMPO_THRESHOLD = 10


o_LAUNCH_BLACKOUT_ENABLED = os.environ.get("V128_LAUNCH_BLACKOUT", "1") != "0"
o_LAUNCH_BLACKOUT_TURNS = 10


o_NEUTRAL_HARD_CAP_ENABLED = os.environ.get("V128_NEUTRAL_CAP", "1") != "0"
o_NEUTRAL_HARD_CAP_4P = 40
o_NEUTRAL_HARD_CAP_2P = 61
o_NEUTRAL_WATCHLIST_MIN_DROP = 5


o_LOW_PROD_NEUTRAL_SKIP_ENABLED = True
o_LOW_PROD_NEUTRAL_SKIP_PROD = 1
o_LOW_PROD_NEUTRAL_SKIP_GARRISON = 14


o_WEAKEST_TARGET_ENABLED = os.environ.get("V128_WEAKEST_TARGET", "1") != "0"
o_WEAKEST_TARGET_BONUS = 2.0
o_WEAKEST_TARGET_MIN_STEP = 60
o_WEAKEST_DONT_FINISH_SHARE = 0.05
o_WEAKEST_DONT_FINISH_PENALTY = 12.0


o_LEADER_BASH_ENABLED = os.environ.get("V128_LEADER_BASH", "1") != "0"
o_LEADER_BASH_RATIO = 1.3
o_LEADER_BASH_BONUS = 4.0
o_LEADER_BASH_MIN_STEP = 60


o_COALITION_ENABLED = True
o_COALITION_MAX_PARTICIPANTS = 3
o_COALITION_NEUTRALS_ONLY = False
o_COALITION_MAX_TRAVEL_BONUS = 2
o_COALITION_MIN_PER_CONTRIBUTOR = 15
o_COALITION_MIN_PER_CONTRIBUTOR_2P = 15
o_COALITION_MIN_PER_CONTRIBUTOR_4P = 5
o_COALITION_MIN_TARGET_SHIPS = 20


o_HAMMER_ENABLED = True
o_HAMMER_STOCKPILE_MIN = 50
o_HAMMER_TARGET_PROD_MIN = 2
o_HAMMER_PROD_SHARE_TRIGGER = 0.40
o_HAMMER_OVERKILL_RATIO = 1.30
o_HAMMER_SURROUNDED_PROMOTE_TURNS = 10
o_HAMMER_MAX_TRAVEL = O_MAX_TRAVEL_CAP  # was 24; no long-distance hammers
o_HAMMER_ABORT_OVERRUN_RATIO = 1.329521
o_HAMMER_PLAN_REVALIDATE_INTERVAL = 1
o_HAMMER_MIN_PER_CONTRIBUTOR = 9


o_MEGA_HAMMER_ENABLED = True


o_MEGA_HAMMER_4P_ONLY = True
o_MEGA_HAMMER_SHIPS_MIN = 300
o_MEGA_HAMMER_TARGET_GARRISON_MAX = 80
o_MEGA_HAMMER_MAX_TRAVEL = O_MAX_TRAVEL_CAP  # was 40; no long-distance mega-hammers


o_PROD_RESERVE_ENABLED = False


o_MEGA_HAMMER_THRESHOLD_BY_PROD = {5: 200, 4: 250, 3: 300, 2: 350, 1: 400}


o_FRESH_CAPTURE_INHERITANCE_ENABLED = True
o_FRESH_CAPTURE_MAX_AGE = 5
o_MEGA_HAMMER_SHIPS_MIN_FRESH = 200


o_MEGA_HAMMER_CONCENTRATE_ENABLED = True
o_MEGA_HAMMER_MAX_PER_TURN = 1


o_MEGA_HAMMER_MELIS_VERIFY = True


o_MEGA_HAMMER_VERIFY_OPP_EMIT = 0.30


o_HAMMER_NO_THREAT_OVERSEND_ENABLED = True
o_HAMMER_NO_THREAT_OVERSEND_2P_ONLY = True


o_HAMMER_ALWAYS_OVERSEND_2P = False


o_HAMMER_SAFE_SURPLUS_OVERSEND_ENABLED = True
o_HAMMER_SAFE_SURPLUS_RATIO = 2.0
o_HAMMER_OVERSEND_MAX_THREAT_RATIO = 0.3


o_ACCUMULATOR_ENABLED = True
o_ACCUMULATOR_4P_ONLY = True
o_ACCUMULATOR_TURN_MIN = 15
o_ACCUMULATOR_LEAD_MIN_SHIPS = 100
o_ACCUMULATOR_LEAD_THREAT_RATIO = 0.5
o_ACCUMULATOR_FEEDER_MIN_SURPLUS = 30
o_ACCUMULATOR_FEEDER_KEEP_RESERVE = 30
o_ACCUMULATOR_FEEDER_MAX_TRAVEL = O_MAX_TRAVEL_CAP  # was 30; feed only nearby
o_ACCUMULATOR_MAX_FEEDS_PER_TURN = 3


o_BRAIN_LEAD_RESERVE_ENABLED = True
o_BRAIN_LEAD_RESERVE_4P_ONLY = True


o_BRAIN_LEAD_RESERVE_MIN_SHIPS = 200


o_BRAIN_LEAD_RESERVE_REQUIRE_TARGET = False


o_BRAIN_LEAD_PREFER_FRONTIER = False
o_BRAIN_LEAD_FRONTIER_WEIGHT = 2.0


o_MEGA_HAMMER_TARGET_GARRISON_MAX_ITER_H = 100


o_MULTIPRONG_ENABLED = False
o_MULTIPRONG_2P_ONLY = True


o_MULTIPRONG_REINFORCER_MIN_RATIO = 1.0


o_MULTIPRONG_E_OVERKILL = 1.05

o_MULTIPRONG_CREDIBILITY_FACTOR = 0.6
o_MULTIPRONG_MAX_TRAVEL = O_MAX_TRAVEL_CAP  # was 40
o_MULTIPRONG_MIN_PER_CONTRIBUTOR = 8
o_MULTIPRONG_MAX_PARTICIPANTS = 3


o_LATE_FLUSH_REMAINING_TURNS = 25
o_LATE_FLUSH_OVERKILL_RATIO = 1.05


o_SOFT_DEADLINE_FRACTION = 0.82


o_RACE_ENABLED = True
o_RACE_HORIZON_TURNS = 18
o_RACE_MAX_NEUTRAL_DIST = 20
o_RACE_TIE_GOES_TO_LARGER = True


o_PERSONALITY_ENABLED = True
o_PERSONALITY_AGG_HIGH = 0.30
o_PERSONALITY_AGG_LOW = 0.10
o_PERSONALITY_MIN_SAMPLE = 50

o_MODE_PARAMS = {
    "patient": {
        "expand_k_opening": 2,
        "expand_max_travel_opening": 22,
        "expand_k_mid": 1,
        "expand_max_travel_mid": 14,
        "hammer_prod_share": 0.2,
        "hammer_overkill": 1.30,
        "hammer_stockpile_min": 50,
    },
    "opportunistic": {
        "expand_k_opening": 3,
        "expand_max_travel_opening": 22,
        "expand_k_mid": 2,
        "expand_max_travel_mid": 18,
        "hammer_prod_share": 0.35,
        "hammer_overkill": 1.30,
        "hammer_stockpile_min": 50,
    },
    "pressure": {
        "expand_k_opening": 3,
        "expand_max_travel_opening": 22,
        "expand_k_mid": 0,
        "expand_max_travel_mid": 9,
        "hammer_prod_share": 0.30,
        "hammer_overkill": 1.20,
        "hammer_stockpile_min": 50,
    },
}


o_MODE_PARAMS_2P = {
    "patient": {
        "expand_k_opening": 5,
        "expand_max_travel_opening": 35,
        "expand_k_mid": 4,
        "expand_max_travel_mid": 28,
        "hammer_prod_share": 0.30,
        "hammer_overkill": 1.15,
        "hammer_stockpile_min": 25,
    },
    "opportunistic": {
        "expand_k_opening": 5,
        "expand_max_travel_opening": 35,
        "expand_k_mid": 6,
        "expand_max_travel_mid": 30,
        "hammer_prod_share": 0.28,
        "hammer_overkill": 1.15,
        "hammer_stockpile_min": 25,
    },
    "pressure": {
        "expand_k_opening": 5,
        "expand_max_travel_opening": 35,
        "expand_k_mid": 2,
        "expand_max_travel_mid": 52,
        "hammer_prod_share": 0.25,
        "hammer_overkill": 1.177645,
        "hammer_stockpile_min": 25,
    },
}


o_TWO_P_PATIENT_NUDGE_TURNS = 10
o_TWO_P_PATIENT_ESCALATE_TURNS = 20
o_TWO_P_PROD_SHARE_HISTORY = 10
o_TWO_P_PROD_SHARE_PROGRESS_EPS = 0.005


o_STOP_EXPAND_2P_ENABLED = True


o_STOP_EXPAND_PROD_SHARE_2P = 0.65
o_STOP_EXPAND_TURN_MIN_2P = 30


o_COMBAT_STOP_EXPAND_ENABLED = False
o_COMBAT_STOP_EXPAND_4P_ONLY = True
o_COMBAT_STOP_EXPAND_TURN_MIN = 25
o_COMBAT_CONTACT_MIN_SHIPS = 15
o_COMBAT_CHEAP_GARRISON = 10
o_COMBAT_CHEAP_DIST = 12.0


o_PROD_LAG_STOP_EXPAND_ENABLED = False  # abolished: keep expanding even when behind on production
o_PROD_LAG_STOP_EXPAND_TURN_MIN = 25
o_PROD_LAG_STOP_EXPAND_THRESH_2P = 0.40
o_PROD_LAG_STOP_EXPAND_THRESH_4P = 0.22


o_ENEMY_TEMPO_STOP_EXPAND_ENABLED = False  # abolished: don't stop expanding just because the enemy is active
o_ENEMY_TEMPO_STOP_EXPAND_TURN_MIN = 20
o_ENEMY_TEMPO_STOP_EXPAND_MIN_LAUNCHES = 2


o_EASY_ENEMY_STOP_EXPAND_ENABLED = False
o_EASY_ENEMY_STOP_EXPAND_TURN_MIN = 15
o_EASY_ENEMY_MAX_GARRISON = 20
o_EASY_ENEMY_MAX_DIST = 25.0
o_EASY_ENEMY_MIN_COUNT = 1


o_TURN_CUTOFF_STOP_EXPAND_ENABLED = True
o_TURN_CUTOFF_STOP_EXPAND_TURN = 80


o_PROD_LEAD_STOP_EXPAND_4P_ENABLED = True
o_PROD_LEAD_STOP_EXPAND_4P_TURN_MIN = 25
o_PROD_LEAD_STOP_EXPAND_4P_THRESH = 0.35


o_STOCKPILE_STOP_EXPAND_ENABLED = False  # abolished: a big garrison shouldn't halt expansion
o_STOCKPILE_STOP_EXPAND_TURN_MIN = 20
o_STOCKPILE_STOP_EXPAND_MAX_GARRISON = 250


o_NEUTRAL_SATURATION_STOP_EXPAND_ENABLED = False
o_NEUTRAL_SATURATION_2P_ONLY = True
o_NEUTRAL_SATURATION_TURN_MIN = 20
o_NEUTRAL_SATURATION_CHEAP_GARRISON = 10
o_NEUTRAL_SATURATION_REACH_DIST = 30.0


o_Planet = namedtuple("o_Planet", ["id", "owner", "x", "y", "radius", "ships", "production"])
o_Fleet = namedtuple("o_Fleet", ["id", "owner", "x", "y", "angle", "from_planet_id", "ships"])


def o_dist(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)


def o_fleet_speed(ships):
    if ships <= 1:
        return 1.0
    ratio = math.log(ships) / math.log(1000.0)
    ratio = max(0.0, min(1.0, ratio))
    return 1.0 + (o_MAX_SPEED - 1.0) * (ratio ** 1.5)


def o_orbital_radius(p):
    return o_dist(p.x, p.y, o_CENTER_X, o_CENTER_Y)


def o_point_to_segment_distance(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    seg_sq = dx * dx + dy * dy
    if seg_sq <= 1e-9:
        return o_dist(px, py, x1, y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / seg_sq))
    return o_dist(px, py, x1 + t * dx, y1 + t * dy)


def o_segment_hits_sun(x1, y1, x2, y2):
    return o_point_to_segment_distance(o_CENTER_X, o_CENTER_Y, x1, y1, x2, y2) < o_SUN_R + o_SUN_SAFETY


def o_launch_point(sx, sy, sr, angle):
    c = sr + o_LAUNCH_CLEARANCE
    return sx + math.cos(angle) * c, sy + math.sin(angle) * c


def o_safe_geometry(sx, sy, sr, tx, ty, tr):
    angle = math.atan2(ty - sy, tx - sx)
    lx, ly = o_launch_point(sx, sy, sr, angle)
    hit_d = max(0.0, o_dist(sx, sy, tx, ty) - (sr + o_LAUNCH_CLEARANCE) - tr)
    ex = lx + math.cos(angle) * hit_d
    ey = ly + math.sin(angle) * hit_d
    if o_segment_hits_sun(lx, ly, ex, ey):
        return None
    return angle, hit_d


def o_estimate_arrival(sx, sy, sr, tx, ty, tr, ships):
    safe = o_safe_geometry(sx, sy, sr, tx, ty, tr)
    if safe is None:
        return None
    angle, total_d = safe
    turns = max(1, int(math.ceil(total_d / o_fleet_speed(max(1, ships)))))
    return angle, turns


def o_predict_planet_position(planet, initial_by_id, ang_vel, turns):
    init = initial_by_id.get(planet.id)
    if init is None:
        return planet.x, planet.y
    r = o_dist(init.x, init.y, o_CENTER_X, o_CENTER_Y)
    if r + init.radius >= o_ROTATION_LIMIT:
        return planet.x, planet.y
    cur = math.atan2(planet.y - o_CENTER_Y, planet.x - o_CENTER_X)
    new = cur + ang_vel * turns
    return o_CENTER_X + r * math.cos(new), o_CENTER_Y + r * math.sin(new)


o_R4_BEHIND_SUN_WAIT_ENABLED = True
o_R4_FUTURE_HORIZON = 10


def o_predict_comet_position(planet_id, comets, turns):
    for group in comets:
        pids = group.get("planet_ids", []) if isinstance(group, dict) else []
        if planet_id not in pids:
            continue
        idx = pids.index(planet_id)
        paths = group.get("paths", []) if isinstance(group, dict) else []
        path_index = group.get("path_index", 0) if isinstance(group, dict) else 0
        if idx >= len(paths):
            return None
        path = paths[idx]
        future_idx = int(path_index) + int(turns)
        if 0 <= future_idx < len(path):
            return float(path[future_idx][0]), float(path[future_idx][1])
        return None
    return None


def o_predict_target_position(target, world, turns):
    if target.id in world.comet_ids:
        pos = o_predict_comet_position(target.id, world.comets, turns)
        if pos is not None:
            return pos
    return o_predict_planet_position(target, world.initial_by_id, world.ang_vel, turns)


o_AIM_MAX_ITERS = 6
o_AIM_CONVERGE_TURNS = 2
o_AIM_CONVERGE_DIST = 0.6


def o_aim_at_target(src, target, ships, initial_by_id, ang_vel, world=None):
    est = o_estimate_arrival(src.x, src.y, src.radius, target.x, target.y, target.radius, ships)
    if est is None and o_R4_BEHIND_SUN_WAIT_ENABLED and world is not None:
        for future_t in range(2, o_R4_FUTURE_HORIZON, 2):
            if target.id in world.comet_ids:
                pos = o_predict_comet_position(target.id, world.comets, future_t)
            else:
                init = initial_by_id.get(target.id)
                if init is None:
                    pos = None
                elif o_dist(init.x, init.y, o_CENTER_X, o_CENTER_Y) + init.radius >= o_ROTATION_LIMIT:
                    pos = None
                else:
                    pos = o_predict_planet_position(target, initial_by_id, ang_vel, future_t)
            if pos is None:
                continue
            est = o_estimate_arrival(src.x, src.y, src.radius, pos[0], pos[1], target.radius, ships)
            if est is not None:
                break
    if est is None:
        return None

    is_comet = world is not None and target.id in world.comet_ids
    if not is_comet:
        init = initial_by_id.get(target.id)
        if init is None:
            return est
        if o_dist(init.x, init.y, o_CENTER_X, o_CENTER_Y) + init.radius >= o_ROTATION_LIMIT:
            return est

    angle, turns = est
    tx, ty = target.x, target.y
    for _ in range(o_AIM_MAX_ITERS):
        if is_comet:
            pos = o_predict_comet_position(target.id, world.comets, turns)
            if pos is None:
                return None
            ntx, nty = pos
        else:
            ntx, nty = o_predict_planet_position(target, initial_by_id, ang_vel, turns)
        nest = o_estimate_arrival(src.x, src.y, src.radius, ntx, nty, target.radius, ships)
        if nest is None:
            return None
        nangle, nturns = nest
        if (abs(ntx - tx) < o_AIM_CONVERGE_DIST
                and abs(nty - ty) < o_AIM_CONVERGE_DIST
                and abs(nturns - turns) <= o_AIM_CONVERGE_TURNS):
            return nangle, nturns
        angle, turns = nangle, nturns
        tx, ty = ntx, nty
    return None


def o_fleet_target_planet(fleet, planets, initial_by_id=None, ang_vel=0.0):
    dx_dir = math.cos(fleet.angle)
    dy_dir = math.sin(fleet.angle)
    speed = o_fleet_speed(fleet.ships)

    def _is_orbital(p):
        if initial_by_id is None:
            return False
        init = initial_by_id.get(p.id)
        if init is None:
            return False
        return o_dist(init.x, init.y, o_CENTER_X, o_CENTER_Y) + init.radius < o_ROTATION_LIMIT

    best_p, best_t = None, float(o_SIM_HORIZON) + 1.0

    for p in planets:
        if _is_orbital(p):
            continue
        dx = p.x - fleet.x
        dy = p.y - fleet.y
        proj = dx * dx_dir + dy * dy_dir
        if proj < 0:
            continue
        perp_sq = dx * dx + dy * dy - proj * proj
        rr = p.radius * p.radius
        if perp_sq >= rr:
            continue
        hit_d = max(0.0, proj - math.sqrt(max(0.0, rr - perp_sq)))
        t = hit_d / speed
        if t <= o_SIM_HORIZON and t < best_t:
            best_t, best_p = t, p

    if initial_by_id is not None:
        best_dsq = None
        max_t = int(math.ceil(min(best_t, float(o_SIM_HORIZON))))
        for t in range(1, max_t + 1):
            fx = fleet.x + dx_dir * speed * t
            fy = fleet.y + dy_dir * speed * t
            for p in planets:
                if not _is_orbital(p):
                    continue
                px, py = o_predict_planet_position(p, initial_by_id, ang_vel, t)
                rr = p.radius * p.radius
                dsq = (fx - px) ** 2 + (fy - py) ** 2
                if dsq < rr:
                    if t < best_t or (t == best_t and (best_dsq is None or dsq < best_dsq)):
                        best_t, best_p, best_dsq = float(t), p, dsq
            if best_p is not None and best_t <= t:
                break

    if best_p is None:
        return None, None
    return best_p, max(1, int(math.ceil(best_t)))


def o_garrison_at_arrival(target, travel_turns):
    # Engine truth: production is a FLOAT added each turn; don't floor the rate.
    if target.owner == -1:
        return float(target.ships)
    return float(target.ships) + float(target.production) * float(travel_turns)


def o_needed_to_capture(target, travel_turns):
    # Capture needs survivor > garrison strictly; floor(garrison)+1 is smallest int above it.
    return int(math.floor(o_garrison_at_arrival(target, travel_turns))) + 1


o_EFFECTIVE_GARRISON_ENABLED = True


def o_effective_garrison_at_arrival(target, travel_turns, world):
    if not o_EFFECTIVE_GARRISON_ENABLED:
        return target.owner, o_garrison_at_arrival(target, travel_turns)
    arrivals = world.arrivals_by_planet.get(target.id, [])
    if world.is_2p:
        relevant = sorted(
            ((eta, owner, ships) for eta, owner, ships in arrivals
             if 1 <= eta <= travel_turns and ships > 0 and owner != -1),
            key=lambda x: x[0],
        )
    else:
        relevant = sorted(
            ((eta, owner, ships) for eta, owner, ships in arrivals
             if 1 <= eta <= travel_turns and owner != world.player and ships > 0
             and owner != -1),
            key=lambda x: x[0],
        )
    if not relevant:
        return target.owner, o_garrison_at_arrival(target, travel_turns)
    owner = int(target.owner)
    ships = float(target.ships)
    prod = max(0.0, float(target.production))  # fractional production rate
    last_t = 0
    for eta, fleet_owner, fleet_ships in relevant:
        if owner != -1:
            ships += prod * (eta - last_t)
        if fleet_owner == owner:
            ships += fleet_ships
        else:
            if fleet_ships > ships:
                owner = int(fleet_owner)
                ships = fleet_ships - ships
            elif fleet_ships < ships:
                ships -= fleet_ships
            else:
                ships = 0
        last_t = eta
    if owner != -1:
        ships += prod * (travel_turns - last_t)
    return owner, ships


def o_effective_needed_to_capture(target, travel_turns, world):
    _, defender_ships = o_effective_garrison_at_arrival(target, travel_turns, world)
    return int(math.floor(defender_ships)) + 1


def o_compute_planet_reserve(planet, arrivals, player):
    if planet.owner != player:
        return 0, True, 0, None

    prod = max(0.0, float(planet.production))  # fractional production rate
    ships_now = max(0, int(planet.ships))
    if prod > 0:
        absorb_window = max(1, int(ships_now / prod))
    else:
        absorb_window = o_SIM_HORIZON

    hostile_in_window = 0
    for eta, owner, ships in arrivals:
        if ships <= 0 or owner == player or owner == -1:
            continue
        if int(eta) <= absorb_window:
            hostile_in_window += int(ships)

    absorb_min_threat = max(1, min(o_ABSORB_MIN_THREAT, ships_now // 3))
    skip_in_window_hostiles = hostile_in_window < absorb_min_threat

    friendly_events = defaultdict(int)
    hostile_by_owner = defaultdict(lambda: defaultdict(int))
    for eta, owner, ships in arrivals:
        if ships <= 0:
            continue
        if owner == player:
            friendly_events[eta] += ships
        elif owner == -1:
            continue
        else:
            if skip_in_window_hostiles and int(eta) <= absorb_window:
                continue
            hostile_by_owner[eta][owner] += int(ships)

    events = defaultdict(int)
    for eta, ships in friendly_events.items():
        events[eta] += ships
    for eta, owner_totals in hostile_by_owner.items():
        sorted_h = sorted(owner_totals.values(), reverse=True)
        if len(sorted_h) == 1:
            survivor = sorted_h[0]
        elif sorted_h[0] == sorted_h[1]:
            survivor = 0
        else:
            survivor = sorted_h[0] - sorted_h[1]
        events[eta] -= survivor

    if not events:
        return 0, True, 0, None

    growth = float(planet.production)  # fractional production rate
    bal = float(planet.ships)
    last_t = 0
    min_bal = bal
    deadline = None

    for turn in sorted(events):
        bal += growth * (turn - last_t)
        bal += events[turn]
        if bal < min_bal:
            min_bal = bal
        if bal < o_ABSORB_PROJECTION_MARGIN and deadline is None:
            deadline = turn
        last_t = turn

    if min_bal >= o_ABSORB_PROJECTION_MARGIN:
        excess = min_bal - o_ABSORB_PROJECTION_MARGIN
        reserve = max(0, int(planet.ships) - int(math.floor(excess)))
        return reserve, True, 0, None

    deficit = o_ABSORB_PROJECTION_MARGIN - min_bal
    return int(planet.ships), False, int(math.ceil(deficit)), deadline


def o_forward_project(world, our_capture_target=None, our_capture_turn=None,
                    our_capture_ships=None, horizon=20,
                    project_opponent_moves=False,
                    opponent_emit_fraction=0.4,
                    snapshot_turns=None):
    by_pid = defaultdict(list)
    for pid, arrs in world.arrivals_by_planet.items():
        for eta, owner, ships in arrs:
            if 0 < eta <= horizon:
                by_pid[pid].append((int(eta), int(owner), int(ships)))

    if our_capture_target is not None and our_capture_turn is not None:
        by_pid[our_capture_target].append(
            (int(our_capture_turn), int(world.player), int(our_capture_ships))
        )

    state = {}
    for p in world.planets:
        state[p.id] = [int(p.owner), int(p.ships), int(p.production)]

    planet_pos_map = {p.id: (float(p.x), float(p.y)) for p in world.planets}
    pid_list = list(state.keys())

    prod_by_pid = {p.id: max(0, int(p.production)) for p in world.planets}

    snapshots = {} if snapshot_turns else None
    snapshot_set = set(snapshot_turns) if snapshot_turns else None
    for t in range(1, horizon + 1):
        for pid, st in state.items():
            if st[0] != -1:
                st[1] += st[2]

        if project_opponent_moves and t % 4 == 0:
            for pid, st in state.items():
                if st[0] == -1 or st[1] < 10:
                    continue
                src_x, src_y = planet_pos_map[pid]
                src_owner = st[0]
                best_d = float("inf")
                best_op = None
                for opid, ost in state.items():
                    if opid == pid or ost[0] == src_owner:
                        continue
                    ox, oy = planet_pos_map[opid]
                    d = ((src_x - ox) ** 2 + (src_y - oy) ** 2) ** 0.5
                    if d < best_d:
                        best_d, best_op = d, opid
                if best_op is None:
                    continue
                if src_owner == world.player:
                    frac = opponent_emit_fraction * 0.5
                else:
                    frac = opponent_emit_fraction
                emit = int(st[1] * frac)
                if emit < 5:
                    continue
                ratio = math.log(max(2, emit)) / math.log(1000.0)
                speed = 1.0 + (o_MAX_SPEED - 1.0) * (ratio ** 1.5)
                eta_arrive = max(1, int(math.ceil(best_d / speed)))
                arrival_t = t + eta_arrive
                if arrival_t > horizon:
                    continue
                by_pid[best_op].append((arrival_t, src_owner, emit))
                st[1] -= emit

        for pid, arrs in by_pid.items():
            this_turn = [(o, s) for et, o, s in arrs if et == t]
            if not this_turn:
                continue
            st = state[pid]
            defender_owner, garrison = st[0], st[1]
            from_owner = defaultdict(int)
            for o, s in this_turn:
                from_owner[o] += s
            sorted_owners = sorted(from_owner.items(), key=lambda x: -x[1])
            top_owner, top_ships = sorted_owners[0]
            if len(sorted_owners) >= 2:
                second_ships = sorted_owners[1][1]
                if top_ships == second_ships:
                    survivor_ships = 0
                    survivor_owner = -1
                else:
                    survivor_ships = top_ships - second_ships
                    survivor_owner = top_owner
            else:
                survivor_ships = top_ships
                survivor_owner = top_owner
            if survivor_ships > 0:
                if defender_owner == survivor_owner:
                    st[1] = garrison + survivor_ships
                else:
                    new_garrison = garrison - survivor_ships
                    if new_garrison < 0:
                        st[0] = survivor_owner
                        st[1] = -new_garrison
                    else:
                        st[1] = new_garrison
        if snapshot_set is not None and t in snapshot_set:
            snapshots[t] = {pid: (st[0], st[1]) for pid, st in state.items()}

    final = {pid: (st[0], st[1]) for pid, st in state.items()}
    if snapshot_turns is not None:
        return final, snapshots
    return final


def o__depth2_penalty(world, our_action, top_opp_actions=2):
    target_id = our_action["target_id"]
    tgt = world.planet_by_id.get(target_id)
    if tgt is None:
        return 0.0

    proj = o_forward_project(
        world,
        our_capture_target=our_action["target_id"],
        our_capture_turn=our_action["arrival_turn"],
        our_capture_ships=our_action["ships"],
        horizon=o_FWD_SIM_HORIZON + 6,
        project_opponent_moves=True,
        opponent_emit_fraction=0.30,
    )
    end_owner, end_ships = proj.get(target_id, (-1, 0))

    worst_delta = 0.0
    candidates_evaluated = 0
    for ep in world.planets:
        if ep.owner == world.player or ep.owner == -1:
            continue
        if int(ep.ships) < 9:
            continue
        d = ((tgt.x - ep.x) ** 2 + (tgt.y - ep.y) ** 2) ** 0.5
        if d > 30.0:
            continue
        opp_ships = max(8, int(ep.ships) - 5)
        ratio = math.log(max(2, opp_ships)) / math.log(1000.0)
        speed = 1.0 + (o_MAX_SPEED - 1.0) * (ratio ** 1.5)
        opp_eta = max(1, int(math.ceil(d / speed)))
        if opp_eta > o_FWD_SIM_HORIZON + 4:
            continue
        if end_owner != world.player and opp_ships > end_ships:
            worst_delta = min(worst_delta, -opp_ships)
        candidates_evaluated += 1
        if candidates_evaluated >= top_opp_actions:
            break
    return worst_delta


def _o_territory_gain(world, target_id):
    """Territory bias for the old bot's melis-based expansion: favor home and
    frontier targets, penalize non-frontier so we don't scatter sideways."""
    if _home_quadrant is None:
        return 0.0
    tp = world.planet_by_id.get(int(target_id))
    if tp is None:
        return 0.0
    # Scale: o_forward_score gives +8 per production point, so these are sized
    # in "production points" — home ~1pt favor, frontier ~0.5pt, non-frontier a
    # ~1.25pt penalty once the land-grab is over (turn >= 50).
    tq = _get_quadrant(tp)
    fq = _frontier_quadrant(_home_quadrant, world.ang_vel)
    if tq == _home_quadrant:
        return 8.0
    if tq == fq:
        return 4.0
    return -4.0 if world.step < 50 else -10.0


def _o_territory_dist_bias(world, planet):
    """Distance-unit territory bias (smaller = preferred). Mirrors
    o__nearest_targets so cheap-pickup also favors home/frontier and
    deprioritizes scattering into non-frontier quadrants."""
    if _home_quadrant is None:
        return 0.0
    tq = _get_quadrant(planet)
    fq = _frontier_quadrant(_home_quadrant, world.ang_vel)
    if tq == _home_quadrant:
        return -8.0
    if tq == fq:
        return -3.0
    return 8.0 if world.step < 50 else 15.0


def o_search_step_action(world, max_per_source=3, max_actions_to_eval=10,
                       use_depth2=False):
    actions = o_generate_step_actions(world, max_per_source=max_per_source)
    if not actions:
        return []
    baseline_score = o_melis_evaluate(world, our_step_action=None)
    apply_decay = world.is_2p
    scored = []
    for act in actions[:max_actions_to_eval]:
        act_score = o_melis_evaluate(world, our_step_action=act)
        gain = act_score - baseline_score
        if apply_decay and gain > 0:
            gain *= 0.97 ** int(act["arrival_turn"])
        gain += _o_territory_gain(world, act["target_id"])  # favor home/frontier
        act["score"] = gain
        scored.append(act)
    scored.sort(key=lambda a: (-a["score"], a.get("raw_dist", 0.0)))
    if use_depth2:
        for act in scored[:3]:
            act["score"] += o__depth2_penalty(world, act)
        scored.sort(key=lambda a: (-a["score"], a.get("raw_dist", 0.0)))
    if o_MELIS_SANITY_ENABLED and world.is_2p and scored and scored[0]["score"] < o_MELIS_SANITY_THETA:
        return []
    return scored


def o_generate_step_actions(world, max_per_source=3):
    actions = []
    if not world.my_planets:
        return actions
    is_opening = world.is_opening
    if is_opening:
        max_travel = world.mode_params.get(
            "expand_max_travel_opening", o_EXPAND_MAX_TRAVEL_OPENING)
    else:
        max_travel = world.mode_params["expand_max_travel_mid"]
    max_travel = min(max_travel, O_MAX_TRAVEL_CAP)  # no long-distance fleets

    for src in world.my_planets:
        avail = max(0, int(src.ships))
        if avail < o_MIN_DISPATCH_SHIPS:
            continue
        targets = []
        for t in world.planets:
            if t.owner == world.player:
                continue
            if not o_is_targetable(world, t):
                continue
            if o__neutral_blocked_by_cap(world, t):
                continue
            raw = o_dist(src.x, src.y, t.x, t.y)
            if raw / o_MAX_SPEED > max_travel + 4:
                continue
            targets.append((raw, t))
        targets.sort(key=lambda x: x[0])
        if o_F16_DIVERSITY_ENABLED:
            n_close = min(o_F16_CLOSEST_PICKS, max_per_source)
            picks = list(targets[:n_close])
            picked_ids = {p[1].id for p in picks}
            extras = [(raw, t) for raw, t in targets if t.id not in picked_ids]
            extras.sort(key=lambda x: (-int(x[1].production), x[0]))
            picks.extend(extras[:o_F16_PROD_PICKS])
        else:
            picks = targets[:max_per_source]
        for raw, t in picks:
            plan = o_plan_solo_capture(world, src, t, avail, max_travel)
            if plan is None:
                continue
            angle, turns, ships = plan
            actions.append({
                "target_id": int(t.id),
                "source_id": int(src.id),
                "angle": float(angle),
                "arrival_turn": int(turns),
                "ships": int(ships),
                "raw_dist": float(raw),
            })
    actions.sort(key=lambda a: (-world.planet_by_id[a["target_id"]].production, a["raw_dist"]))
    return actions


def o_melis_evaluate(world, our_step_action=None, horizon=12, future_horizon=8,
                   opp_emit=0.20):
    target = arrival = ships = None
    if our_step_action is not None:
        target = our_step_action.get("target_id")
        arrival = our_step_action.get("arrival_turn")
        ships = our_step_action.get("ships")
    H = horizon + future_horizon
    n = 2 if world.is_2p else 4
    if o_FWD_SCORE_AGG_ENABLED:
        snap_turns = tuple(t for t in o_FWD_SCORE_AGG_TURNS if t <= H)
        if not snap_turns:
            snap_turns = (H,)
        final, snaps = o_forward_project(
            world,
            our_capture_target=target,
            our_capture_turn=arrival,
            our_capture_ships=ships,
            horizon=H,
            project_opponent_moves=True,
            opponent_emit_fraction=opp_emit,
            snapshot_turns=snap_turns,
        )
        total = 0.0
        count = 0
        for t in snap_turns:
            snap = snaps.get(t)
            if snap is None:
                continue
            total += o_forward_score(snap, world.player, n, world)
            count += 1
        if H not in snap_turns:
            total += o_forward_score(final, world.player, n, world)
            count += 1
        return total / max(1, count)
    state = o_forward_project(
        world,
        our_capture_target=target,
        our_capture_turn=arrival,
        our_capture_ships=ships,
        horizon=H,
        project_opponent_moves=True,
        opponent_emit_fraction=opp_emit,
    )
    return o_forward_score(state, world.player, n, world)


def o_forward_score(state, player, n_seats, world=None):
    n_planets = [0] * n_seats
    n_prod = [0] * n_seats
    n_ships = [0] * n_seats
    for pid, (o, s) in state.items():
        if 0 <= o < n_seats:
            n_ships[o] += s
            n_planets[o] += 1
            if world is not None:
                p = world.planet_by_id.get(pid)
                if p is not None:
                    n_prod[o] += int(p.production)
    if n_seats <= 1:
        return n_ships[player]
    others = [i for i in range(n_seats) if i != player]
    leader_ships = max(n_ships[i] for i in others)
    leader_planets = max(n_planets[i] for i in others)
    leader_prod = max(n_prod[i] for i in others)
    return ((n_ships[player] - leader_ships)
            + 5 * (n_planets[player] - leader_planets)
            + 8 * (n_prod[player] - leader_prod))


class o_World:
    def __init__(self, obs, inferred_step=None):
        global o_COALITION_MIN_PER_CONTRIBUTOR, o_DEFENSE_OVERSEND, o_PSM_OPENING_TURN, o_SO1_STATIC_BONUS
        self.player = o__read(obs, "player", 0)
        obs_step = o__read(obs, "step", 0) or 0
        self.step = max(obs_step, inferred_step or 0)
        raw_planets = o__read(obs, "planets", []) or []
        raw_fleets = o__read(obs, "fleets", []) or []
        raw_init = o__read(obs, "initial_planets", []) or []
        self.ang_vel = o__read(obs, "angular_velocity", 0.0) or 0.0

        self.planets = [o_Planet(*p) for p in raw_planets]
        self.fleets = [o_Fleet(*f) for f in raw_fleets]
        self.initial_by_id = {o_Planet(*p).id: o_Planet(*p) for p in raw_init}

        raw_comet_ids = o__read(obs, "comet_planet_ids", []) or []
        self.comet_ids = set(int(x) for x in raw_comet_ids)

        self.comet_remaining = {}
        raw_comet_groups = o__read(obs, "comets", []) or []

        self.comets = raw_comet_groups
        for grp in raw_comet_groups:
            try:
                idx = int(grp.get("path_index", 0))
                pids = grp.get("planet_ids", []) or []
                paths = grp.get("paths", []) or []
                for i, pid in enumerate(pids):
                    if i < len(paths):
                        rem = max(0, len(paths[i]) - idx)
                        self.comet_remaining[int(pid)] = rem
            except (AttributeError, TypeError, IndexError):
                continue

        self.planet_by_id = {p.id: p for p in self.planets}
        self.my_planets = [p for p in self.planets if p.owner == self.player]
        self.enemy_planets = [p for p in self.planets if p.owner not in (-1, self.player)]
        self.neutral_planets = [p for p in self.planets if p.owner == -1]

        self.remaining_steps = max(1, o_TOTAL_STEPS - self.step)
        self.is_opening = self.step < o_PSM_OPENING_TURN
        self.is_late = self.remaining_steps < o_LATE_FLUSH_REMAINING_TURNS

        self.owner_strength = defaultdict(int)
        self.owner_production = defaultdict(int)
        for p in self.planets:
            if p.owner != -1:
                self.owner_strength[p.owner] += int(p.ships)
                self.owner_production[p.owner] += int(p.production)
        for f in self.fleets:
            self.owner_strength[f.owner] += int(f.ships)

        self.my_prod = self.owner_production.get(self.player, 0)
        self.total_prod = sum(self.owner_production.values())
        self.my_prod_share = (self.my_prod / self.total_prod) if self.total_prod else 0.0

        if self.remaining_steps < 80 and self.my_prod_share > 0.55:
            self.is_late = True

        self.leader_id = None
        self.contest_leader = False

        self.owner_planet_count = defaultdict(int)
        for p in self.planets:
            if p.owner not in (-1,):
                self.owner_planet_count[p.owner] += 1
        self.weakest_enemy = None
        self.weakest_enemy_prod_share = 0.0
        if self.total_prod > 0:
            best_score = None
            for owner in self.owner_production.keys():
                if owner in (-1, self.player):
                    continue
                score = (
                    self.owner_production.get(owner, 0) * 0.5
                    + self.owner_strength.get(owner, 0) * 0.3
                    + self.owner_planet_count.get(owner, 0) * 0.2
                )
                if best_score is None or score < best_score:
                    best_score = score
                    self.weakest_enemy = owner
            if self.weakest_enemy is not None:
                their_prod = self.owner_production.get(self.weakest_enemy, 0)
                self.weakest_enemy_prod_share = (
                    their_prod / self.total_prod if self.total_prod else 0.0
                )

        self.arrivals_by_planet = defaultdict(list)
        for f in self.fleets:
            target, eta = o_fleet_target_planet(f, self.planets, self.initial_by_id, self.ang_vel)
            if target is None:
                continue
            self.arrivals_by_planet[target.id].append((eta, int(f.owner), int(f.ships)))

        self.enemy_race_eta = o__compute_enemy_race_eta(self) if o_RACE_ENABLED else {}

        global o__game_num_players
        if o__game_num_players is None and self.planets:
            o__game_num_players = self.num_players
        self.is_2p = (o__game_num_players == 2)

        if self.is_2p:
            o_COALITION_MIN_PER_CONTRIBUTOR = o_COALITION_MIN_PER_CONTRIBUTOR_2P
            o_DEFENSE_OVERSEND = o_DEFENSE_OVERSEND_2P
            o_PSM_OPENING_TURN = o_PSM_OPENING_TURN_2P
            o_SO1_STATIC_BONUS = o_SO1_STATIC_BONUS_2P
        else:
            o_COALITION_MIN_PER_CONTRIBUTOR = o_COALITION_MIN_PER_CONTRIBUTOR_4P
            o_DEFENSE_OVERSEND = o_DEFENSE_OVERSEND_4P
            o_PSM_OPENING_TURN = o_PSM_OPENING_TURN_4P
            o_SO1_STATIC_BONUS = o_SO1_STATIC_BONUS_4P

        if o_LEADER_BASH_ENABLED and not self.is_2p:
            lead_scores = {}
            for owner in self.owner_production.keys():
                if owner == -1:
                    continue
                lead_scores[owner] = (
                    self.owner_strength.get(owner, 0) * 0.5
                    + self.owner_production.get(owner, 0) * 0.5
                )
            if lead_scores:
                top_owner = max(lead_scores, key=lambda k: lead_scores[k])
                self.leader_id = top_owner
                my_score = lead_scores.get(self.player, 0)
                top_score = lead_scores.get(top_owner, 0)
                if (
                    top_owner != self.player
                    and my_score > 0
                    and (top_score / my_score) >= o_LEADER_BASH_RATIO
                ):
                    self.contest_leader = True

        self.mode = o__detect_mode(self) if o_PERSONALITY_ENABLED else "patient"

        if o_TERMINAL_PHASE_ENABLED and self.remaining_steps < o_TERMINAL_PHASE_TURNS:
            self.mode = "pressure"
        params_table = o_MODE_PARAMS_2P if self.is_2p else o_MODE_PARAMS
        self.mode_params = params_table[self.mode]

        self.stop_expanding_2p = (
            o_STOP_EXPAND_2P_ENABLED
            and self.is_2p
            and self.step >= o_STOP_EXPAND_TURN_MIN_2P
            and self.my_prod_share >= o_STOP_EXPAND_PROD_SHARE_2P
        )

        self.in_combat_contact = False
        if o_COMBAT_STOP_EXPAND_ENABLED:
            my_ids = {p.id for p in self.my_planets}
            enemy_ids = {p.id for p in self.enemy_planets}
            for pid, arrs in self.arrivals_by_planet.items():
                if pid in my_ids:
                    for _eta, owner, ships in arrs:
                        if owner != self.player and owner != -1 and ships >= o_COMBAT_CONTACT_MIN_SHIPS:
                            self.in_combat_contact = True
                            break
                elif pid in enemy_ids:
                    for _eta, owner, ships in arrs:
                        if owner == self.player and ships >= o_COMBAT_CONTACT_MIN_SHIPS:
                            self.in_combat_contact = True
                            break
                if self.in_combat_contact:
                    break
        self.combat_stop_expand = (
            o_COMBAT_STOP_EXPAND_ENABLED
            and self.in_combat_contact
            and self.step >= o_COMBAT_STOP_EXPAND_TURN_MIN
            and (not o_COMBAT_STOP_EXPAND_4P_ONLY or not self.is_2p)
        )

        prod_lag_thresh = (
            o_PROD_LAG_STOP_EXPAND_THRESH_2P if self.is_2p
            else o_PROD_LAG_STOP_EXPAND_THRESH_4P
        )
        self.prod_lag_stop_expand = (
            o_PROD_LAG_STOP_EXPAND_ENABLED
            and self.step >= o_PROD_LAG_STOP_EXPAND_TURN_MIN
            and self.my_prod_share < prod_lag_thresh
        )

        self.enemy_tempo_stop_expand = (
            o_ENEMY_TEMPO_STOP_EXPAND_ENABLED
            and self.step >= o_ENEMY_TEMPO_STOP_EXPAND_TURN_MIN
            and o_FLEET_INTENT_ENABLED
            and len(o__enemy_recently_launched) >= o_ENEMY_TEMPO_STOP_EXPAND_MIN_LAUNCHES
        )

        self.easy_enemy_stop_expand = False
        if o_EASY_ENEMY_STOP_EXPAND_ENABLED and self.step >= o_EASY_ENEMY_STOP_EXPAND_TURN_MIN:
            easy_count = 0
            for ep in self.enemy_planets:
                if int(ep.ships) > o_EASY_ENEMY_MAX_GARRISON:
                    continue
                for mp in self.my_planets:
                    if o_dist(mp.x, mp.y, ep.x, ep.y) <= o_EASY_ENEMY_MAX_DIST:
                        easy_count += 1
                        break
                if easy_count >= o_EASY_ENEMY_MIN_COUNT:
                    break
            self.easy_enemy_stop_expand = (easy_count >= o_EASY_ENEMY_MIN_COUNT)

        self.stockpile_stop_expand = False
        if o_STOCKPILE_STOP_EXPAND_ENABLED and self.step >= o_STOCKPILE_STOP_EXPAND_TURN_MIN:
            for mp in self.my_planets:
                if int(mp.ships) >= o_STOCKPILE_STOP_EXPAND_MAX_GARRISON:
                    self.stockpile_stop_expand = True
                    break

        self.prod_lead_stop_expand_4p = (
            o_PROD_LEAD_STOP_EXPAND_4P_ENABLED
            and not self.is_2p
            and self.step >= o_PROD_LEAD_STOP_EXPAND_4P_TURN_MIN
            and self.my_prod_share >= o_PROD_LEAD_STOP_EXPAND_4P_THRESH
        )

        self.turn_cutoff_stop_expand = (
            o_TURN_CUTOFF_STOP_EXPAND_ENABLED
            and self.step >= o_TURN_CUTOFF_STOP_EXPAND_TURN
        )

        self.neutral_saturation_stop_expand = False
        if (
            o_NEUTRAL_SATURATION_STOP_EXPAND_ENABLED
            and self.step >= o_NEUTRAL_SATURATION_TURN_MIN
            and (not o_NEUTRAL_SATURATION_2P_ONLY or self.is_2p)
        ):
            any_cheap = False
            for n in self.planets:
                if n.owner != -1 or n.id in self.comet_ids:
                    continue
                if int(n.ships) > o_NEUTRAL_SATURATION_CHEAP_GARRISON:
                    continue
                for mp in self.my_planets:
                    if o_dist(mp.x, mp.y, n.x, n.y) <= o_NEUTRAL_SATURATION_REACH_DIST:
                        any_cheap = True
                        break
                if any_cheap:
                    break
            self.neutral_saturation_stop_expand = not any_cheap

        self.stop_expand_lax = (
            self.combat_stop_expand
            or self.prod_lag_stop_expand
            or self.enemy_tempo_stop_expand
            or self.easy_enemy_stop_expand
            or self.neutral_saturation_stop_expand
            or self.stockpile_stop_expand
        )

        self.focus_enemy_2p = None
        if o_F14_4A_2P_FOCUS_ENABLED and self.is_2p:
            for o in self.owner_production.keys():
                if o not in (-1, self.player):
                    self.focus_enemy_2p = o
                    break

    @property
    def num_players(self):
        owners = set()
        for p in self.planets:
            if p.owner != -1:
                owners.add(p.owner)
        for f in self.fleets:
            owners.add(f.owner)
        return max(2, len(owners))


def o__read(obs, key, default=None):
    if isinstance(obs, dict):
        return obs.get(key, default)
    return getattr(obs, key, default)


def o__compute_enemy_race_eta(world):
    out = {}
    if not world.neutral_planets:
        return out

    for n in world.neutral_planets:
        needed = int(n.ships) + 1
        earliest = None

        for eta, owner, ships in world.arrivals_by_planet.get(n.id, []):
            if owner == world.player or owner == -1:
                continue
            if ships < needed:
                continue
            if earliest is None or eta < earliest:
                earliest = int(eta)

        for ep in world.enemy_planets:
            if int(ep.ships) < needed:
                continue
            d = o_dist(ep.x, ep.y, n.x, n.y)
            if d > o_RACE_MAX_NEUTRAL_DIST:
                continue
            if o_safe_geometry(ep.x, ep.y, ep.radius, n.x, n.y, n.radius) is None:
                continue
            min_turns = max(1, int(math.ceil(d / o_fleet_speed(int(ep.ships)))))
            if min_turns > o_RACE_HORIZON_TURNS:
                continue
            if earliest is None or min_turns < earliest:
                earliest = min_turns

        if earliest is not None:
            out[n.id] = earliest
    return out


def o__detect_mode(world):
    if world.is_opening:
        if world.is_2p:
            o__record_2p_progress(world.my_prod_share, intended_patient=True, reset=True)
        return "patient"

    enemy_planet_ships = 0
    for p in world.planets:
        if p.owner not in (-1, world.player):
            enemy_planet_ships += int(p.ships)
    enemy_fleet_ships = 0
    for f in world.fleets:
        if f.owner != world.player and f.owner != -1:
            enemy_fleet_ships += int(f.ships)

    enemy_total = enemy_planet_ships + enemy_fleet_ships
    if enemy_total < o_PERSONALITY_MIN_SAMPLE:
        intended = "patient"
    else:
        aggression = enemy_fleet_ships / float(enemy_total)
        if aggression >= o_PERSONALITY_AGG_HIGH:
            intended = "pressure"
        elif aggression <= o_PERSONALITY_AGG_LOW:
            intended = "opportunistic"
        else:
            intended = "patient"

    if not world.is_2p:
        return intended

    o__record_2p_progress(world.my_prod_share, intended_patient=(intended == "patient"))
    return "pressure"


def o__record_2p_progress(my_prod_share, intended_patient, reset=False):
    global o__2p_patient_streak, o__2p_prod_share_history
    if reset:
        o__2p_patient_streak = 0
        o__2p_prod_share_history = []
        return 0
    o__2p_prod_share_history.append(float(my_prod_share))
    if len(o__2p_prod_share_history) > o_TWO_P_PROD_SHARE_HISTORY:
        o__2p_prod_share_history.pop(0)
    if not intended_patient:
        o__2p_patient_streak = 0
        return 0
    if len(o__2p_prod_share_history) >= o_TWO_P_PROD_SHARE_HISTORY:
        delta = o__2p_prod_share_history[-1] - o__2p_prod_share_history[0]
        if delta > o_TWO_P_PROD_SHARE_PROGRESS_EPS:
            o__2p_patient_streak = 0
            return 0
    o__2p_patient_streak += 1
    return o__2p_patient_streak


o__agent_step = 0
o__hammer_plan = None
o__planet_idle_counts = {}
o__promoted_stockpiles = set()
o__game_num_players = None
o__2p_patient_streak = 0
o__2p_prod_share_history = []


o__neutral_prev_ships = {}
o__neutral_wounded = set()


o__enemy_prev_ships = {}
o__enemy_recently_launched = set()


o__planet_prev_owner = {}
o__freshly_lost_planets = set()

o__freshly_captured_planets = set()
o__planet_capture_age = {}


o__pending_commitments = []


o_OPP_PROFILE_WINDOW = 20
o__opp_profile = {}


def o__update_opp_profile_4p(world):
    global o__opp_profile
    if world.step == 0:
        o__opp_profile = {}

    plan_ships = defaultdict(int)
    plan_max = defaultdict(int)
    plan_count = defaultdict(int)
    for p in world.planets:
        if p.owner == world.player or p.owner == -1:
            continue
        s = int(p.ships)
        plan_ships[p.owner] += s
        plan_count[p.owner] += 1
        if s > plan_max[p.owner]:
            plan_max[p.owner] = s
    fleet_ships = defaultdict(int)
    for f in world.fleets:
        if f.owner == world.player or f.owner == -1:
            continue
        fleet_ships[f.owner] += int(f.ships)

    enemies = set(plan_count.keys()) | set(fleet_ships.keys())
    for owner in enemies:
        ps = plan_ships.get(owner, 0)
        fs = fleet_ships.get(owner, 0)
        total = ps + fs
        emit = (fs / total) if total else 0.0
        prof = o__opp_profile.setdefault(owner, {"emit": [], "stock": [], "plan": []})
        prof["emit"].append(emit)
        prof["stock"].append(plan_max.get(owner, 0))
        prof["plan"].append(plan_count.get(owner, 0))
        if len(prof["emit"]) > o_OPP_PROFILE_WINDOW:
            prof["emit"] = prof["emit"][-o_OPP_PROFILE_WINDOW:]
            prof["stock"] = prof["stock"][-o_OPP_PROFILE_WINDOW:]
            prof["plan"] = prof["plan"][-o_OPP_PROFILE_WINDOW:]

    world.opp_profile = o__opp_profile


def o_predict_defender_at_arrival(world, target, arrival_turn):
    arrivals = world.arrivals_by_planet.get(target.id, [])
    by_turn = defaultdict(list)
    for eta, owner, ships in arrivals:
        if ships <= 0:
            continue
        by_turn[eta].append((owner, ships))

    owner = target.owner
    garrison = float(target.ships)
    horizon = max(1, int(math.ceil(arrival_turn)))

    for t in range(1, horizon + 1):
        if owner != -1:
            garrison += float(target.production)  # fractional production rate
        group = by_turn.get(t)
        if group:
            owner, garrison = o__resolve_combat(owner, garrison, group)
    return owner, max(0.0, garrison)


def o__resolve_combat(owner, garrison, arrivals):
    by_owner = defaultdict(int)
    for o, s in arrivals:
        by_owner[o] += s
    if not by_owner:
        return owner, max(0.0, garrison)
    sorted_o = sorted(by_owner.items(), key=lambda kv: kv[1], reverse=True)
    top_o, top_s = sorted_o[0]
    if len(sorted_o) > 1 and top_s == sorted_o[1][1]:
        survivor_o, survivor_s = -1, 0
    elif len(sorted_o) > 1:
        survivor_o, survivor_s = top_o, top_s - sorted_o[1][1]
    else:
        survivor_o, survivor_s = top_o, top_s

    if survivor_s <= 0:
        return owner, max(0.0, garrison)
    if owner == survivor_o:
        return owner, garrison + survivor_s
    garrison -= survivor_s
    if garrison < 0:
        return survivor_o, -garrison
    return owner, garrison


o_FWD_SIM_ENABLED = os.environ.get("V128_FWD_SIM", "1") != "0"
o_FWD_LOOKAHEAD_HORIZON = 25
o_FWD_LOOKAHEAD_TOP_K = 6
o_FWD_MAX_FLEETS = 80


def o__fwd_clone(world):
    planet_ids = []
    planet_owner = {}
    planet_ships = {}
    planet_xy = {}
    planet_radius = {}
    planet_prod = {}
    orbital = {}
    for p in world.planets:
        if p.id in world.comet_ids:
            continue
        planet_ids.append(p.id)
        planet_owner[p.id] = int(p.owner)
        planet_ships[p.id] = float(p.ships)
        planet_xy[p.id] = (float(p.x), float(p.y))
        planet_radius[p.id] = float(p.radius)
        planet_prod[p.id] = int(p.production)
        init = world.initial_by_id.get(p.id)
        if init is not None:
            dx = float(init.x) - o_CENTER_X
            dy = float(init.y) - o_CENTER_Y
            r = math.sqrt(dx * dx + dy * dy)
            if r + p.radius < o_ROTATION_LIMIT:
                orbital[p.id] = (r, math.atan2(dy, dx))
    fleets = []
    next_id = 0
    for f in world.fleets:
        fleets.append([int(f.id), int(f.owner), float(f.x), float(f.y),
                       float(f.angle), int(f.ships)])
        next_id = max(next_id, int(f.id))
    return {
        "planet_ids": planet_ids,
        "planet_owner": planet_owner,
        "planet_ships": planet_ships,
        "planet_xy": planet_xy,
        "planet_radius": planet_radius,
        "planet_prod": planet_prod,
        "orbital": orbital,
        "fleets": fleets,
        "step": int(world.step),
        "ang_vel": float(world.ang_vel),
        "next_fleet_id": next_id + 1,
    }


def o__fwd_inject_launch(state, src_id, angle, ships):
    if src_id not in state["planet_xy"]:
        return False
    if state["planet_ships"][src_id] < ships:
        return False
    state["planet_ships"][src_id] -= ships
    radius = state["planet_radius"][src_id]
    sx, sy = state["planet_xy"][src_id]
    fx = sx + math.cos(angle) * (radius + 0.1)
    fy = sy + math.sin(angle) * (radius + 0.1)
    owner = state["planet_owner"][src_id]
    state["fleets"].append([state["next_fleet_id"], int(owner), fx, fy,
                            float(angle), int(ships)])
    state["next_fleet_id"] += 1
    return True


def o__fwd_step(state):
    for pid in state["planet_ids"]:
        if state["planet_owner"][pid] != -1:
            state["planet_ships"][pid] += state["planet_prod"][pid]
    combat = {pid: [] for pid in state["planet_ids"]}
    surviving = []
    radii = state["planet_radius"]
    xy = state["planet_xy"]
    pids = state["planet_ids"]
    for fl in state["fleets"]:
        ships = fl[5]
        if ships <= 0:
            continue
        speed = o_fleet_speed(ships)
        old_x, old_y = fl[2], fl[3]
        new_x = old_x + math.cos(fl[4]) * speed
        new_y = old_y + math.sin(fl[4]) * speed
        fl[2] = new_x
        fl[3] = new_y
        if not (0.0 <= new_x <= o_BOARD and 0.0 <= new_y <= o_BOARD):
            continue
        if o_point_to_segment_distance(o_CENTER_X, o_CENTER_Y, old_x, old_y, new_x, new_y) < o_SUN_R:
            continue
        hit_pid = -1
        for pid in pids:
            px, py = xy[pid]
            if o_point_to_segment_distance(px, py, old_x, old_y, new_x, new_y) < radii[pid]:
                hit_pid = pid
                break
        if hit_pid >= 0:
            combat[hit_pid].append(fl)
        else:
            surviving.append(fl)
    state["step"] += 1
    new_xy = dict(xy)
    for pid, (r, a0) in state["orbital"].items():
        a = a0 + state["ang_vel"] * state["step"]
        new_xy[pid] = (o_CENTER_X + r * math.cos(a), o_CENTER_Y + r * math.sin(a))
    still = []
    for fl in surviving:
        hit_pid = -1
        for pid in pids:
            if pid not in state["orbital"]:
                continue
            old_px, old_py = xy[pid]
            new_px, new_py = new_xy[pid]
            if o_point_to_segment_distance(fl[2], fl[3], old_px, old_py, new_px, new_py) < radii[pid]:
                hit_pid = pid
                break
        if hit_pid >= 0:
            combat[hit_pid].append(fl)
        else:
            still.append(fl)
    state["planet_xy"] = new_xy
    state["fleets"] = still
    for pid, arrivals in combat.items():
        if not arrivals:
            continue
        per_owner = defaultdict(int)
        for fl in arrivals:
            per_owner[fl[1]] += fl[5]
        sorted_o = sorted(per_owner.items(), key=lambda kv: kv[1], reverse=True)
        top_o, top_s = sorted_o[0]
        if len(sorted_o) > 1:
            second_s = sorted_o[1][1]
            if top_s == second_s:
                surv_s, surv_o = 0, -1
            else:
                surv_s, surv_o = top_s - second_s, top_o
        else:
            surv_o, surv_s = top_o, top_s
        if surv_s > 0:
            cur = state["planet_owner"][pid]
            if cur == surv_o:
                state["planet_ships"][pid] += surv_s
            else:
                state["planet_ships"][pid] -= surv_s
                if state["planet_ships"][pid] < 0:
                    state["planet_owner"][pid] = surv_o
                    state["planet_ships"][pid] = -state["planet_ships"][pid]


def o__fwd_simulate(state, horizon):
    for _ in range(horizon):
        if len(state["fleets"]) > o_FWD_MAX_FLEETS:
            break
        o__fwd_step(state)
    return state


def o__fwd_my_score(state, player):
    total = 0.0
    for pid in state["planet_ids"]:
        if state["planet_owner"][pid] == player:
            total += state["planet_ships"][pid]
    for fl in state["fleets"]:
        if fl[1] == player:
            total += fl[5]
    return total


def o__fwd_capture_holds_2p(world, src, target, angle, turns, ships, my_player):
    state = o__fwd_clone(world)
    if not o__fwd_inject_launch(state, src.id, angle, int(ships)):
        return True
    horizon = int(turns) + 15
    o__fwd_simulate(state, horizon)
    return state["planet_owner"].get(target.id) == my_player


def o_is_targetable(world, target):
    if target.id in world.comet_ids:
        return False
    if target.owner == -1:
        my_arrivals = sorted(
            ((eta, ships) for eta, owner, ships
             in world.arrivals_by_planet.get(target.id, [])
             if owner == world.player),
            key=lambda x: x[0],
        )
        if my_arrivals:
            total_ships = sum(s for _, s in my_arrivals)
            last_eta = my_arrivals[-1][0]
            if total_ships > o_garrison_at_arrival(target, last_eta):
                return False
        if o__neutral_blocked_by_cap(world, target):
            return False
        if (o_LOW_PROD_NEUTRAL_SKIP_ENABLED
                and int(target.production) <= o_LOW_PROD_NEUTRAL_SKIP_PROD
                and int(target.ships) >= o_LOW_PROD_NEUTRAL_SKIP_GARRISON):
            return False
    return True


def o__update_neutral_watchlist(world):
    o__neutral_wounded.clear()
    if o_NEUTRAL_HARD_CAP_ENABLED:
        for p in world.neutral_planets:
            prev = o__neutral_prev_ships.get(p.id)
            cur = int(p.ships)
            if prev is not None and (prev - cur) >= o_NEUTRAL_WATCHLIST_MIN_DROP:
                o__neutral_wounded.add(p.id)
    o__neutral_prev_ships.clear()
    for p in world.neutral_planets:
        o__neutral_prev_ships[p.id] = int(p.ships)

    if o_FLEET_INTENT_ENABLED:
        o__enemy_recently_launched.clear()
        for p in world.enemy_planets:
            prev = o__enemy_prev_ships.get(p.id)
            cur = int(p.ships)
            if prev is not None:
                expected = prev + int(p.production)
                if expected - cur >= o_FLEET_INTENT_MIN_DROP:
                    o__enemy_recently_launched.add(p.id)
        o__enemy_prev_ships.clear()
        for p in world.enemy_planets:
            o__enemy_prev_ships[p.id] = int(p.ships)

    if o_R1_RECAPTURE_PRIORITY_ENABLED:
        o__freshly_lost_planets.clear()
        o__freshly_captured_planets.clear()
        for p in world.planets:
            prev_owner = o__planet_prev_owner.get(p.id)
            if prev_owner == world.player and p.owner != -1 and p.owner != world.player:
                o__freshly_lost_planets.add(p.id)
            if (
                o_FRESH_CAPTURE_INHERITANCE_ENABLED
                and prev_owner is not None
                and prev_owner != world.player
                and p.owner == world.player
            ):
                o__freshly_captured_planets.add(p.id)
                o__planet_capture_age[p.id] = 0
        if o_FRESH_CAPTURE_INHERITANCE_ENABLED:
            for pid in list(o__planet_capture_age.keys()):
                if pid in o__freshly_captured_planets:
                    continue
                pp = world.planet_by_id.get(pid)
                if pp is None or pp.owner != world.player:
                    del o__planet_capture_age[pid]
                else:
                    o__planet_capture_age[pid] += 1
                    if o__planet_capture_age[pid] > o_FRESH_CAPTURE_MAX_AGE:
                        del o__planet_capture_age[pid]
        o__planet_prev_owner.clear()
        for p in world.planets:
            o__planet_prev_owner[p.id] = int(p.owner)


def o__neutral_blocked_by_cap(world, target):
    if not o_NEUTRAL_HARD_CAP_ENABLED:
        return False
    if target.owner != -1:
        return False
    if o_NEUTRAL_CAP_USES_EFFECTIVE_GARRISON:
        eff_owner, eff_ships = o_effective_garrison_at_arrival(target, o_NEUTRAL_CAP_LOOKAHEAD, world)
        if eff_owner != -1:
            return False
        if world.is_2p:
            return eff_ships >= o_NEUTRAL_HARD_CAP_2P
        if eff_ships <= o_NEUTRAL_HARD_CAP_4P:
            return False
        return target.id not in o__neutral_wounded
    if world.is_2p:
        return int(target.ships) >= o_NEUTRAL_HARD_CAP_2P
    if int(target.ships) <= o_NEUTRAL_HARD_CAP_4P:
        return False
    return target.id not in o__neutral_wounded


def o__neutral_tempo_ok(world, target, ships, turns):
    if not o_NEUTRAL_TEMPO_FILTER_ENABLED:
        return True
    if world.is_2p:
        return True
    if target.owner != -1:
        return True
    remaining_after = max(0, int(world.remaining_steps) - int(turns))
    net = float(target.production) * remaining_after - float(ships)
    return net >= o_NEUTRAL_TEMPO_THRESHOLD


def o__ti1_extra_margin(world):
    if not o_TI1_TIE_FOR_WIN_ENABLED:
        return 0
    if world.remaining_steps > o_TI1_HORIZON_TURNS:
        return 0
    my_sum = world.owner_strength.get(world.player, 0)
    leader_sum = my_sum
    for owner, ships in world.owner_strength.items():
        if owner == world.player or owner == -1:
            continue
        if ships > leader_sum:
            leader_sum = ships
    if leader_sum - my_sum < o_TI1_TRAILING_GAP_MIN:
        return 0
    return o_TI1_REQUIRED_EXTRA_MARGIN


def o__endgame_roi_ok(world, target, ships, turns):
    if not o_ENDGAME_ROI_ENABLED:
        return True
    if world.is_2p:
        return True
    if target.owner != -1:
        return True
    if world.step < o_TOTAL_STEPS - o_ENDGAME_ROI_TURNS:
        return True
    remaining_after = max(0, int(world.remaining_steps) - int(turns))
    expected_growth = float(target.production) * remaining_after
    threshold = float(target.ships) if o_E2_USE_GARRISON_THRESHOLD else float(ships)
    return expected_growth > threshold


def o_friendly_already_committed(world, target_id):
    target = world.planet_by_id.get(target_id)
    if target is None:
        return False
    pending = [c for c in o__pending_commitments if c["target_id"] == target_id]
    if not pending:
        return False
    if target.owner == -1 or target.owner == world.player:
        return sum(c["ships"] for c in pending) > 0
    for c in pending:
        eta = int(c["arrival_abs"]) - int(world.step)
        if eta <= 0:
            continue
        if int(c["ships"]) >= o_needed_to_capture(target, eta):
            return True
    return False


def o__commit_fleet(world, moves, spent, target_locked,
                  src_id, target_id, angle, turns, ships):
    # Hard backstop: no early-game fleet ever flies more than O_MAX_TRAVEL_CAP
    # turns, whatever path requested it (expand, hammer, defense, evac, ...).
    if int(turns) > O_MAX_TRAVEL_CAP:
        return
    moves.append([src_id, float(angle), int(ships)])
    spent[src_id] += int(ships)
    target_locked.add(target_id)
    target_obj = world.planet_by_id.get(int(target_id))
    owner_at_commit = int(target_obj.owner) if target_obj is not None else -2
    o__pending_commitments.append({
        "target_id": int(target_id),
        "ships": int(ships),
        "arrival_abs": int(world.step) + int(turns),
        "owner_at_commit": owner_at_commit,
    })


def o_plan_solo_capture(world, src, tgt, max_avail, max_travel):
    raw_dist = o_dist(src.x, src.y, tgt.x, tgt.y)
    if o_F3_THREE_BUCKET_ENABLED:
        if tgt.owner == -1 and raw_dist < o_F3_SAFE_DIST:
            min_floor = o_F3_SAFE_FLOOR
        elif (tgt.owner != -1 and tgt.owner != world.player
              and int(tgt.ships) >= o_F3_HARD_GARRISON):
            min_floor = o_F3_HARD_FLOOR
        else:
            min_floor = o_MIN_DISPATCH_SHIPS
    else:
        min_floor = 5 if (world.is_2p and raw_dist < 12.0) else o_MIN_DISPATCH_SHIPS
    if max_avail < min_floor:
        return None
    aim = o_aim_at_target(src, tgt, max_avail, world.initial_by_id, world.ang_vel, world=world)
    if aim is None:
        return None
    angle, turns = aim
    if turns > max_travel:
        return None
    need = o_effective_needed_to_capture(tgt, turns, world)
    margin = o_EXPAND_MIN_MARGIN_4P if not world.is_2p else o_EXPAND_MIN_MARGIN
    extra = o_X8B_2P_EXTRA if world.is_2p else 0
    extra += o__ti1_extra_margin(world)
    preferred = max(min_floor, need + margin + extra)
    if o_SP1_SPEED_AWARE_ENABLED:
        raw_dist = o_dist(src.x, src.y, tgt.x, tgt.y)
        if raw_dist >= o_SP1_LONG_DIST_THRESHOLD:
            preferred = max(preferred, min(o_SP1_LONG_DIST_SHIPS, max_avail))
    if preferred <= max_avail:
        ships = preferred
    else:
        ships = max(min_floor, need + margin)
        if ships > max_avail:
            ships = max(min_floor, need)
    if ships < min_floor or ships > max_avail:
        return None
    aim2 = o_aim_at_target(src, tgt, ships, world.initial_by_id, world.ang_vel, world=world)
    if aim2 is None:
        return None
    angle, turns = aim2
    if turns > max_travel:
        return None
    need2 = o_effective_needed_to_capture(tgt, turns, world)
    if ships < need2 + margin:
        ships = need2 + margin
        if ships > max_avail:
            return None
        aim3 = o_aim_at_target(src, tgt, ships, world.initial_by_id, world.ang_vel, world=world)
        if aim3 is None:
            return None
        angle, turns = aim3
        if turns > max_travel:
            return None
    if o_AS1_ANTI_SECOND_ENABLED and not world.is_2p:
        for eta, owner, e_ships in world.arrivals_by_planet.get(tgt.id, []):
            if int(eta) != int(turns):
                continue
            if owner == world.player or owner == -1:
                continue
            if int(e_ships) >= int(ships):
                return None
    if o_FWD_SIM_FILTER_ENABLED and not world.is_2p and tgt.owner == -1:
        proj = o_forward_project(
            world,
            our_capture_target=tgt.id,
            our_capture_turn=int(turns),
            our_capture_ships=int(ships),
            horizon=o_FWD_SIM_HORIZON,
            project_opponent_moves=True,
            opponent_emit_fraction=0.30,
        )
        end_owner, end_ships = proj.get(tgt.id, (-1, 0))
        if end_owner != world.player and end_owner != -1 and end_ships > 5:
            return None
    return angle, turns, int(ships)


def o_handle_defense(world, rescue_needs, available, spent, target_locked,
                   moves, mode_log):
    if not rescue_needs:
        return

    # Defend by what we'd lose, most valuable first: a high-production planet
    # hurts most to lose, so when rescuers are scarce it gets first claim.
    ordered = sorted(rescue_needs.items(),
                     key=lambda kv: (-float(kv[1][2].production), -int(kv[1][2].ships)))
    for victim_id, (deficit, deadline, victim) in ordered:
        if victim_id in target_locked:
            continue
        need = deficit + o_DEFENSE_OVERSEND

        if o_PREEMPTIVE_DOOM_EVAC_ENABLED and (not o_PREEMPTIVE_DOOM_EVAC_2P_ONLY or world.is_2p):
            enemy_arrivals = [
                (eta, owner, int(ships)) for eta, owner, ships
                in world.arrivals_by_planet.get(victim_id, [])
                if owner != world.player and owner != -1
            ]
            if world.is_2p or not o_PREEMPTIVE_EVAC_USE_LARGEST_SINGLE_ENEMY_4P:
                threat_metric = sum(ships for _eta, _owner, ships in enemy_arrivals)
            else:
                by_owner = defaultdict(int)
                for _eta, owner, ships in enemy_arrivals:
                    by_owner[owner] += ships
                threat_metric = max(by_owner.values()) if by_owner else 0
            window = deadline if deadline is not None else o_PREEMPTIVE_EVAC_DEFAULT_WINDOW
            garrison_at_deadline = float(victim.ships) + float(victim.production) * int(window)
            if threat_metric > garrison_at_deadline * o_PREEMPTIVE_EVAC_DOOM_RATIO:
                if o__try_doom_evac(world, victim, available, spent, target_locked, moves, mode_log):
                    continue

        solo = []
        for src in world.my_planets:
            if src.id == victim_id:
                continue
            avail = available[src.id] - spent[src.id]
            if avail < need:
                continue
            aim = o_aim_at_target(src, victim, avail, world.initial_by_id, world.ang_vel, world=world)
            if aim is None:
                continue
            angle, turns = aim
            if deadline is not None and turns > deadline:
                continue
            solo.append((turns, src.id, src, angle, avail))

        if solo:
            solo.sort()
            fired_solo = False
            last_fail = None
            for _t, src_id, src, _angle_est, avail in solo:
                send = min(avail, need)
                send = max(send, deficit + 1)
                if send < o_MIN_DISPATCH_SHIPS:
                    send = o_MIN_DISPATCH_SHIPS if avail >= o_MIN_DISPATCH_SHIPS else 0
                if send <= 0:
                    last_fail = "doomed-too-poor"
                    continue
                aim_final = o_aim_at_target(src, victim, send, world.initial_by_id, world.ang_vel, world=world)
                if aim_final is None:
                    last_fail = "doomed-aim-blocked"
                    continue
                angle, turns = aim_final
                if deadline is not None and turns > deadline:
                    last_fail = "doomed-too-slow"
                    continue
                if o_FWD_SIM_DEFENSE_CHECK and not world.is_2p:
                    proj = o_forward_project(
                        world,
                        our_capture_target=victim_id,
                        our_capture_turn=int(turns),
                        our_capture_ships=int(send),
                        horizon=o_FWD_SIM_HORIZON,
                        project_opponent_moves=True,
                        opponent_emit_fraction=0.30,
                    )
                    end_owner, _ = proj.get(victim_id, (-1, 0))
                    if end_owner != world.player:
                        last_fail = "fwd-sim-victim-still-lost"
                        continue
                o__commit_fleet(world, moves, spent, target_locked,
                              src_id, victim_id, angle, turns, int(send))
                mode_log[victim_id] = "defended-by-solo"
                mode_log[src_id] = "defense"
                fired_solo = True
                break
            if fired_solo:
                continue
            if last_fail is not None:
                mode_log[victim_id] = last_fail

        if not o_COALITION_ENABLED:
            if o__try_doom_evac(world, victim, available, spent, target_locked, moves, mode_log):
                continue
            mode_log[victim_id] = "doomed"
            continue
        coalition = o__find_defense_coalition(
            world, victim, deadline, need, available, spent
        )
        if coalition is None:
            if o__try_doom_evac(world, victim, available, spent, target_locked, moves, mode_log):
                continue
            mode_log[victim_id] = "doomed"
            continue
        for src_id, src, angle, ships, turns in coalition:
            o__commit_fleet(world, moves, spent, target_locked,
                          src_id, victim_id, angle, turns, int(ships))
            mode_log[src_id] = "defense-coalition"
        mode_log[victim_id] = "defended-by-coalition"


def o__try_doom_evac(world, victim, available, spent, target_locked, moves, mode_log):
    if not o_DOOM_EVAC_ENABLED:
        return False
    garrison = available[victim.id] - spent[victim.id]
    if garrison < o_DOOM_EVAC_MIN_SHIPS:
        return False

    friendly_candidates = []
    for dst in world.my_planets:
        if dst.id == victim.id:
            continue
        aim = o_aim_at_target(victim, dst, garrison, world.initial_by_id,
                            world.ang_vel, world=world)
        if aim is None:
            continue
        angle, turns = aim
        if turns > o_DOOM_EVAC_MAX_TRAVEL:
            continue
        score = int(dst.ships) + int(dst.production) * 5
        friendly_candidates.append((-score, int(turns), dst, angle))
    if friendly_candidates:
        friendly_candidates.sort()
        _score, turns, dst, angle = friendly_candidates[0]
        o__commit_fleet(world, moves, spent, target_locked,
                      victim.id, dst.id, angle, turns, int(garrison))
        mode_log[victim.id] = "doom-evac-launched"
        mode_log[dst.id] = "doom-evac-recipient"
        return True

    if not o_DOOM_EVAC_ATTACK_FALLBACK_ENABLED:
        return False
    if o_DOOM_EVAC_ATTACK_FALLBACK_4P_ONLY and world.is_2p:
        return False
    attack_candidates = []
    for dst in world.planets:
        if dst.id == victim.id or dst.owner == world.player:
            continue
        if dst.id in target_locked:
            continue
        if not o_is_targetable(world, dst):
            continue
        aim = o_aim_at_target(victim, dst, garrison, world.initial_by_id,
                            world.ang_vel, world=world)
        if aim is None:
            continue
        angle, turns = aim
        if turns > o_DOOM_EVAC_MAX_TRAVEL:
            continue
        is_enemy = dst.owner != -1
        prod = float(dst.production) if is_enemy else 0.0  # fractional rate
        arrival_garrison = float(dst.ships) + prod * int(turns)
        required = arrival_garrison + o_DOOM_EVAC_ATTACK_OVERKILL
        if int(garrison) < required:
            continue
        recently_launched_bonus = (
            -o_DOOM_EVAC_ATTACK_PREFER_LAUNCHED_BONUS
            if (is_enemy and dst.id in o__enemy_recently_launched) else 0
        )
        rank = (
            recently_launched_bonus,
            -int(dst.production),
            int(turns),
            int(required),
        )
        attack_candidates.append((rank, dst, angle, turns))
    if not attack_candidates:
        return False
    attack_candidates.sort(key=lambda x: x[0])
    _rank, dst, angle, turns = attack_candidates[0]
    o__commit_fleet(world, moves, spent, target_locked,
                  victim.id, dst.id, angle, turns, int(garrison))
    mode_log[victim.id] = "doom-evac-attack"
    mode_log[dst.id] = "doom-evac-attack-target"
    return True


def o__find_defense_coalition(world, victim, deadline, need, available, spent):
    options = []
    for src in world.my_planets:
        if src.id == victim.id:
            continue
        avail = available[src.id] - spent[src.id]
        if avail < o_COALITION_MIN_PER_CONTRIBUTOR:
            continue
        aim = o_aim_at_target(src, victim, avail, world.initial_by_id, world.ang_vel, world=world)
        if aim is None:
            continue
        _angle_est, turns = aim
        if deadline is not None and turns > deadline:
            continue
        options.append((turns, src.id, src, avail))

    if len(options) < 2:
        return None
    options.sort()

    for i in range(len(options)):
        for j in range(i + 1, len(options)):
            t_i, sid_i, s_i, a_i = options[i]
            t_j, sid_j, s_j, a_j = options[j]
            if a_i + a_j < need:
                continue
            ratio = a_i / float(a_i + a_j)
            ship_i = max(o_COALITION_MIN_PER_CONTRIBUTOR,
                         min(a_i, int(round(need * ratio))))
            ship_j = max(o_COALITION_MIN_PER_CONTRIBUTOR,
                         min(a_j, need - ship_i))
            while ship_i + ship_j < need:
                if ship_i < a_i:
                    ship_i += 1
                elif ship_j < a_j:
                    ship_j += 1
                else:
                    break
            if (ship_i + ship_j < need
                    or ship_i < o_COALITION_MIN_PER_CONTRIBUTOR
                    or ship_j < o_COALITION_MIN_PER_CONTRIBUTOR):
                continue
            aim_i = o_aim_at_target(s_i, victim, ship_i, world.initial_by_id, world.ang_vel, world=world)
            aim_j = o_aim_at_target(s_j, victim, ship_j, world.initial_by_id, world.ang_vel, world=world)
            if aim_i is None or aim_j is None:
                continue
            ang_i, turns_i = aim_i
            ang_j, turns_j = aim_j
            if (deadline is not None
                    and (turns_i > deadline or turns_j > deadline)):
                continue
            return [
                (sid_i, s_i, ang_i, ship_i, turns_i),
                (sid_j, s_j, ang_j, ship_j, turns_j),
            ]
    return None


o_COMET_EVAC_REMAINING_TURNS = 3
o_COMET_EVAC_MIN_SHIPS = 5


o_DOOM_EVAC_ENABLED = True
o_DOOM_EVAC_MIN_SHIPS = 5
o_DOOM_EVAC_MAX_TRAVEL = O_MAX_TRAVEL_CAP  # was 40; no long-distance evac flights


o_DOOM_EVAC_ATTACK_FALLBACK_ENABLED = True
o_DOOM_EVAC_ATTACK_FALLBACK_4P_ONLY = True
o_DOOM_EVAC_ATTACK_OVERKILL = 2
o_DOOM_EVAC_ATTACK_PREFER_LAUNCHED_BONUS = 3


o_PREEMPTIVE_DOOM_EVAC_ENABLED = True
o_PREEMPTIVE_DOOM_EVAC_2P_ONLY = False

o_PREEMPTIVE_EVAC_DOOM_RATIO = 1.20
o_PREEMPTIVE_EVAC_DEFAULT_WINDOW = 15


o_PREEMPTIVE_EVAC_USE_LARGEST_SINGLE_ENEMY_4P = True


def o_handle_comet_evac(world, available, spent, target_locked, moves, mode_log):
    if not world.comet_remaining:
        return
    own_non_comet = [p for p in world.my_planets if p.id not in world.comet_ids]
    if not own_non_comet:
        own_non_comet = [p for p in world.planets
                         if p.owner == -1 and p.id not in world.comet_ids]
        if not own_non_comet:
            return
    for src in world.my_planets:
        rem = world.comet_remaining.get(src.id)
        if rem is None or rem > o_COMET_EVAC_REMAINING_TURNS:
            continue
        if src.id in mode_log:
            continue
        avail = max(0, available[src.id] - spent.get(src.id, 0))
        if avail < o_COMET_EVAC_MIN_SHIPS:
            continue
        best = None
        best_d = float("inf")
        for dst in own_non_comet:
            if dst.id == src.id:
                continue
            d_now = o_dist(src.x, src.y, dst.x, dst.y)
            est_turns = max(1, int(math.ceil(d_now / o_fleet_speed(max(1, int(avail))))))
            dst_px, dst_py = o_predict_target_position(dst, world, est_turns)
            d = o_dist(src.x, src.y, dst_px, dst_py)
            if d < best_d:
                best_d = d
                best = dst
        if best is None:
            continue
        aim = o_aim_at_target(src, best, avail, world.initial_by_id, world.ang_vel, world=world)
        if aim is None:
            continue
        angle, turns = aim
        o__commit_fleet(world, moves, spent, target_locked,
                      src.id, best.id, angle, turns, int(avail))
        mode_log[src.id] = "comet-evac"


def o_handle_cheap_pickup(world, available, spent, target_locked, moves, mode_log):
    if not o_CHEAP_PICKUP_ENABLED:
        return
    if o_CHEAP_PICKUP_4P_ONLY and world.is_2p:
        return
    if o_LAUNCH_BLACKOUT_ENABLED and world.step >= o_TOTAL_STEPS - o_LAUNCH_BLACKOUT_TURNS:
        return
    if world.is_opening:
        max_travel = world.mode_params.get("expand_max_travel_opening", o_EXPAND_MAX_TRAVEL_OPENING)
    else:
        max_travel = world.mode_params["expand_max_travel_mid"]
    max_travel = min(max_travel, O_MAX_TRAVEL_CAP)  # no long-distance fleets

    cheap_neutrals = [
        p for p in world.neutral_planets
        if int(p.ships) <= o_CHEAP_PICKUP_MAX_GARRISON
        and p.id not in target_locked
        and o_is_targetable(world, p)
    ]
    if not cheap_neutrals:
        return
    if o_CHEAP_PICKUP_MIN_PROD >= 2 and any(int(p.production) >= o_CHEAP_PICKUP_MIN_PROD for p in cheap_neutrals):
        cheap_neutrals = [p for p in cheap_neutrals if int(p.production) >= o_CHEAP_PICKUP_MIN_PROD]

    sources = sorted(world.my_planets,
                     key=lambda s: -(available[s.id] - spent[s.id]))
    for src in sources:
        avail = available[src.id] - spent[src.id]
        if avail < o_MIN_DISPATCH_SHIPS:
            continue
        if mode_log.get(src.id):
            continue
        candidates = []
        for n in cheap_neutrals:
            if n.id in target_locked:
                continue
            if o_friendly_already_committed(world, n.id):
                continue
            cost = int(n.ships) + 1
            if cost > avail:
                continue
            raw = o_dist(src.x, src.y, n.x, n.y)
            if raw / o_MAX_SPEED > max_travel + 4:
                continue
            eff = o__effective_target_dist(src, n, world)
            eff += _o_territory_dist_bias(world, n)  # favor home/frontier
            candidates.append((cost, eff, n))
        if not candidates:
            continue
        candidates.sort(key=lambda kv: (kv[1], kv[0]))
        for _cost, _eff, n in candidates:
            plan = o_plan_solo_capture(world, src, n, avail, max_travel)
            if plan is None:
                continue
            angle, turns, ships = plan
            if o_RACE_ENABLED:
                enemy_eta = world.enemy_race_eta.get(n.id)
                if enemy_eta is not None and turns > enemy_eta:
                    continue
            if not o__capture_holds_against_snipe(world, n, turns, int(ships)):
                continue
            if not o__endgame_roi_ok(world, n, int(ships), turns):
                continue
            if not o__neutral_tempo_ok(world, n, int(ships), turns):
                continue
            o__commit_fleet(world, moves, spent, target_locked,
                          src.id, n.id, angle, turns, int(ships))
            mode_log[src.id] = "cheap-pickup"
            break


def o__is_cheap_neutral_pick(world, target):
    if target.owner != -1:
        return True
    if int(target.ships) > o_COMBAT_CHEAP_GARRISON:
        return False
    for mp in world.my_planets:
        if o_dist(mp.x, mp.y, target.x, target.y) <= o_COMBAT_CHEAP_DIST:
            return True
    return False


def o__handle_search_expand_4p(world, available, spent, target_locked, moves, mode_log):
    max_to_pick = o_SEARCH_MAX_ACTIONS_TO_PICK_2P if world.is_2p else o_SEARCH_MAX_ACTIONS_TO_PICK
    actions = o_search_step_action(
        world, max_per_source=o_SEARCH_MAX_PER_SOURCE,
        max_actions_to_eval=30,
        use_depth2=o_SEARCH_DEPTH2_ENABLED,
    )
    committed_sources = set()
    committed_targets = set()
    for act in actions[:max_to_pick * 2]:
        if act["score"] <= 0:
            continue
        src_id = act["source_id"]
        tgt_id = act["target_id"]
        if src_id in committed_sources or tgt_id in committed_targets:
            continue
        if tgt_id in target_locked:
            continue
        src_status = mode_log.get(src_id)
        if src_status == "brain-reserved-lead":
            continue
        avail = available[src_id] - spent[src_id]
        if avail < act["ships"]:
            continue
        tgt = world.planet_by_id.get(tgt_id)
        if (world.stop_expanding_2p or world.prod_lead_stop_expand_4p or world.turn_cutoff_stop_expand) and tgt is not None and tgt.owner == -1:
            continue
        if world.stop_expand_lax and tgt is not None and tgt.owner == -1:
            if not o__is_cheap_neutral_pick(world, tgt):
                continue
        if tgt is not None and tgt.owner == -1:
            turns_act = int(act["arrival_turn"])
            ships_act = int(act["ships"])
            if not o__capture_holds_against_snipe(world, tgt, turns_act, ships_act):
                continue
            if not o__endgame_roi_ok(world, tgt, ships_act, turns_act):
                continue
            if not o__neutral_tempo_ok(world, tgt, ships_act, turns_act):
                continue
        o__commit_fleet(world, moves, spent, target_locked,
                      src_id, tgt_id, act["angle"], act["arrival_turn"], act["ships"])
        mode_log[src_id] = "search-expand"
        committed_sources.add(src_id)
        committed_targets.add(tgt_id)
        if len(committed_sources) >= max_to_pick:
            break
    return committed_sources


def o_handle_expand(world, available, spent, target_locked, moves, mode_log):
    if o_LAUNCH_BLACKOUT_ENABLED and world.step >= o_TOTAL_STEPS - o_LAUNCH_BLACKOUT_TURNS:
        return
    if (o_SEARCH_EXPAND_4P_ENABLED and not world.is_2p) or \
       (o_SEARCH_EXPAND_2P_ENABLED and world.is_2p):
        o__handle_search_expand_4p(world, available, spent, target_locked, moves, mode_log)
    if world.is_opening:
        K = world.mode_params.get("expand_k_opening", o_EXPAND_K_OPENING)
        max_travel = world.mode_params.get("expand_max_travel_opening", o_EXPAND_MAX_TRAVEL_OPENING)
    else:
        K = world.mode_params["expand_k_mid"]
        max_travel = world.mode_params["expand_max_travel_mid"]
    max_travel = min(max_travel, O_MAX_TRAVEL_CAP)  # no long-distance fleets

    nonfriendly = [
        p for p in world.planets
        if p.owner != world.player and o_is_targetable(world, p)
    ]
    if world.stop_expanding_2p or world.prod_lead_stop_expand_4p or world.turn_cutoff_stop_expand:
        nonfriendly = [p for p in nonfriendly if p.owner != -1]
    elif world.stop_expand_lax:
        nonfriendly = [
            p for p in nonfriendly
            if p.owner != -1 or o__is_cheap_neutral_pick(world, p)
        ]
    if not nonfriendly:
        return

    def frontier_key(src):
        return min(o_dist(src.x, src.y, t.x, t.y) for t in nonfriendly)

    sources = sorted(world.my_planets, key=frontier_key)

    for src in sources:
        avail = o__routine_avail(world, src, available[src.id] - spent[src.id])
        if avail < o_MIN_DISPATCH_SHIPS:
            continue
        status = mode_log.get(src.id)
        if status and status != "cheap-pickup":
            continue

        # Use a wider candidate window so reachable targets aren't hidden behind
        # a few unreachable near ones (territory bias + small K could starve it).
        candidates = o__nearest_targets(src, world, max(K, 8), max_travel, target_locked)
        fired_solo = False
        for tgt, _approx_dist in candidates:
            if o_friendly_already_committed(world, tgt.id):
                continue
            plan = o_plan_solo_capture(world, src, tgt, avail, max_travel)
            if plan is None:
                continue
            angle, turns, ships = plan
            if o_RACE_ENABLED and tgt.owner == -1:
                enemy_eta = world.enemy_race_eta.get(tgt.id)
                if enemy_eta is not None and turns > enemy_eta:
                    snipe = o__plan_counter_snipe(world, src, tgt, avail, max_travel)
                    if snipe is None:
                        continue
                    angle, turns, ships = snipe
            if tgt.owner == -1 and not o__capture_holds_against_snipe(world, tgt, turns, int(ships)):
                continue
            if not o__endgame_roi_ok(world, tgt, int(ships), turns):
                continue
            if not o__neutral_tempo_ok(world, tgt, int(ships), turns):
                continue
            if (
                o_FWD_SIM_ENABLED
                and world.is_2p
                and tgt.owner != world.player
                and not o__fwd_capture_holds_2p(world, src, tgt, angle, turns, int(ships), world.player)
            ):
                continue
            o__commit_fleet(world, moves, spent, target_locked,
                          src.id, tgt.id, angle, turns, int(ships))
            mode_log[src.id] = "expand-solo"
            fired_solo = True
            break

        if fired_solo:
            continue
        if not o_COALITION_ENABLED:
            continue

        coalition_max_travel = max_travel + o_COALITION_MAX_TRAVEL_BONUS
        for tgt, _ in candidates:
            if tgt.id in target_locked:
                continue
            if o_COALITION_NEUTRALS_ONLY and tgt.owner != -1:
                continue
            if o_friendly_already_committed(world, tgt.id):
                continue
            ok = o__try_coalition_expand(
                world, src, tgt, coalition_max_travel, available, spent,
                target_locked, moves, mode_log,
            )
            if ok:
                break


def o__effective_target_dist(src, tgt, world):
    raw = o_dist(src.x, src.y, tgt.x, tgt.y)
    if not o_ROT_AWARE_RANK_ENABLED:
        return raw
    init = world.initial_by_id.get(tgt.id)
    if init is None:
        return raw
    if o_dist(init.x, init.y, o_CENTER_X, o_CENTER_Y) + init.radius >= o_ROTATION_LIMIT:
        return raw
    speed = o_fleet_speed(50)
    travel = max(1, int(math.ceil(raw / speed)))
    if travel > 60:
        return raw
    px, py = o_predict_planet_position(tgt, world.initial_by_id, world.ang_vel, travel)
    return o_dist(src.x, src.y, px, py)


def o__counter_snipe_candidates(world, src, max_travel, target_locked):
    if not o_COUNTER_SNIPE_ENABLED:
        return []
    if o_COUNTER_SNIPE_2P_ONLY and not world.is_2p:
        return []
    out = []
    for n in world.neutral_planets:
        if n.id in target_locked:
            continue
        if not o_is_targetable(world, n):
            continue
        enemy_eta = None
        enemy_remaining = None
        needed = int(n.ships) + 1
        for eta, owner, ships in world.arrivals_by_planet.get(n.id, []):
            if owner == world.player or owner == -1:
                continue
            if ships < needed:
                continue
            if enemy_eta is None or eta < enemy_eta:
                enemy_eta = int(eta)
                enemy_remaining = ships - int(n.ships)
        if enemy_eta is None:
            continue
        d = o_dist(src.x, src.y, n.x, n.y)
        speed = o_fleet_speed(50)
        my_eta_est = max(1, int(math.ceil(d / speed)))
        if my_eta_est > max_travel + 4:
            continue
        delay = my_eta_est - enemy_eta
        if delay < o_COUNTER_SNIPE_MIN_DELAY or delay > o_COUNTER_SNIPE_MAX_DELAY:
            continue
        prod = max(0.0, float(n.production))  # fractional production rate
        defender_at_my_arrival = max(0, int(enemy_remaining)) + prod * delay
        flip_cost = int(math.floor(defender_at_my_arrival)) + 1
        if flip_cost > o_COUNTER_SNIPE_MAX_COST:
            continue
        out.append((flip_cost, n, d))
    out.sort(key=lambda kv: kv[0])
    return [(n, d) for _cost, n, d in out]


def o__plan_counter_snipe(world, src, tgt, max_avail, max_travel):
    if not o_COUNTER_SNIPE_ENABLED or tgt.owner != -1:
        return None
    if o_COUNTER_SNIPE_2P_ONLY and not world.is_2p:
        return None
    if max_avail < o_MIN_DISPATCH_SHIPS:
        return None
    enemy_eta = None
    enemy_remaining = None
    needed_to_take = int(tgt.ships) + 1
    for eta, owner, ships in world.arrivals_by_planet.get(tgt.id, []):
        if owner == world.player or owner == -1:
            continue
        if ships < needed_to_take:
            continue
        if enemy_eta is None or eta < enemy_eta:
            enemy_eta = int(eta)
            enemy_remaining = ships - int(tgt.ships)
    if enemy_eta is None:
        return None

    aim = o_aim_at_target(src, tgt, max_avail, world.initial_by_id, world.ang_vel, world=world)
    if aim is None:
        return None
    angle, turns = aim
    if turns > max_travel:
        return None
    delay = turns - enemy_eta
    if delay < o_COUNTER_SNIPE_MIN_DELAY or delay > o_COUNTER_SNIPE_MAX_DELAY:
        return None
    prod = max(0.0, float(tgt.production))  # fractional production rate
    defender = max(0, int(enemy_remaining)) + prod * delay
    ships = max(o_MIN_DISPATCH_SHIPS, int(math.floor(defender)) + 1)
    if ships > max_avail or ships > o_COUNTER_SNIPE_MAX_COST:
        return None
    aim2 = o_aim_at_target(src, tgt, ships, world.initial_by_id, world.ang_vel, world=world)
    if aim2 is None:
        return None
    angle, turns = aim2
    if turns > max_travel:
        return None
    delay2 = turns - enemy_eta
    if delay2 < o_COUNTER_SNIPE_MIN_DELAY or delay2 > o_COUNTER_SNIPE_MAX_DELAY:
        return None
    defender2 = max(0, int(enemy_remaining)) + prod * delay2
    if ships < int(math.floor(defender2)) + 1:
        ships = int(math.floor(defender2)) + 1
        if ships > max_avail or ships > o_COUNTER_SNIPE_MAX_COST:
            return None
        aim3 = o_aim_at_target(src, tgt, ships, world.initial_by_id, world.ang_vel, world=world)
        if aim3 is None:
            return None
        angle, turns = aim3
        if turns > max_travel:
            return None
    return angle, turns, int(ships)


def o__capture_holds_against_snipe(world, target, arrival_turn, ships_sent):
    if not o_ANTI_SNIPE_ENABLED:
        return True
    if o_ANTI_SNIPE_2P_ONLY and not world.is_2p:
        return True
    if target.owner != -1:
        return True
    arrivals = world.arrivals_by_planet.get(target.id, [])
    enemy_after = []
    friendly_after = []
    for eta, owner, ships in arrivals:
        if ships <= 0:
            continue
        if eta <= arrival_turn:
            continue
        if eta - arrival_turn > o_ANTI_SNIPE_HORIZON:
            continue
        if owner == world.player:
            friendly_after.append((eta, ships))
        elif owner != -1:
            enemy_after.append((eta, ships))

    if o_REACTIVE_SNIPE_PROJECTION_ENABLED:
        for enemy_p in world.enemy_planets:
            e_ships = int(enemy_p.ships)
            if e_ships < o_REACTIVE_MIN_ENEMY_SHIPS:
                continue
            if o_SUN_SHADOW_REACTIVE_FILTER and not world.is_2p and o_segment_hits_sun(
                enemy_p.x, enemy_p.y, target.x, target.y
            ):
                continue
            d = o_dist(enemy_p.x, enemy_p.y, target.x, target.y)
            projected_force = max(o_REACTIVE_MIN_PROJECTED, int(e_ships * o_REACTIVE_EMIT_FRAC))
            speed = o_fleet_speed(projected_force)
            travel = max(1, int(math.ceil(d / speed)))
            snipe_eta = travel
            if snipe_eta <= arrival_turn:
                continue
            if snipe_eta - arrival_turn > o_ANTI_SNIPE_HORIZON:
                continue
            enemy_after.append((snipe_eta, projected_force))

    if not enemy_after:
        return True

    if o_N6_USE_EFFECTIVE_PRE_GARRISON:
        _, pre_garrison = o_effective_garrison_at_arrival(target, arrival_turn, world)
    else:
        pre_garrison = o_garrison_at_arrival(target, arrival_turn)
    if ships_sent <= pre_garrison:
        return True
    surplus = ships_sent - pre_garrison
    prod = max(0.0, float(target.production))  # fractional production rate
    by_turn = defaultdict(int)
    for eta, ships in enemy_after:
        by_turn[eta] -= ships
    for eta, ships in friendly_after:
        by_turn[eta] += ships

    bal = surplus
    last_t = arrival_turn
    for eta in sorted(by_turn):
        bal += prod * (eta - last_t)
        bal += by_turn[eta]
        if bal <= 0:
            return False
        last_t = eta
    return True


def o__tiebreak_hash(world, src_id, target_id):
    h = (int(world.player) * 2654435761) & 0xFFFFFFFF
    h ^= (int(world.step) * 1664525) & 0xFFFFFFFF
    h ^= (int(src_id) * 16777619) & 0xFFFFFFFF
    h ^= (int(target_id) * 2246822519) & 0xFFFFFFFF
    return h & 0xFFFF


def o__nearest_targets(src, world, K, max_travel, target_locked):
    _f31_has_better = (
        world.is_2p
        and o_EXPAND_MIN_PROD_2P >= 2
        and any(int(n.production) >= o_EXPAND_MIN_PROD_2P for n in world.neutral_planets
                if n.id not in target_locked)
    )
    candidates = []
    for t in world.planets:
        if t.owner == world.player:
            continue
        if t.id in target_locked:
            continue
        if not o_is_targetable(world, t):
            continue
        if o__neutral_blocked_by_cap(world, t):
            continue
        if _f31_has_better and t.owner == -1 and int(t.production) < o_EXPAND_MIN_PROD_2P:
            continue
        raw = o_dist(src.x, src.y, t.x, t.y)
        if raw / o_MAX_SPEED > max_travel + 4:
            continue
        eff = o__effective_target_dist(src, t, world)
        weight = o_VALUE_WEIGHT_2P if world.is_2p else o_VALUE_WEIGHT_4P
        weighted = eff - max(0, int(t.production)) * weight
        if o_F1B_EXPAND_BONUS_ENABLED and t.owner != world.player and t.owner != -1:
            if t.id in o__enemy_recently_launched:
                weighted -= o_F1B_EXPAND_BONUS
        if o_SO1_STATIC_PREFERENCE_ENABLED:
            init_t = world.initial_by_id.get(t.id)
            if init_t is not None:
                r_t = o_dist(init_t.x, init_t.y, o_CENTER_X, o_CENTER_Y)
                if r_t + init_t.radius >= o_ROTATION_LIMIT:
                    weighted -= o_SO1_STATIC_BONUS
        if (
            o_LEADER_BASH_ENABLED
            and not world.is_2p
            and world.contest_leader
            and world.step >= o_LEADER_BASH_MIN_STEP
            and world.leader_id is not None
            and t.owner == world.leader_id
        ):
            weighted -= o_LEADER_BASH_BONUS
        if (
            not world.is_2p
            and t.owner != -1
            and t.owner != world.player
            and world.opp_profile
            and t.owner in world.opp_profile
        ):
            prof = world.opp_profile[t.owner]
            if len(prof["emit"]) >= 5:
                avg_emit = sum(prof["emit"]) / len(prof["emit"])
                if avg_emit > 0.35:
                    weighted -= 5.0
        if (
            o_WEAKEST_TARGET_ENABLED
            and not world.is_2p
            and world.step >= o_WEAKEST_TARGET_MIN_STEP
            and world.mode == "pressure"
            and world.weakest_enemy is not None
            and t.owner == world.weakest_enemy
        ):
            if world.weakest_enemy_prod_share < o_WEAKEST_DONT_FINISH_SHARE:
                weighted += o_WEAKEST_DONT_FINISH_PENALTY
            else:
                weighted -= o_WEAKEST_TARGET_BONUS
        if (
            o_F14_4A_2P_FOCUS_ENABLED
            and world.is_2p
            and world.focus_enemy_2p is not None
            and t.owner == world.focus_enemy_2p
        ):
            weighted -= o_F14_4A_2P_FOCUS_DIST_BONUS

        # --- Territory bias (our addition) ---
        # Clear our HOME quadrant first (strongest favor), then the frontier,
        # and penalize spreading into other quadrants so we don't scatter while
        # home still has uncaptured/enemy planets.
        if _home_quadrant is not None:
            tq = _get_quadrant(t)
            fq = _frontier_quadrant(_home_quadrant, world.ang_vel)
            if tq == _home_quadrant:
                weighted -= 8.0   # home first
            elif tq == fq:
                weighted -= 3.0   # then frontier
            else:
                weighted += 8.0 if world.step < 50 else 15.0  # avoid scatter

        candidates.append((t, weighted, raw))
    if not candidates:
        return []
    candidates.sort(key=lambda kv: kv[1])
    if (o_FWD_SIM_RANK_BONUS_4P > 0 and not world.is_2p and len(candidates) > 1):
        baseline_proj = o_forward_project(
            world, horizon=o_FWD_SIM_HORIZON,
            project_opponent_moves=True, opponent_emit_fraction=0.30
        )
        baseline_score = o_forward_score(baseline_proj, world.player, 4, world)
        rerank = []
        topN = min(K + 2, len(candidates))
        for idx, (t, w, raw) in enumerate(candidates[:topN]):
            est_eta = max(1, int(math.ceil(raw / o_MAX_SPEED)))
            est_ships = o_needed_to_capture(t, est_eta) + 1
            proj = o_forward_project(
                world, our_capture_target=t.id, our_capture_turn=est_eta,
                our_capture_ships=est_ships, horizon=o_FWD_SIM_HORIZON,
                project_opponent_moves=True, opponent_emit_fraction=0.30
            )
            score_gain = o_forward_score(proj, world.player, 4, world) - baseline_score
            adjusted = w - o_FWD_SIM_RANK_BONUS_4P * score_gain
            rerank.append((t, adjusted, raw))
        candidates = rerank + candidates[topN:]
        candidates.sort(key=lambda kv: kv[1])
    if world.is_2p and o_TIEBREAK_ENABLED and len(candidates) > 1:
        best_d = candidates[0][1]
        eps = max(o_TIEBREAK_EPS_MIN, o_TIEBREAK_EPS_FRAC * best_d)
        def _k(kv):
            tgt, weighted_d, _raw = kv
            bucket = int(weighted_d / eps) if eps > 0 else 0
            return (bucket, o__tiebreak_hash(world, src.id, tgt.id), weighted_d)
        candidates.sort(key=_k)

    counter_snipe = o__counter_snipe_candidates(world, src, max_travel, target_locked)

    if not o_RACE_ENABLED or not world.enemy_race_eta:
        head = counter_snipe + [(t, raw) for t, _eff, raw in candidates[:K]]
        return o__dedupe_targets(head)

    race_priority = []
    normal = []
    for t, _eff, raw in candidates:
        enemy_eta = world.enemy_race_eta.get(t.id)
        if enemy_eta is None or t.owner != -1:
            normal.append((t, raw))
            continue
        my_min = max(1, int(math.ceil(raw / o_fleet_speed(max(1, int(src.ships))))))
        if my_min <= enemy_eta:
            race_priority.append((t, raw))
        else:
            normal.append((t, raw))

    return o__dedupe_targets(counter_snipe + race_priority + normal[:K])


def o__dedupe_targets(seq):
    seen = set()
    out = []
    for tgt, d in seq:
        if tgt.id in seen:
            continue
        seen.add(tgt.id)
        out.append((tgt, d))
    return out


def o__try_coalition_expand(world, src, tgt, max_travel, available, spent,
                          target_locked, moves, mode_log):
    src_avail = available[src.id] - spent[src.id]
    if src_avail < o_COALITION_MIN_PER_CONTRIBUTOR:
        return False
    if int(tgt.ships) < o_COALITION_MIN_TARGET_SHIPS:
        return False

    partners = []
    for p in world.my_planets:
        if p.id == src.id:
            continue
        avail = available[p.id] - spent[p.id]
        if avail < o_COALITION_MIN_PER_CONTRIBUTOR:
            continue
        est = o_aim_at_target(p, tgt, avail, world.initial_by_id, world.ang_vel, world=world)
        if est is None:
            continue
        _, est_turns = est
        if est_turns > max_travel:
            continue
        partners.append((est_turns, p, avail))
    if not partners:
        return False
    partners.sort(key=lambda kv: kv[0])

    for est_turns, p, p_avail in partners:
        combined = src_avail + p_avail
        est_src = o_aim_at_target(src, tgt, src_avail, world.initial_by_id, world.ang_vel, world=world)
        if est_src is None:
            continue
        worst = max(est_src[1], est_turns)
        total_needed = o_needed_to_capture(tgt, worst)
        if combined < total_needed:
            continue

        ratio = src_avail / float(combined)
        s_src = max(o_COALITION_MIN_PER_CONTRIBUTOR,
                    min(src_avail, int(round(total_needed * ratio))))
        s_p = max(o_COALITION_MIN_PER_CONTRIBUTOR,
                  min(p_avail, total_needed - s_src))
        while s_src + s_p < total_needed:
            if s_src < src_avail:
                s_src += 1
            elif s_p < p_avail:
                s_p += 1
            else:
                break
        if s_src + s_p < total_needed:
            continue
        if s_src < o_COALITION_MIN_PER_CONTRIBUTOR or s_p < o_COALITION_MIN_PER_CONTRIBUTOR:
            continue
        if s_src > src_avail or s_p > p_avail:
            continue

        aim_src = o_aim_at_target(src, tgt, s_src, world.initial_by_id, world.ang_vel, world=world)
        aim_p = o_aim_at_target(p, tgt, s_p, world.initial_by_id, world.ang_vel, world=world)
        if aim_src is None or aim_p is None:
            continue
        a_src, t_src = aim_src
        a_p, t_p = aim_p
        if t_src > max_travel or t_p > max_travel:
            continue

        if world.is_2p and abs(t_src - t_p) > 1:
            continue

        post_eta = max(t_src, t_p)
        post_needed = o_needed_to_capture(tgt, post_eta)
        if s_src + s_p < post_needed:
            continue

        o__commit_fleet(world, moves, spent, target_locked,
                      src.id, tgt.id, a_src, t_src, int(s_src))
        o__commit_fleet(world, moves, spent, target_locked,
                      p.id, tgt.id, a_p, t_p, int(s_p))
        mode_log[src.id] = "expand-coalition"
        mode_log[p.id] = "expand-coalition"
        return True

    return False


def o__routine_avail(world, planet, base_avail):
    if not o_PROD_RESERVE_ENABLED:
        return base_avail
    if PROD_RESERVE_4P_ONLY and world.is_2p:
        return base_avail
    if world.step < PROD_RESERVE_TURN_MIN:
        return base_avail
    if int(planet.production) < PROD_RESERVE_MIN_PROD:
        return base_avail
    reserve = int(int(planet.ships) * PROD_RESERVE_FRAC)
    return max(0, base_avail - reserve)


def o__brain_pick_lead(world, available, spent, mode_log, min_ships=None):
    if min_ships is None:
        min_ships = o_ACCUMULATOR_LEAD_MIN_SHIPS
    enemies = world.enemy_planets
    candidates = []
    for p in world.my_planets:
        status = mode_log.get(p.id)
        if status and status != "brain-reserved-lead":
            continue
        avail = available[p.id] - spent[p.id]
        if avail < min_ships:
            continue
        threat = sum(int(ships) for eta, owner, ships
                     in world.arrivals_by_planet.get(p.id, [])
                     if owner != world.player and owner != -1)
        if threat >= avail * o_ACCUMULATOR_LEAD_THREAT_RATIO:
            continue
        if o_BRAIN_LEAD_PREFER_FRONTIER and enemies:
            frontier_dist = min(o_dist(p.x, p.y, e.x, e.y) for e in enemies)
            score = float(avail) - frontier_dist * o_BRAIN_LEAD_FRONTIER_WEIGHT
        else:
            score = float(avail)
        candidates.append((score, p))
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]


def o__brain_reserve_lead(world, available, spent, mode_log):
    if not o_BRAIN_LEAD_RESERVE_ENABLED:
        return
    if not o_ACCUMULATOR_ENABLED:
        return
    if o_BRAIN_LEAD_RESERVE_4P_ONLY and world.is_2p:
        return
    if o_ACCUMULATOR_4P_ONLY and world.is_2p:
        return
    if world.step < o_ACCUMULATOR_TURN_MIN:
        return
    lead = o__brain_pick_lead(world, available, spent, mode_log,
                            min_ships=o_BRAIN_LEAD_RESERVE_MIN_SHIPS)
    if lead is None:
        return
    if o_BRAIN_LEAD_RESERVE_REQUIRE_TARGET:
        has_target = False
        for tgt in world.enemy_planets:
            if int(tgt.ships) > o_MEGA_HAMMER_TARGET_GARRISON_MAX_ITER_H:
                continue
            aim = o_aim_at_target(lead, tgt, available[lead.id] - spent[lead.id],
                                world.initial_by_id, world.ang_vel, world=world)
            if aim is None:
                continue
            _, turns = aim
            if turns > o_MEGA_HAMMER_MAX_TRAVEL:
                continue
            has_target = True
            break
        if not has_target:
            return
    mode_log[lead.id] = "brain-reserved-lead"


def o_handle_accumulator(world, available, spent, target_locked, moves, mode_log):
    if not o_ACCUMULATOR_ENABLED:
        return
    if o_ACCUMULATOR_4P_ONLY and world.is_2p:
        return
    if world.step < o_ACCUMULATOR_TURN_MIN:
        return

    lead_candidates = []
    for p in world.my_planets:
        status = mode_log.get(p.id)
        if status and status != "brain-reserved-lead":
            continue
        avail = available[p.id] - spent[p.id]
        if avail < o_ACCUMULATOR_LEAD_MIN_SHIPS:
            continue
        threat = sum(int(ships) for eta, owner, ships
                     in world.arrivals_by_planet.get(p.id, [])
                     if owner != world.player and owner != -1)
        if threat >= avail * o_ACCUMULATOR_LEAD_THREAT_RATIO:
            continue
        lead_candidates.append((avail, p))
    if not lead_candidates:
        return
    lead_candidates.sort(key=lambda x: -x[0])
    lead_avail, lead = lead_candidates[0]

    feeders = []
    for p in world.my_planets:
        if p.id == lead.id or p.id in mode_log:
            continue
        threat = sum(int(ships) for eta, owner, ships
                     in world.arrivals_by_planet.get(p.id, [])
                     if owner != world.player and owner != -1)
        if threat > 0:
            continue
        avail = available[p.id] - spent[p.id]
        surplus = avail - o_ACCUMULATOR_FEEDER_KEEP_RESERVE
        if surplus < o_ACCUMULATOR_FEEDER_MIN_SURPLUS:
            continue
        aim = o_aim_at_target(p, lead, surplus, world.initial_by_id,
                            world.ang_vel, world=world)
        if aim is None:
            continue
        angle, turns = aim
        if turns > o_ACCUMULATOR_FEEDER_MAX_TRAVEL:
            continue
        feeders.append((turns, surplus, p, angle))

    if not feeders:
        return
    feeders.sort(key=lambda x: (x[0], -x[1]))
    fed_count = 0
    for turns, surplus, src, angle in feeders:
        if fed_count >= o_ACCUMULATOR_MAX_FEEDS_PER_TURN:
            break
        o__commit_fleet(world, moves, spent, target_locked,
                      src.id, lead.id, angle, turns, int(surplus))
        mode_log[src.id] = "accumulator-feeder"
        fed_count += 1
    if fed_count > 0:
        if lead.id not in mode_log:
            mode_log[lead.id] = "accumulator-lead"


def o_handle_mega_hammer(world, available, spent, target_locked, moves, mode_log):
    if not o_MEGA_HAMMER_ENABLED:
        return
    if o_MEGA_HAMMER_4P_ONLY and world.is_2p:
        return
    sources = sorted(world.my_planets,
                     key=lambda p: -(available[p.id] - spent[p.id]))
    fired_targets = set()
    fired_count = 0
    for src in sources:
        if o_MEGA_HAMMER_CONCENTRATE_ENABLED and fired_count >= o_MEGA_HAMMER_MAX_PER_TURN:
            break
        avail = available[src.id] - spent[src.id]
        prod = int(src.production)
        if o_FRESH_CAPTURE_INHERITANCE_ENABLED and src.id in o__planet_capture_age:
            threshold = o_MEGA_HAMMER_SHIPS_MIN_FRESH
        else:
            threshold = o_MEGA_HAMMER_THRESHOLD_BY_PROD.get(prod, o_MEGA_HAMMER_SHIPS_MIN)
        if avail < threshold:
            continue
        status = mode_log.get(src.id)
        if status and status not in ("cheap-pickup", "brain-reserved-lead"):
            continue
        best = None
        for tgt in world.enemy_planets:
            if tgt.id in target_locked or tgt.id in fired_targets:
                continue
            if int(tgt.ships) > o_MEGA_HAMMER_TARGET_GARRISON_MAX_ITER_H:
                continue
            aim = o_aim_at_target(src, tgt, avail, world.initial_by_id,
                                world.ang_vel, world=world)
            if aim is None:
                continue
            angle, turns = aim
            if turns > o_MEGA_HAMMER_MAX_TRAVEL:
                continue
            focus_bonus = 0
            if (o_F14_4A_2P_FOCUS_ENABLED and world.is_2p
                    and getattr(world, "focus_enemy_2p", None) is not None
                    and tgt.owner == world.focus_enemy_2p):
                focus_bonus = o_F14_4A_2P_FOCUS_MEGA_BONUS
            score = (int(tgt.production) + focus_bonus, -int(turns))
            if best is None or score > best[0]:
                best = (score, tgt, angle, turns)
        if best is None:
            continue
        _, tgt, angle, turns = best
        if o_MEGA_HAMMER_MELIS_VERIFY and turns > 0:
            proj = o_forward_project(
                world,
                our_capture_target=tgt.id,
                our_capture_turn=int(turns),
                our_capture_ships=int(avail),
                horizon=o_FWD_SIM_HORIZON + int(turns),
                project_opponent_moves=True,
                opponent_emit_fraction=o_MEGA_HAMMER_VERIFY_OPP_EMIT,
            )
            end_owner, _ = proj.get(tgt.id, (-1, 0))
            if end_owner != world.player:
                continue
        o__commit_fleet(world, moves, spent, target_locked,
                      src.id, tgt.id, angle, turns, int(avail))
        mode_log[src.id] = "mega-hammer-launched"
        mode_log[tgt.id] = "mega-hammer-target"
        fired_targets.add(tgt.id)
        fired_count += 1


def o_handle_hammer(world, available, spent, target_locked, moves, mode_log):
    global o__hammer_plan
    if not o_HAMMER_ENABLED:
        return
    if not world.enemy_planets:
        o__hammer_plan = None
        return

    if o__hammer_plan is not None:
        target = world.planet_by_id.get(o__hammer_plan["target_id"])
        if target is None or target.owner == world.player:
            o__hammer_plan = None
        else:
            arrival_rel = o__hammer_plan["target_arrival_abs"] - world.step
            if arrival_rel <= 0:
                o__hammer_plan = None
            else:
                d_owner, d_ships = o_predict_defender_at_arrival(world, target, arrival_rel)
                if d_ships > o__hammer_plan["committed_strength"] / o_HAMMER_ABORT_OVERRUN_RATIO:
                    o__hammer_plan = None

    if o__hammer_plan is None:
        if not o__hammer_should_fire(world):
            return
        plan = o__build_hammer_plan(world, available, spent)
        if plan is None:
            return
        if o_HAMMER_MELIS_VERIFY:
            target = world.planet_by_id.get(plan["target_id"])
            if target is not None:
                arrival_rel = plan["target_arrival_abs"] - world.step
                if arrival_rel > 0:
                    proj = o_forward_project(
                        world,
                        our_capture_target=plan["target_id"],
                        our_capture_turn=int(arrival_rel),
                        our_capture_ships=int(plan["committed_strength"]),
                        horizon=o_FWD_SIM_HORIZON + arrival_rel,
                        project_opponent_moves=True,
                        opponent_emit_fraction=0.30,
                    )
                    end_owner, _ = proj.get(plan["target_id"], (-1, 0))
                    if end_owner != world.player:
                        return
        o__hammer_plan = plan

    plan = o__hammer_plan
    completed_launches = []
    for src_id, launch in list(plan["launches"].items()):
        if launch.get("fired"):
            continue
        if launch["fire_turn_abs"] > world.step:
            continue
        src = world.planet_by_id.get(src_id)
        if src is None or src.owner != world.player:
            completed_launches.append(src_id)
            continue
        ships = launch["ships"]
        if ships < o_HAMMER_MIN_PER_CONTRIBUTOR:
            completed_launches.append(src_id)
            continue
        avail = available[src_id] - spent[src_id]
        if avail < ships:
            completed_launches.append(src_id)
            continue
        target = world.planet_by_id[plan["target_id"]]
        aim = o_aim_at_target(src, target, ships, world.initial_by_id, world.ang_vel, world=world)
        if aim is None:
            completed_launches.append(src_id)
            continue
        angle, turns = aim
        o__commit_fleet(world, moves, spent, target_locked,
                      src_id, plan["target_id"], angle, turns, int(ships))
        mode_log[src_id] = "hammer"
        launch["fired"] = True

    for sid in completed_launches:
        plan["launches"].pop(sid, None)
    if not plan["launches"] or all(l.get("fired") for l in plan["launches"].values()):
        o__hammer_plan = None


def o__hammer_should_fire(world):
    if world.is_late:
        return True
    threshold = world.mode_params["hammer_prod_share"]
    if world.my_prod_share < threshold:
        return False
    return True


def o__build_hammer_plan(world, available, spent):
    stockpile_min = world.mode_params.get("hammer_stockpile_min", o_HAMMER_STOCKPILE_MIN)
    stockpiles = []
    for p in world.my_planets:
        avail = o__routine_avail(world, p, available[p.id] - spent[p.id])
        if avail < o_HAMMER_MIN_PER_CONTRIBUTOR:
            continue
        promoted = p.id in o__promoted_stockpiles
        if avail < stockpile_min and not promoted:
            continue
        stockpiles.append((p, avail))
    if not stockpiles:
        return None

    overkill = o_LATE_FLUSH_OVERKILL_RATIO if world.is_late else world.mode_params["hammer_overkill"]

    targets = [
        p for p in world.enemy_planets
        if o_is_targetable(world, p) and p.production >= o_HAMMER_TARGET_PROD_MIN
    ]
    if not targets:
        if world.is_late:
            targets = [p for p in world.enemy_planets if o_is_targetable(world, p)]
        if not targets:
            return None

    best = None
    for tgt in targets:
        per_src = []
        for src, avail in stockpiles:
            aim = o_aim_at_target(src, tgt, max(1, avail), world.initial_by_id, world.ang_vel, world=world)
            if aim is None:
                continue
            angle, turns = aim
            if turns > o_HAMMER_MAX_TRAVEL:
                continue
            per_src.append((turns, src, avail, angle))
        if not per_src:
            continue
        per_src.sort()
        target_arrival = per_src[-1][0]
        d_owner, d_ships = o_predict_defender_at_arrival(world, tgt, target_arrival)
        if d_owner == world.player:
            continue
        required = int(math.ceil(d_ships * overkill)) + 1

        accum = 0
        chosen = []
        for turns, src, avail, angle in per_src:
            chosen.append((turns, src, avail, angle))
            accum += avail
            if accum >= required:
                break
        if accum < required:
            continue

        slack = accum - required
        if slack > 0 and chosen:
            last_turn, last_src, last_avail, last_angle = chosen[-1]
            oversend_active = (
                o_HAMMER_NO_THREAT_OVERSEND_ENABLED
                and (not o_HAMMER_NO_THREAT_OVERSEND_2P_ONLY or world.is_2p)
            )
            last_src_threat = sum(
                int(ships) for eta, owner, ships
                in world.arrivals_by_planet.get(last_src.id, [])
                if owner != world.player and owner != -1
            )
            safe_surplus_ok = (
                o_HAMMER_SAFE_SURPLUS_OVERSEND_ENABLED
                and last_avail >= required * o_HAMMER_SAFE_SURPLUS_RATIO
                and last_src_threat <= last_avail * o_HAMMER_OVERSEND_MAX_THREAT_RATIO
            )
            if safe_surplus_ok:
                pass
            elif oversend_active and o_HAMMER_ALWAYS_OVERSEND_2P and world.is_2p:
                pass
            elif oversend_active and last_src_threat == 0:
                pass
            else:
                trimmed = last_avail - slack
                if trimmed < o_HAMMER_MIN_PER_CONTRIBUTOR:
                    chosen.pop()
                    if not chosen or sum(c[2] for c in chosen) < required - last_avail:
                        chosen.append((last_turn, last_src, last_avail, last_angle))
                else:
                    chosen[-1] = (last_turn, last_src, trimmed, last_angle)

        score = required - target_arrival * 0.5
        if (o_F14_4A_2P_FOCUS_ENABLED and world.is_2p
                and getattr(world, "focus_enemy_2p", None) is not None
                and tgt.owner == world.focus_enemy_2p):
            score += o_F14_4A_2P_FOCUS_HAMMER_BONUS
        if o_FLEET_INTENT_ENABLED and tgt.id in o__enemy_recently_launched:
            score += o_FLEET_INTENT_HAMMER_BONUS
        if o_R1_RECAPTURE_PRIORITY_ENABLED and tgt.id in o__freshly_lost_planets:
            score += o_R1_RECAPTURE_HAMMER_BONUS
        if not world.is_2p:
            my_strength = world.owner_strength.get(world.player, 0)
            enemy_strengths = [
                (world.owner_strength[o], o)
                for o in world.owner_strength
                if o not in (-1, world.player) and world.owner_strength[o] > 0
            ]
            if enemy_strengths:
                max_enemy_strength, max_enemy_owner = max(enemy_strengths)
                if max_enemy_strength > my_strength and tgt.owner == max_enemy_owner:
                    score = score - abs(score) * 0.3
        cand = {
            "target_id": tgt.id,
            "target_arrival_abs": world.step + target_arrival,
            "committed_strength": sum(c[2] for c in chosen),
            "score": score,
            "launches": {},
        }
        for turns, src, ships, angle in chosen:
            fire_turn_rel = target_arrival - turns
            cand["launches"][src.id] = {
                "fire_turn_abs": world.step + fire_turn_rel,
                "ships": int(ships),
                "angle": float(angle),
                "fired": False,
            }
        if best is None or cand["score"] > best["score"]:
            best = cand
    return best


def o_handle_multiprong(world, available, spent, target_locked, moves, mode_log):
    if not o_MULTIPRONG_ENABLED:
        return
    if o_MULTIPRONG_2P_ONLY and not world.is_2p:
        return
    if o__hammer_plan is None:
        return

    target_id = o__hammer_plan.get("target_id")
    target = world.planet_by_id.get(target_id)
    if target is None or target.owner == world.player or target.owner == -1:
        return
    arrival_rel = o__hammer_plan.get("target_arrival_abs", world.step) - world.step
    if arrival_rel <= 0:
        return
    committed = int(o__hammer_plan.get("committed_strength", 0))
    if committed <= 0:
        return

    reinforcer_ships = defaultdict(int)
    for f in world.fleets:
        if int(f.ships) <= 0:
            continue
        if f.owner == world.player or f.owner == -1:
            continue
        ftarget, _eta = o_fleet_target_planet(
            f, world.planets, world.initial_by_id, world.ang_vel
        )
        if ftarget is None or ftarget.id != target_id:
            continue
        reinforcer_ships[int(f.from_planet_id)] += int(f.ships)
    if not reinforcer_ships:
        return

    _, defender_at_arrival = o_predict_defender_at_arrival(world, target, arrival_rel)
    needed_t = int(math.ceil(defender_at_arrival)) + 1
    deficit = max(0, needed_t - committed)

    min_reinforce = max(1, int(math.ceil(deficit * o_MULTIPRONG_REINFORCER_MIN_RATIO)))

    candidates = []
    for src_id, ship_count in reinforcer_ships.items():
        src = world.planet_by_id.get(src_id)
        if src is None:
            continue
        if src.owner == world.player or src.owner == -1:
            continue
        if ship_count < min_reinforce:
            continue
        candidates.append((src, ship_count))
    if not candidates:
        return
    candidates.sort(key=lambda kv: kv[1], reverse=True)

    for reinforcer, in_flight in candidates:
        if reinforcer.id in target_locked:
            continue
        if not o_is_targetable(world, reinforcer):
            continue
        prong = o__build_multiprong_attack(
            world, reinforcer, available, spent, target_locked
        )
        if prong is None:
            continue
        prong_strength, prong_arrival, prong_landings, e_at_arrival = prong

        if prong_strength <= e_at_arrival * o_MULTIPRONG_E_OVERKILL:
            continue
        needed_e = int(math.ceil(e_at_arrival)) + 1
        if committed + prong_strength < needed_t + int(round(needed_e * o_MULTIPRONG_CREDIBILITY_FACTOR)):
            continue

        for src_id, src, angle, ships, turns in prong_landings:
            o__commit_fleet(
                world, moves, spent, target_locked,
                src_id, reinforcer.id, angle, turns, int(ships),
            )
            mode_log[src_id] = "multiprong"
        mode_log[reinforcer.id] = "multiprong-target"
        return


def o__build_multiprong_attack(world, target, available, spent, target_locked):
    sources = []
    for src in world.my_planets:
        avail = available[src.id] - spent[src.id]
        if avail < o_MULTIPRONG_MIN_PER_CONTRIBUTOR:
            continue
        aim = o_aim_at_target(src, target, max(o_MULTIPRONG_MIN_PER_CONTRIBUTOR, avail), world.initial_by_id, world.ang_vel, world=world)
        if aim is None:
            continue
        _angle, est_turns = aim
        if est_turns > o_MULTIPRONG_MAX_TRAVEL:
            continue
        sources.append((est_turns, src, avail))
    if not sources:
        return None
    sources.sort(key=lambda kv: kv[0])

    chosen = []
    for est_turns, src, avail in sources[:o_MULTIPRONG_MAX_PARTICIPANTS]:
        chosen.append((est_turns, src, avail))
        common_arrival = max(t for t, _, _ in chosen)
        _, e_at_arrival = o_predict_defender_at_arrival(world, target, common_arrival)
        total_avail = sum(a for _, _, a in chosen)
        required = int(math.ceil(e_at_arrival * o_MULTIPRONG_E_OVERKILL)) + 1
        if total_avail >= required:
            break
    common_arrival = max(t for t, _, _ in chosen)
    _, e_at_arrival = o_predict_defender_at_arrival(world, target, common_arrival)
    required = int(math.ceil(e_at_arrival * o_MULTIPRONG_E_OVERKILL)) + 1
    total_avail = sum(a for _, _, a in chosen)
    if total_avail < required:
        return None

    slack = total_avail - required
    if slack > 0 and chosen:
        last_turn, last_src, last_avail = chosen[-1]
        trimmed = last_avail - slack
        if trimmed >= o_MULTIPRONG_MIN_PER_CONTRIBUTOR:
            chosen[-1] = (last_turn, last_src, trimmed)

    landings = []
    final_strength = 0
    for est_turns, src, ships in chosen:
        if ships < o_MULTIPRONG_MIN_PER_CONTRIBUTOR:
            return None
        aim = o_aim_at_target(src, target, ships, world.initial_by_id, world.ang_vel, world=world)
        if aim is None:
            return None
        angle, turns = aim
        if turns > o_MULTIPRONG_MAX_TRAVEL:
            return None
        landings.append((src.id, src, angle, int(ships), int(turns)))
        final_strength += int(ships)

    final_arrival = max(turns for _, _, _, _, turns in landings)
    _, final_defender = o_predict_defender_at_arrival(world, target, final_arrival)
    final_required = int(math.ceil(final_defender * o_MULTIPRONG_E_OVERKILL)) + 1
    if final_strength < final_required:
        return None

    return final_strength, final_arrival, landings, final_defender


def o_handle_flow_to_frontier(world, available, spent, target_locked, moves, mode_log):
    """Hybrid regroup (attack-leaning): each planet keeps a safe reserve and
    sends surplus toward (a) a threatened friendly planet if any exist, else
    (b) the frontier quadrant. Relays through closer friendly planets.
    Runs AFTER attack handlers: only planets with no target this turn flow."""
    if _home_quadrant is None:
        return
    frontier_q = _frontier_quadrant(_home_quadrant, world.ang_vel)
    frontier_planets = [p for p in world.my_planets if _get_quadrant(p) == frontier_q]

    # Threat-first (defense). If any of our planets is under real threat, surplus
    # goes to reinforce the most threatened one instead of pushing frontier.
    threatened = _threatened_planets(world)

    for src in sorted(world.my_planets,
                      key=lambda p: -(available[p.id] - spent[p.id])):
        if mode_log.get(src.id):
            continue
        keep = _safe_reserve(world, src)
        avail = available[src.id] - spent[src.id]
        surplus = avail - keep
        if surplus < MIN_DISPATCH_SHIPS:
            continue

        # Choose destination set: threatened planets (defense) or frontier (attack)
        if threatened:
            dest_pool = [p for p in threatened if p.id != src.id]
        else:
            if _get_quadrant(src) == frontier_q:
                continue  # frontier planets attack, don't flow
            dest_pool = [p for p in frontier_planets if p.id != src.id]
        if not dest_pool:
            continue

        dest = min(dest_pool, key=lambda p: dist(src.x, src.y, p.x, p.y))
        dest_d = dist(src.x, src.y, dest.x, dest.y)
        # Relay: nearest friendly strictly closer to dest than src (else dest)
        relay = None
        for rp in sorted(world.my_planets, key=lambda p: dist(src.x, src.y, p.x, p.y)):
            if rp.id == src.id or rp.id in target_locked:
                continue
            if dist(rp.x, rp.y, dest.x, dest.y) < dest_d:
                relay = rp
                break
        tgt = relay if relay is not None else dest
        if tgt.id == src.id or tgt.id in target_locked:
            continue
        aim = o_aim_at_target(src, tgt, surplus, world.initial_by_id,
                              world.ang_vel, world=world)
        if aim is None:
            continue
        angle, turns = aim
        o__commit_fleet(world, moves, spent, target_locked,
                        src.id, tgt.id, angle, turns, int(surplus))
        mode_log[src.id] = "flow-to-frontier"


def o_plan_moves(world, deadline=None):
    global o__planet_idle_counts, o__promoted_stockpiles, o__pending_commitments

    def _commitment_viable(c):
        if c["arrival_abs"] <= world.step:
            return False
        target = world.planet_by_id.get(c["target_id"])
        if target is None:
            return False
        if target.owner == world.player:
            return False
        if o_FAILTOLERANT_ENABLED:
            owner_at_commit = c.get("owner_at_commit")
            if owner_at_commit is not None and int(target.owner) != int(owner_at_commit):
                return False
        return True
    o__pending_commitments[:] = [c for c in o__pending_commitments if _commitment_viable(c)]

    o__update_neutral_watchlist(world)

    moves = []
    spent = defaultdict(int)
    target_locked = set()
    mode_log = {}

    rescue_needs = {}
    available = {}
    for p in world.my_planets:
        arrivals = world.arrivals_by_planet.get(p.id, [])
        reserve, holds, deficit, dline = o_compute_planet_reserve(
            p, arrivals, world.player
        )
        available[p.id] = max(0, int(p.ships) - reserve)
        if not holds:
            rescue_needs[p.id] = (deficit, dline, p)
            mode_log[p.id] = "absorb-need-rescue"
        elif arrivals:
            mode_log[p.id] = "absorb"

    def _over_budget():
        return deadline is not None and time.perf_counter() >= deadline

    o_handle_comet_evac(world, available, spent, target_locked, moves, mode_log)

    o_handle_defense(world, rescue_needs, available, spent, target_locked,
                   moves, mode_log)

    o__brain_reserve_lead(world, available, spent, mode_log)

    if not _over_budget():
        if not (o_SEARCH_EXPAND_4P_ENABLED and not world.is_2p
                and o_SEARCH_DISABLES_CHEAP_PICKUP):
            o_handle_cheap_pickup(world, available, spent, target_locked, moves, mode_log)

    if not _over_budget():
        o_handle_expand(world, available, spent, target_locked, moves, mode_log)

    if not _over_budget():
        o_handle_accumulator(world, available, spent, target_locked, moves, mode_log)

    if not _over_budget():
        o_handle_mega_hammer(world, available, spent, target_locked, moves, mode_log)

    if not _over_budget():
        o_handle_hammer(world, available, spent, target_locked, moves, mode_log)

    if not _over_budget():
        o_handle_multiprong(world, available, spent, target_locked, moves, mode_log)

    # Our addition: AFTER attacks — only planets that found no target this turn
    # (no mode_log) flow surplus to frontier / reinforce a threatened planet.
    if not _over_budget():
        o_handle_flow_to_frontier(world, available, spent, target_locked, moves, mode_log)

    for p in world.my_planets:
        if mode_log.get(p.id) and "absorb" not in mode_log[p.id]:
            o__planet_idle_counts[p.id] = 0
        else:
            o__planet_idle_counts[p.id] = o__planet_idle_counts.get(p.id, 0) + 1
            if o__planet_idle_counts[p.id] >= o_HAMMER_SURROUNDED_PROMOTE_TURNS:
                o__promoted_stockpiles.add(p.id)

    return moves


def o_agent(obs, config=None):
    global o__agent_step, o__hammer_plan, o__planet_idle_counts, o__promoted_stockpiles, o__pending_commitments
    global o__game_num_players, o__2p_patient_streak, o__2p_prod_share_history

    global o__opp_profile
    obs_step = o__read(obs, "step", 0) or 0
    if obs_step == 0:
        o__agent_step = 0
        o__hammer_plan = None
        o__planet_idle_counts = {}
        o__promoted_stockpiles = set()
        o__pending_commitments = []
        o__game_num_players = None
        o__2p_patient_streak = 0
        o__2p_prod_share_history = []
        o__neutral_prev_ships.clear()
        o__neutral_wounded.clear()
        o__enemy_prev_ships.clear()
        o__enemy_recently_launched.clear()
        o__planet_prev_owner.clear()
        o__freshly_lost_planets.clear()
        o__opp_profile = {}
    o__agent_step += 1

    start = time.perf_counter()
    world = o_World(obs, inferred_step=o__agent_step - 1)
    if not world.my_planets:
        return []

    if not world.is_2p:
        o__update_opp_profile_4p(world)

    act_timeout = o__read(config, "actTimeout", 1.0) if config is not None else 1.0
    soft_budget = max(0.5, act_timeout * o_SOFT_DEADLINE_FRACTION)
    deadline = start + soft_budget

    return o_plan_moves(world, deadline=deadline)


# ===== End fused opponent-bot logic =====

def agent(obs, config=None):
    global _agent_step, _pending_commitments
    global _game_num_players, _2p_patient_streak, _2p_prod_share_history

    global _opp_profile, _starting_max_prod, _home_quadrant, _parent_ids, _late_latched, _opp_aggression
    obs_step = _read(obs, "step", 0) or 0
    if obs_step == 0:
        _late_latched = False
        _opp_aggression = 0.0
        _agent_step = 0
        _pending_commitments = []
        _game_num_players = None
        _starting_max_prod = None
        _home_quadrant = None
        _parent_ids = []
        _parent_quads.clear()
        _drift_start.clear()
        _drift_count.clear()
        _2p_patient_streak = 0
        _2p_prod_share_history = []
        _neutral_prev_ships.clear()
        _neutral_wounded.clear()
        _enemy_prev_ships.clear()
        _enemy_recently_launched.clear()
        _planet_prev_owner.clear()
        _freshly_lost_planets.clear()
        _opp_profile = {}
        _idle_streak.clear()
    _agent_step += 1
    step_est = max(int(obs_step), _agent_step - 1)

    # At step 0 only, build our World once to fix the home quadrant (needed by
    # the territory/frontier logic the o_ pipeline reads).
    if obs_step == 0:
        w0 = World(obs, inferred_step=0)
        if w0.my_planets:
            _starting_max_prod = max((int(p.production) for p in w0.my_planets), default=1)
            _home_quadrant = _get_quadrant(w0.my_planets[0])

    # Early phase ends when the board is mostly claimed (not a fixed turn): stay
    # in the old-bot land-grab while plenty of neutrals remain, then latch into
    # our own pipeline once >= BOARD_FILL_SWITCH of the (non-comet) planets are owned.
    if not _late_latched:
        raw = _read(obs, "planets", []) or []
        cids = set(int(c) for c in (_read(obs, "comet_planet_ids", []) or []))
        alive = [p for p in raw if len(p) >= 2 and int(p[0]) >= 0 and int(p[0]) not in cids]
        total = len(alive)
        claimed = sum(1 for p in alive if int(p[1]) != -1)
        if total > 0 and claimed / total >= BOARD_FILL_SWITCH:
            _late_latched = True

    # Early game: delegate to the fused o_ pipeline (builds its own World).
    # We do NOT build our own World here — avoids a wasteful double parse/turn.
    if not _late_latched:
        try:
            return o_agent(obs, config)
        except Exception:
            pass  # fall through to our own logic on any error

    start = time.perf_counter()
    world = World(obs, inferred_step=_agent_step - 1)
    if not world.my_planets:
        return []

    # Maintain anchored quadrants (territory) each turn we run our own pipeline.
    if PARENT_ENABLED:
        _update_parent_quads(world)

    
    if not world.is_2p:
        _update_opp_profile_4p(world)

    act_timeout = _read(config, "actTimeout", 1.0) if config is not None else 1.0
    soft_budget = max(0.5, act_timeout * SOFT_DEADLINE_FRACTION)
    deadline = start + soft_budget

    return plan_moves(world, deadline=deadline)


__all__ = ["agent", "Planet", "Fleet"]
