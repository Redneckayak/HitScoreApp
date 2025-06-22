import json
from datetime import datetime

# === Example test data ===
batters = [
    {
        "name": "Aaron Judge",
        "season_avg": 0.280,
        "L5": 0.320,
        "L10": 0.300,
        "L20": 0.290,
        "sp_oba": 0.250
    },
    {
        "name": "Juan Soto",
        "season_avg": 0.300,
        "L5": 0.350,
        "L10": 0.320,
        "L20": 0.310,
        "sp_oba": 0.240
    }
]

results = []
for batter in batters:
    season_component = batter["season_avg"] / 0.238
    trend_component = (batter["L5"] + batter["L10"] + batter["L20"]) / 26.75
    sp_component = batter["sp_oba"] / 0.238
    hit_score = season_component + trend_component + sp_component

    results.append({
        "name": batter["name"],
        "hit_score": round(hit_score, 2)
    })

output = {
    "generated_at": datetime.utcnow().isoformat(),
    "players": results
}

with open("hit_scores.json", "w") as f:
    json.dump(output, f, indent=4)

print(f"✅ Generated hit_scores.json with {len(results)} batters")

add hit_score.py
