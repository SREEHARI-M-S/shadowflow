CREATE TABLE enriched_users AS
SELECT
    u.*,
    t.total_spend
FROM clean_users AS u
LEFT JOIN customer_transactions AS t
    ON u.user_id = t.user_id;
