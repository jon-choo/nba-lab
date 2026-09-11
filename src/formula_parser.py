# formula_parser.py
from stats_engine import get_player_shots, calculate_stat

# "stat keywords" and what they map to
STAT_DEFINITIONS = {
    'MidRange_PullUp_PCT': {'zone': 'Mid-Range', 'action_contains': 'Pull-Up|Pullup'},
    'RestrictedArea_PCT': {'zone': 'Restricted Area', 'action_contains': None},
    'MidRange_PCT': {'zone': 'Mid-Range', 'action_contains': None},
    'CatchShoot_3PT_PCT': {'zone': None, 'action_contains': 'Jump Shot'},  # refine later
    # add more as you identify useful stat combos
}

def evaluate_formula(player_name, season, formula_string):
    """
    formula_string example: 'MidRange_PullUp_PCT + RestrictedArea_PCT'
    Only supports addition for now — we'll expand this.
    """
    df = get_player_shots(player_name, season)

    stat_keywords = [s.strip() for s in formula_string.split('+')]

    total = 0
    breakdown = {}

    for keyword in stat_keywords:
        if keyword not in STAT_DEFINITIONS:
            print(f"Warning: unknown stat '{keyword}'")
            continue

        params = STAT_DEFINITIONS[keyword]
        attempts, makes, pct = calculate_stat(df, **params)
        breakdown[keyword] = pct
        total += pct

    return total, breakdown


# Test 
result, breakdown = evaluate_formula(
    "LeBron James", "2022-23",
    "MidRange_PullUp_PCT + RestrictedArea_PCT"
)

print(f"\nFormula result: {result:.3f}")
print("Breakdown:")
for stat, val in breakdown.items():
    print(f"  {stat}: {val:.1%}")