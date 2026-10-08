import json
import psycopg

with open("data/games.json", "r") as file:
    games = json.load(file)

print(f"Loaded {len(games)} games from JSON!")

conn = psycopg.connect(
    dbname = "steam_data"
)

print("Connected to PostgreSQL!")

cursor = conn.cursor()

insert_query = """
INSERT INTO games (
    appid,
    name,
    developer,
    publisher,
    positive,
    negative,
    price_cents,
    initial_price_cents,
    discount,
    ccu
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
ON CONFLICT (appid) DO UPDATE SET
    name = EXCLUDED.name,
    developer = EXCLUDED.developer,
    publisher = EXCLUDED.publisher,
    positive = EXCLUDED.positive,
    negative = EXCLUDED.negative,
    price_cents = EXCLUDED.price_cents,
    initial_price_cents = EXCLUDED.initial_price_cents,
    discount = EXCLUDED.discount,
    ccu = EXCLUDED.ccu;
"""
affected_count = 0

for game in games:
    cursor.execute(
        insert_query,
        (
            game["appid"],
            game["name"],
            game["developer"],
            game["publisher"],
            game["positive"],
            game["negative"],
            game["price"],
            game["initialprice"],
            game["discount"],
            game["ccu"],
        ),
    )
    affected_count += cursor.rowcount
    

try:
    cursor.execute("""
        SELECT COUNT(*)
        FROM games
        WHERE price_cents < 0
           OR discount < 0
           OR discount > 100
           OR name IS NULL
           OR price_cents IS NULL
           OR discount IS NULL;
    """)

    invalid_count = cursor.fetchone()[0]

    if invalid_count > 0:
        raise ValueError(
            f"Validation failed: {invalid_count} invalid game(s) found"
        )

    conn.commit()
    print("Validation passed. Changes committed!")

except Exception:
    conn.rollback()
    print("Validation failed. Changes rolled back!")
    raise

conn.commit()

cursor.close()
conn.close()

print(f"Games inserted or updated: {affected_count}")