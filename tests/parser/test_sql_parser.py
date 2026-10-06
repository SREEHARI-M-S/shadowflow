from shadowflow.parser.sql_parser import extract_table_dependencies


def test_create_table_as_select() -> None:
    sql = """
    CREATE TABLE clean_users AS
    SELECT * FROM raw_users;
    """
    inputs, outputs = extract_table_dependencies(sql)
    assert inputs == ["raw_users"]
    assert outputs == ["clean_users"]


def test_join_dependencies() -> None:
    sql = """
    CREATE TABLE enriched_users AS
    SELECT *
    FROM clean_users
    JOIN transactions ON clean_users.id = transactions.user_id;
    """
    inputs, outputs = extract_table_dependencies(sql)
    assert set(inputs) == {"clean_users", "transactions"}
    assert outputs == ["enriched_users"]
