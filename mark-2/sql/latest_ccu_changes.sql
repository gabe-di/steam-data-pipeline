
-- Compare the two most recent CCU observations for each game

WITH ranked_snapshots AS (
    SELECT
        g.appid,
        g.name,
        s.collected_at,
        s.ccu,
        LAG(s.ccu) OVER (
            PARTITION BY s.appid
            ORDER BY s.collected_at
        ) AS previous_ccu,
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
    ccu,
    previous_ccu,
    ccu - previous_ccu AS ccu_change
FROM ranked_snapshots
WHERE snapshot_rank = 1
  AND previous_ccu IS NOT NULL
ORDER BY ABS(ccu - previous_ccu) DESC, name
LIMIT 10;
