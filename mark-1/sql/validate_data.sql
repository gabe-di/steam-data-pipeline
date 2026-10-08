SELECT COUNT(*) AS invalid_prices
FROM game_prices
WHERE price_dollars < 0;

SELECT COUNT(*) AS invalid_discounts
FROM game_prices
WHERE discount > 100 OR discount < 0;

SELECT
    (SELECT COUNT(*) FROM games) AS source_count,
    (SELECT COUNT(*) FROM game_prices) AS view_count;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM games
        WHERE price_cents < 0
    ) THEN
        RAISE EXCEPTION 'Validation failed: negative prices found';
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM games
        WHERE discount < 0 OR discount > 100
    ) THEN
        RAISE EXCEPTION 'Validation failed: invalid discounts found';
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM games
        WHERE appid IS NULL
           OR name IS NULL
           OR price_cents IS NULL
           OR discount IS NULL
    ) THEN
        RAISE EXCEPTION 'Validation failed: missing required values';
    END IF;
END $$;