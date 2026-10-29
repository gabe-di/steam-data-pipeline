import os
import json
import psycopg
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "data" / "games.json", "r") as file:
    games = json.load(file)

print(f"Loaded {len(games)} games from JSON!")

database_url = os.getenv("DATABASE_URL")

if database_url:
    conn = psycopg.connect(database_url)
else:
    conn = psycopg.connect(dbname="steam_data_mk2")

print("Connected to PostgreSQL!")

cursor = conn.cursor()

insert_query = """
INSERT INTO games (
    appid,
    name,
    developer,
    publisher
)
VALUES (%s, %s, %s, %s)
ON CONFLICT (appid) DO UPDATE SET
    name = EXCLUDED.name,
    developer = EXCLUDED.developer,
    publisher = EXCLUDED.publisher;
"""

snapshot_query = """
INSERT INTO game_snapshots (
    appid,
    collected_at,
    positive,
    negative,
    price,
    initialprice,
    discount,
    ccu
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (appid, collected_at) DO NOTHING;
"""

snapshots_inserted = 0

try:
    for game in games:
        cursor.execute(
            insert_query,
            (
                game["appid"],
                game["name"],
                game["developer"],
                game["publisher"],
            ),
        )

        cursor.execute(
            snapshot_query,
            (
                game["appid"],
                game["collected_at"],
                game["positive"],
                game["negative"],
                game["price"],
                game["initialprice"],
                game["discount"],
                game["ccu"],
            ),
        )

        snapshots_inserted += cursor.rowcount

    cursor.execute("""
        SELECT COUNT(*)
        FROM game_snapshots
        WHERE price < 0
           OR initialprice < 0
           OR positive < 0
           OR negative < 0
           OR ccu < 0
           OR discount < 0
           OR discount > 100
           OR price IS NULL
           OR discount IS NULL;
    """)

    invalid_count = cursor.fetchone()[0]

    if invalid_count > 0:
        raise ValueError(
            f"Validation failed: {invalid_count} invalid snapshot(s) found"
        )

    conn.commit()
    print("Validation passed. Changes committed!")

except Exception:
    conn.rollback()
    print("Validation failed. Changes rolled back!")
    raise

finally:
    cursor.close()
    conn.close()

print(f"Snapshots inserted: {snapshots_inserted}")
