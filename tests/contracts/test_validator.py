from pathlib import Path

import duckdb

from shadowflow.contracts.validator import load_contract, validate_dataset_contract


def test_validate_clean_users_contract() -> None:
    contract = load_contract(Path("examples/basic_pipeline/contracts/clean_users.yaml"))
    conn = duckdb.connect()
    conn.execute("CREATE TABLE clean_users AS SELECT 1::BIGINT AS user_id UNION ALL SELECT 3")
    result = validate_dataset_contract(conn, contract)
    conn.close()
    assert result.ok
