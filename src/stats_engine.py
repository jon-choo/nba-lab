import sqlite3
import pandas as pd

def get_player_shots(player_name, season, db_path='../data/nba_lab.db'):
    """Pull a player's shots from the local database (not the API)."""
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM shots WHERE PLAYER_NAME_LABEL = ? AND SEASON = ?"
    df = pd.read_sql_query(query, conn, params=(player_name, season))
    conn.close()
    return df

def calculate_stat(df, zone=None, action_contains=None):
    filtered = df.copy()

    if zone:
        filtered = filtered[filtered['SHOT_ZONE_BASIC'] == zone]

    if action_contains:
        filtered = filtered[filtered['ACTION_TYPE'].str.contains(action_contains, case=False, na=False)]

    attempts = len(filtered)
    makes = filtered['SHOT_MADE_FLAG'].sum()
    fg_pct = makes / attempts if attempts > 0 else 0

    return attempts, makes, fg_pct


# Test 
lebron_shots = get_player_shots("LeBron James", "2022-23")

attempts, makes, pct = calculate_stat(lebron_shots, zone='Mid-Range', action_contains='Pull-Up|Pullup')
print(f"LeBron Midrange Pull-Ups: {attempts} attempts, {makes} makes, {pct:.1%}")

# Test
attempts2, makes2, pct2 = calculate_stat(lebron_shots, zone='Restricted Area')
print(f"LeBron Restricted Area: {attempts2} attempts, {makes2} makes, {pct2:.1%}")