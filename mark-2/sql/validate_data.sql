
-- Steam Data Pipeline Mark II
-- Database integrity and data quality checks

-- Test 1: Find snapshots without a matching game
SELECT COUNT(*) AS orphaned_snapshots
FROM game_snapshots AS s
LEFT JOIN games AS g
    ON s.appid = g.appid
WHERE g.appid IS NULL;

-- Test 2: Find invalid numerical values
SELECT COUNT(*) AS invalid_snapshots
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

-- Test 3: Find duplicate snapshot keys
SELECT COUNT(*) AS duplicate_snapshot_groups
FROM (
    SELECT appid, collected_at
    FROM game_snapshots
    GROUP BY appid, collected_at
    HAVING COUNT(*) > 1
) AS duplicates;
