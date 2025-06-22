import requests
import json
from datetime import datetime

BASE_URL = "https://statsapi.mlb.com/api/v1"

# === 1) Get today's date ===
today = datetime.utcnow().strftime("%Y-%m-%d")
print(f"📅 Today: {today}")

# === 2) Get all team IDs ===
teams_url = f"{BASE_URL}/teams?sportId=1"
teams = requests.get(teams_url).json()['teams']
team_ids = [team['id'] for team in teams]

# === 3) Get all active hitters ===
batters = []
for team_id in team_ids:
    roster_url = f"{BASE_URL}/teams/{team_id}/roster/active"
    roster_res = requests.get(roster_url).json()
    for p in roster_res['roster']:
        if p['position']['type'] == 'Hitter':
            batters.append({
                "name": p['person']['fullName'],
                "id": p['person']['id'],
                "team_id": team_id
            })

print(f"✅ Found {len(batters)} active hitters.")

# === 4) Get today's schedule & probable SPs ===
sched_url = f"{BASE_URL}/schedule?sportId=1&date={today}"
sched_res = requests.get(sched_url).json()
dates = sched_res.get('dates', [])

games = []
if dates:
    games = dates[0].get('games', [])

team_sp_map = {}
for game in games:
    away_team = game['teams']['away']['team']['id']
    home_team = game['teams']['home']['team']['id']

    away_sp = game['teams']['home'].get('probablePitcher', {}).get('id')
    home_sp = game['teams']['away'].get('probablePitcher', {}).get('id')

    if away_sp:
        team_sp_map[away_team] = away_sp
    if home_sp:
        team_sp_map[home_team] = home_sp

print(f"✅ Mapped SPs for {len(team_sp_map)} teams.")

# === 5) Pull stats for each batter ===
results = []
SEASON_AVG_BASE = 0.238
TREND_BASE = 26.75

for b in batters:
    try:
        player_id = b['id']
        team_id = b['team_id']

        sp_id_
