CREATE TABLE clean_users AS
SELECT *
FROM users
WHERE active = true;
