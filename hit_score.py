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

        # ✅ Correct: NO stray sp_id_
        sp_id = team_sp_map.get(team_id)
        if not sp_id:
            print(f"⚠️ No SP for {b['name']} (Team ID {team_id}), skipping.")
            continue

        # Season AVG
        season_url = f"{BASE_URL}/people/{player_id}/stats?stats=season&group=hitting"
        season_data = requests.get(season_url).json()
        splits = season_data['stats'][0]['splits']
        if not splits:
            continue
        season_avg = float(splits[0]['stat']['avg'])

        # Game Log: L5/L10/L20
        log_url = f"{BASE_URL}/people/{player_id}/stats?stats=gameLog&group=hitting"
        log_data = requests.get(log_url).json()
        splits = log_data['stats'][0]['splits']
        if not splits:
            continue

        L5 = sum(int(g['stat']['hits']) for g in splits[:5]) / 5
        L10 = sum(int(g['stat']['hits']) for g in splits[:10]) / 10
        L20 = sum(int(g['stat']['hits']) for g in splits[:20]) / 20

        # SP OBA
        sp_url = f"{BASE_URL}/people/{sp_id}/stats?stats=season&group=pitching"
        sp_data = requests.get(sp_url).json()
        sp_splits = sp_data['stats'][0]['splits']
        if not sp_splits:
            continue
        sp_oba = float(sp_splits[0]['stat']['avg'])

        # Compute Hit Score
        season_component = season_avg / SEASON_AVG_BASE
        trend_component = (L5 + L10 + L20) / TREND_BASE
        sp_component = sp_oba / SEASON_AVG_BASE

        hit_score = season_component + trend_component + sp_component

        results.append({
            "name": b['name'],
            "season_avg": round(season_avg, 3),
            "L5": round(L5, 3),
            "L10": round(L10, 3),
            "L20": round(L20, 3),
            "sp_oba": round(sp_oba, 3),
            "hit_score": round(hit_score, 2)
        })

        print(f"✅ {b['name']}: {round(hit_score, 2)}")

    except Exception as e:
        print(f"❌ Error for {b['name']}: {e}")

# === 6) Save ===
output = {
    "generated_at": datetime.utcnow().isoformat(),
    "players": results
}

with open("hit_scores.json", "w") as f:
    json.dump(output, f, indent=4)

print(f"\n🎉 All done! Saved hit_scores.json with {len(results)} players.")
