from __future__ import annotations

from pydantic import BaseModel, Field

import duckdb


class TableStatistics(BaseModel):
    name: str
    row_count: int = Field(ge=0)
    columns: list[str] = Field(default_factory=list)


def profile_table(conn: duckdb.DuckDBPyConnection, table: str) -> TableStatistics:
    row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    count = int(row[0]) if row else 0
    describe = conn.execute(f"DESCRIBE {table}").fetchall()
    columns = [str(row[0]) for row in describe]
    return TableStatistics(name=table, row_count=count, columns=columns)
