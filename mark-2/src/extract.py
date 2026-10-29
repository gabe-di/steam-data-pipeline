import requests
import json
from datetime import datetime, timezone
from pathlib import Path
url = "https://steamspy.com/api.php?request=top100in2weeks"

response = requests.get(url)

data = response.json()

games = []

collected_at = datetime.now(timezone.utc).isoformat()

for app_key, game in data.items():
    clean_game = {
        "appid": game["appid"],
        "name": game["name"],
        "developer": game["developer"],
        "publisher": game["publisher"],
        "collected_at": collected_at,
        "positive": game["positive"],
        "negative": game["negative"],
        "price": int(game["price"]),
        "initialprice": int(game["initialprice"]),
        "discount": int(game["discount"]),
        "ccu": game["ccu"]
    }

    games.append(clean_game)

if not games:
    raise ValueError("Extraction failed: no games were returned")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

with open(DATA_DIR / "games.json", "w") as file:
    json.dump(games, file, indent=4)

print(f"Extracted {len(games)} games!")