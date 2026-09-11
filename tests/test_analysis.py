from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail
import pandas as pd

player_list = players.find_players_by_full_name("LeBron James")
player_id = player_list[0]['id']

shots = shotchartdetail.ShotChartDetail(
    player_id=player_id,
    team_id=0,
    season_nullable='2022-23',
    context_measure_simple='FGA'
)
df = shots.get_data_frames()[0]

# Filter to only midrange shots
midrange = df[df['SHOT_ZONE_BASIC'] == 'Mid-Range']

# Filter to only pull-up jumpshots within midrange
midrange_pullups = midrange[midrange['ACTION_TYPE'].str.contains('Pull-Up|Pullup', case=False, na=False)]

total_attempts = len(midrange_pullups)
makes = midrange_pullups['SHOT_MADE_FLAG'].sum()
fg_pct = makes / total_attempts if total_attempts > 0 else 0

print(f"Midrange pull-up attempts: {total_attempts}")
print(f"Midrange pull-up makes: {makes}")
print(f"Midrange pull-up FG%: {fg_pct:.1%}")

# Compare to his overall midrange FG%
all_midrange_makes = midrange['SHOT_MADE_FLAG'].sum()
all_midrange_attempts = len(midrange)
print(f"\nOverall midrange FG% (all types): {all_midrange_makes/all_midrange_attempts:.1%} ({all_midrange_attempts} attempts)")