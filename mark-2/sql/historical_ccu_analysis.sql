
-- Historical concurrent player analysis
-- Compares each game's CCU with its previous snapshot

SELECT
    g.appid,
    g.name,
    s.collected_at,
    s.ccu,
    LAG(s.ccu) OVER (
        PARTITION BY s.appid
        ORDER BY s.collected_at
    ) AS previous_ccu,
    s.ccu - LAG(s.ccu) OVER (
        PARTITION BY s.appid
        ORDER BY s.collected_at
    ) AS ccu_change
FROM game_snapshots AS s
JOIN games AS g
    ON s.appid = g.appid
ORDER BY g.name, s.collected_at;
