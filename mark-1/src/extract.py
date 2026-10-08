import requests
import json

url = "https://steamspy.com/api.php?request=top100in2weeks"

response = requests.get(url)

data = response.json()

games = []

for app_key, game in data.items():
    clean_game = {
        "appid": game["appid"],
        "name": game["name"],
        "developer": game["developer"],
        "publisher": game["publisher"],
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

with open("data/games.json", "w") as file:
    json.dump(games, file, indent=4)

print(f"Extracted {len(games)} games!")