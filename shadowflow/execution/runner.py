from __future__ import annotations

from pathlib import Path

import duckdb

from shadowflow.diff.statistics import TableStatistics, profile_table
from shadowflow.execution.planner import order_steps
from shadowflow.execution.sample_data import ensure_basic_pipeline_data
from shadowflow.models.pipeline import PipelineDefinition


class PipelineRunResult:
    def __init__(
        self,
        tables: dict[str, int],
        profiles: dict[str, TableStatistics] | None = None,
    ) -> None:
        self.tables = tables
        self.profiles = profiles or {}


def execute_on_connection(
    conn: duckdb.DuckDBPyConnection,
    definition: PipelineDefinition,
    data_dir: Path,
    *,
    seed_sample_data: bool = False,
) -> None:
    if seed_sample_data:
        ensure_basic_pipeline_data(data_dir)

    for parquet in sorted(data_dir.glob("*.parquet")):
        table = parquet.stem
        conn.execute(
            f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_parquet(?)",
            [str(parquet)],
        )

    for step in order_steps(definition):
        conn.execute(step.sql)


def _collect_results(
    conn: duckdb.DuckDBPyConnection,
    definition: PipelineDefinition,
    with_profiles: bool,
) -> PipelineRunResult:
    tables: dict[str, int] = {}
    profiles: dict[str, TableStatistics] = {}
    for step in definition.steps:
        for output in step.outputs:
            count = conn.execute(f"SELECT COUNT(*) FROM {output}").fetchone()
            if count is not None:
                tables[output] = int(count[0])
            if with_profiles and output in tables:
                profiles[output] = profile_table(conn, output)
    return PipelineRunResult(tables=tables, profiles=profiles)


def run_pipeline(
    definition: PipelineDefinition,
    data_dir: Path,
    *,
    seed_sample_data: bool = False,
    with_profiles: bool = False,
) -> PipelineRunResult:
    conn = duckdb.connect()
    execute_on_connection(conn, definition, data_dir, seed_sample_data=seed_sample_data)
    result = _collect_results(conn, definition, with_profiles)
    conn.close()
    return result


def run_pipeline_open(
    definition: PipelineDefinition,
    data_dir: Path,
    *,
    seed_sample_data: bool = False,
    with_profiles: bool = False,
) -> tuple[PipelineRunResult, duckdb.DuckDBPyConnection]:
    """Run pipeline and return an open DuckDB connection (caller must close)."""
    conn = duckdb.connect()
    execute_on_connection(conn, definition, data_dir, seed_sample_data=seed_sample_data)
    return _collect_results(conn, definition, with_profiles), conn
