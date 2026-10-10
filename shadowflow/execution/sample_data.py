from __future__ import annotations

from pathlib import Path

import duckdb


def ensure_basic_pipeline_data(data_dir: Path) -> None:
    """Create minimal Parquet inputs for examples/basic_pipeline if missing."""
    data_dir.mkdir(parents=True, exist_ok=True)
    users_path = data_dir / "users.parquet"
    tx_path = data_dir / "customer_transactions.parquet"
    if users_path.is_file() and tx_path.is_file():
        return

    conn = duckdb.connect()
    conn.execute(
        f"""
        COPY (
            SELECT * FROM (
                VALUES
                    (1::BIGINT, true),
                    (2::BIGINT, false),
                    (3::BIGINT, true)
            ) AS t(user_id, active)
        ) TO '{users_path.as_posix()}' (FORMAT PARQUET)
        """,
    )
    conn.execute(
        f"""
        COPY (
            SELECT * FROM (
                VALUES
                    (1::BIGINT, 120.5::DOUBLE),
                    (3::BIGINT, 45.0::DOUBLE)
            ) AS t(user_id, total_spend)
        ) TO '{tx_path.as_posix()}' (FORMAT PARQUET)
        """,
    )
    conn.close()
