from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# Find a player by name 
player_list = players.find_players_by_full_name("LeBron James")
print(player_list)

if player_list:
    player_id = player_list[0]['id']
    print(f"\nFound player ID: {player_id}")

    # Pull his career stats
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = career.get_data_frames()[0]
    print("\nCareer stats (first few rows):")
    print(df.head())
else:
    print("Player not found.")