-- Rank discounted games by positive review percentage
-- Include only games with at least 1,000 total reviews

SELECT
    name,
    positive,
    negative,
    positive + negative AS total_reviews,
    ROUND(
        100.0 * positive / NULLIF(positive + negative, 0),
        2
    ) AS positive_review_pct,
    ROUND(price_cents / 100.0, 2) AS price_dollars,
    discount
FROM games
WHERE positive + negative >= 1000
  AND discount > 0
ORDER BY positive_review_pct DESC, total_reviews DESC
LIMIT 10;