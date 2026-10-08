CREATE OR REPLACE VIEW game_prices AS
SELECT
    appid,
    name,
    ROUND(price_cents / 100.0, 2) AS price_dollars,
    ROUND(initial_price_cents / 100.0, 2) AS initial_price_dollars,
    discount
FROM games;