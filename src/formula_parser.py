from stats_engine import get_player_shots, calculate_stat
from asteval import Interpreter
import re

# Expanded stat definitions — add more as needed
STAT_DEFINITIONS = {
    'MidRange_PullUp_PCT':      {'zone': 'Mid-Range', 'action_contains': 'Pull-Up|Pullup'},
    'MidRange_PCT':             {'zone': 'Mid-Range', 'action_contains': None},
    'RestrictedArea_PCT':       {'zone': 'Restricted Area', 'action_contains': None},
    'Paint_NonRA_PCT':          {'zone': 'In The Paint (Non-RA)', 'action_contains': None},
    'CornerThree_PCT':          {'zone': ['Left Corner 3', 'Right Corner 3'], 'action_contains': None},
    'LeftCorner3_PCT':          {'zone': 'Left Corner 3', 'action_contains': None},
    'RightCorner3_PCT':         {'zone': 'Right Corner 3', 'action_contains': None},
    'AboveBreakThree_PCT':      {'zone': 'Above the Break 3', 'action_contains': None},
    'ThreePointAll_PCT':        {'zone': ['Above the Break 3', 'Left Corner 3', 'Right Corner 3'], 'action_contains': None},
    'StepBack_PCT':             {'zone': None, 'action_contains': 'Step Back'},
    'DrivingLayup_PCT':         {'zone': None, 'action_contains': 'Driving Layup'},
    'PullUp_All_PCT':           {'zone': None, 'action_contains': 'Pull-Up|Pullup'},
    'LayupAll_PCT':             {'zone': None, 'action_contains': 'Layup'},
    'Dunk_PCT':                 {'zone': None, 'action_contains': 'Dunk'},
    'Fadeaway_PCT':             {'zone': None, 'action_contains': 'Fadeaway'},
    'Turnaround_PCT':           {'zone': None, 'action_contains': 'Turnaround'},
    'Floater_PCT':              {'zone': None, 'action_contains': 'Floating'},
    'HookShot_PCT':             {'zone': None, 'action_contains': 'Hook'},
}


# Options for user-built stats (the pickers only send these names, never raw patterns)
ZONES = [
    'Restricted Area',
    'In The Paint (Non-RA)',
    'Mid-Range',
    'Left Corner 3',
    'Right Corner 3',
    'Above the Break 3',
]

SHOT_TYPES = {
    'Pull-up':   'Pull-Up|Pullup',
    'Step back': 'Step Back',
    'Fadeaway':  'Fadeaway',
    'Turnaround': 'Turnaround',
    'Floater':   'Floating',
    'Hook shot': 'Hook',
    'Layup':     'Layup',
    'Dunk':      'Dunk',
    'Driving':   'Driving',
    'Running':   'Running',
    'Cutting':   'Cutting',
    'Alley-oop': 'Alley Oop',
    'Jump shot': 'Jump',
    'Bank shot': 'Bank',
}

MAX_CUSTOM_STATS = 20
NAME_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]{0,39}$')


def build_custom_definitions(custom_stats):
    """Check user-built stats and turn them into the same format as STAT_DEFINITIONS."""
    definitions = {}
    errors = []

    if len(custom_stats) > MAX_CUSTOM_STATS:
        errors.append(f"Too many custom stats (max {MAX_CUSTOM_STATS})")
        return definitions, errors

    for stat in custom_stats:
        name = stat['name']
        zones = stat['zones']
        shot_types = stat['shot_types']

        if not NAME_PATTERN.match(name):
            errors.append(f"Invalid stat name '{name}' (use letters, numbers and underscores)")
        elif name in STAT_DEFINITIONS or name in definitions:
            errors.append(f"A stat named '{name}' already exists")
        elif not zones and not shot_types:
            errors.append(f"'{name}' needs at least one zone or shot type")
        elif any(z not in ZONES for z in zones) or any(t not in SHOT_TYPES for t in shot_types):
            errors.append(f"'{name}' has an unknown zone or shot type")
        else:
            patterns = [SHOT_TYPES[t] for t in shot_types]
            if not patterns:
                action = None
            elif stat['shot_match'] == 'all':
                action = ''.join(f'(?=.*(?:{p}))' for p in patterns)
            else:
                action = '|'.join(f'(?:{p})' for p in patterns)
            definitions[name] = {'zone': zones or None, 'action_contains': action}

    return definitions, errors


def evaluate_formula(player_name, season, formula_string, custom_definitions=None):
    df = get_player_shots(player_name, season)

    all_definitions = {**STAT_DEFINITIONS, **(custom_definitions or {})}

    # Find all stat keywords used in the formula (longest names matched first to avoid partial overlaps)
    sorted_keys = sorted(all_definitions.keys(), key=len, reverse=True)

    breakdown = {}
    working_formula = formula_string

    for keyword in sorted_keys:
        pattern = rf'\b{re.escape(keyword)}\b'
        if re.search(pattern, working_formula):
            params = all_definitions[keyword]
            attempts, makes, pct = calculate_stat(df, **params)
            breakdown[keyword] = {'value': pct, 'attempts': attempts, 'makes': makes}
            # Replace the keyword with its numeric value in the formula string
            working_formula = re.sub(pattern, str(pct), working_formula)

    # Safety check: warn about any leftover unrecognized words
    errors = []
    leftover_words = re.findall(r'[A-Za-z_]+', working_formula)
    if leftover_words:
        errors.append(f"Unrecognized terms in formula: {leftover_words}")
        return None, breakdown, errors

    # Safely evaluate the resulting math expression
    aeval = Interpreter()
    result = aeval(working_formula)

    if aeval.error:
        errors.extend(err.get_error()[1] for err in aeval.error)
        return None, breakdown, errors

    return result, breakdown, errors


if __name__ == "__main__":
    # Test 1: original simple addition
    result, breakdown, errors = evaluate_formula(
        "LeBron James", "2022-23",
        "MidRange_PullUp_PCT + RestrictedArea_PCT"
    )
    print(f"\nTest 1  Simple addition")
    print(f"Result: {result:.3f}")
    for k, v in breakdown.items():
        print(f"  {k}: {v['value']:.1%} ({v['makes']}/{v['attempts']})")

    # Test 2: weighted formula with subtraction
    result2, breakdown2, errors2 = evaluate_formula(
        "LeBron James", "2022-23",
        "0.6 * MidRange_PullUp_PCT - 0.2 * StepBack_PCT + RestrictedArea_PCT"
    )
    print(f"\nTest 2 - Weighted formula with subtraction")
    print(f"Result: {result2:.3f}")
    for k, v in breakdown2.items():
        print(f"  {k}: {v['value']:.1%} ({v['makes']}/{v['attempts']})")