CREATE TABLE customer_metrics AS
SELECT
    user_id,
    COUNT(*) AS txn_count,
    SUM(total_spend) AS lifetime_spend
FROM enriched_users
GROUP BY user_id;
