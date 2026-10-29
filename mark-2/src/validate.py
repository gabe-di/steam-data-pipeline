import os
import psycopg

# Connect to Mark II database
database_url = os.getenv("DATABASE_URL")

if database_url:
    conn = psycopg.connect(database_url)
else:
    conn = psycopg.connect(dbname="steam_data_mk2")

checks = {
    "Orphaned snapshots": """
        SELECT COUNT(*)
        FROM game_snapshots AS s
        LEFT JOIN games AS g
            ON s.appid = g.appid
        WHERE g.appid IS NULL;
    """,

    "Invalid snapshots": """
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
    """,

    "Duplicate snapshots": """
        SELECT COUNT(*)
        FROM (
            SELECT appid, collected_at
            FROM game_snapshots
            GROUP BY appid, collected_at
            HAVING COUNT(*) > 1
        ) AS duplicates;
    """
}

try:
    with conn.cursor() as cursor:
        for check_name, query in checks.items():
            cursor.execute(query)
            invalid_count = cursor.fetchone()[0]

            if invalid_count > 0:
                raise ValueError(
                    f"{check_name} failed: {invalid_count} invalid records"
                )

            print(f"{check_name}: PASSED")

    print("All database validation checks passed!!")

finally:
    conn.close()
