
-- Compare the two most recent price observations for each game

WITH price_history AS (
    SELECT
        g.appid,
        g.name,
        s.collected_at,
        s.price,
        LAG(s.price) OVER (
            PARTITION BY s.appid
            ORDER BY s.collected_at
        ) AS previous_price,
        ROW_NUMBER() OVER (
            PARTITION BY s.appid
            ORDER BY s.collected_at DESC
        ) AS snapshot_rank
    FROM game_snapshots AS s
    JOIN games AS g
        ON s.appid = g.appid
)
SELECT
    name,
    collected_at,
    ROUND(price / 100.0, 2) AS current_price_usd,
    ROUND(previous_price / 100.0, 2) AS previous_price_usd,
    ROUND((price - previous_price) / 100.0, 2) AS price_change_usd
FROM price_history
WHERE snapshot_rank = 1
  AND previous_price IS NOT NULL
ORDER BY ABS(price - previous_price) DESC, name
LIMIT 10;
