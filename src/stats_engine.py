import sqlite3
from pathlib import Path

import pandas as pd
from data_pipeline import get_and_save_shots

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "nba_lab.db"


def get_player_shots(player_name, season, db_path=DEFAULT_DB_PATH):
    """
    Check the database first. If the player/season isn't there yet,
    fetch it live from the API, save it, then return it.
    """
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM shots WHERE PLAYER_NAME_LABEL = ? AND SEASON = ?"
    df = pd.read_sql_query(query, conn, params=(player_name, season))
    conn.close()

    if df.empty:
        print(f"No cached data for {player_name} ({season}) - fetching live...")
        get_and_save_shots(player_name, season, db_path=db_path)

        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn, params=(player_name, season))
        conn.close()

    return df


def calculate_stat(df, zone=None, action_contains=None):
    filtered = df.copy()

    if zone:
        if isinstance(zone, (list, tuple, set)):
            filtered = filtered[filtered['SHOT_ZONE_BASIC'].isin(zone)]
        else:
            filtered = filtered[filtered['SHOT_ZONE_BASIC'] == zone]

    if action_contains:
        filtered = filtered[filtered['ACTION_TYPE'].str.contains(action_contains, case=False, na=False)]

    attempts = len(filtered)
    makes = int(filtered['SHOT_MADE_FLAG'].sum())
    fg_pct = makes / attempts if attempts > 0 else 0.0

    return attempts, makes, fg_pct


if __name__ == "__main__":
    lebron_shots = get_player_shots("LeBron James", "2022-23")

    attempts, makes, pct = calculate_stat(lebron_shots, zone='Mid-Range', action_contains='Pull-Up|Pullup')
    print(f"LeBron Midrange Pull-Ups: {attempts} attempts, {makes} makes, {pct:.1%}")

    attempts2, makes2, pct2 = calculate_stat(lebron_shots, zone='Restricted Area')
    print(f"LeBron Restricted Area: {attempts2} attempts, {makes2} makes, {pct2:.1%}")