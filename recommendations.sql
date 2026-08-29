-- =====================================================
-- Personalized Ad/Product Recommender — SQL Queries
-- =====================================================
-- Tables:
--   browsing_history(user_id, product_id, product_name, category,
--                     view_count, purchased, event_date)
--   recommendations(user_id, recommended_product_id, rank,
--                    recommendation_score, most_similar_user, similarity_score)
--
-- Run automatically by recommender.py against recommender.db.
-- =====================================================

-- 1. Most frequently recommended products across all users
SELECT
    recommended_product_id,
    COUNT(*) AS times_recommended,
    ROUND(AVG(recommendation_score), 2) AS avg_recommendation_score
FROM recommendations
GROUP BY recommended_product_id
ORDER BY times_recommended DESC;


-- 2. Recommendation coverage — how many users received recommendations,
-- and how many recommendations were generated on average
SELECT
    COUNT(DISTINCT user_id) AS users_with_recommendations,
    COUNT(*) AS total_recommendations,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT user_id), 2) AS avg_recs_per_user
FROM recommendations;


-- 3. Category distribution of raw browsing activity
-- (which categories get the most views overall)
SELECT
    category,
    COUNT(*) AS total_views,
    SUM(CASE WHEN purchased = 'Yes' THEN 1 ELSE 0 END) AS total_purchases
FROM browsing_history
GROUP BY category
ORDER BY total_views DESC;


-- 4. Top user-similarity pairs used to generate recommendations
SELECT DISTINCT
    user_id,
    most_similar_user,
    similarity_score
FROM recommendations
ORDER BY similarity_score DESC
LIMIT 10;


-- 5. Purchase rate by category (conversion signal)
SELECT
    category,
    COUNT(*) AS total_interactions,
    SUM(CASE WHEN purchased = 'Yes' THEN 1 ELSE 0 END) AS purchases,
    ROUND(SUM(CASE WHEN purchased = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS purchase_rate_pct
FROM browsing_history
GROUP BY category
ORDER BY purchase_rate_pct DESC;
