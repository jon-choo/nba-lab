import sqlite3
from pathlib import Path

import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "nba_lab.db"


def get_and_save_shots(player_name, season, db_path=DEFAULT_DB_PATH):
    # Look up player
    player_list = players.find_players_by_full_name(player_name)
    if not player_list:
        print(f"Player '{player_name}' not found.")
        return
    player_id = player_list[0]['id']

    # Pull shot data
    shots = shotchartdetail.ShotChartDetail(
        player_id=player_id,
        team_id=0,
        season_nullable=season,
        context_measure_simple='FGA'
    )
    df = shots.get_data_frames()[0]

    # Add player name and season as columns (useful once we have many players)
    df['PLAYER_NAME_LABEL'] = player_name
    df['SEASON'] = season

    # Save to SQLite — appends if table exists, creates if not
    conn = sqlite3.connect(db_path)
    df.to_sql('shots', conn, if_exists='append', index=False)
    conn.close()

    print(f"Saved {len(df)} shots for {player_name} ({season}) to {db_path}")

if __name__ == "__main__":
    get_and_save_shots("LeBron James", "2022-23")