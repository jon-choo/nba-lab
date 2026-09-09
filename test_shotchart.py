from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail

# Find LeBron again as our test case
player_list = players.find_players_by_full_name("LeBron James")
player_id = player_list[0]['id']

# Pull shot chart data for a specific season
# team_id=0 means "all teams" (safe default), season format is 'YYYY-YY'
shots = shotchartdetail.ShotChartDetail(
    player_id=player_id,
    team_id=0,
    season_nullable='2022-23',
    context_measure_simple='FGA'  # FGA = all field goal attempts
)

df = shots.get_data_frames()[0]

print(f"Total shots found: {len(df)}")
print(f"\nColumns available:\n{list(df.columns)}")
print(f"\nFirst few rows:")
print(df[['GAME_DATE', 'SHOT_TYPE', 'ACTION_TYPE', 'SHOT_ZONE_BASIC', 'SHOT_DISTANCE', 'SHOT_MADE_FLAG']].head(10))