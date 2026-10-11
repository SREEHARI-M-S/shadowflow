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


def run_pipeline(
    definition: PipelineDefinition,
    data_dir: Path,
    *,
    seed_sample_data: bool = False,
    with_profiles: bool = False,
) -> PipelineRunResult:
    if seed_sample_data:
        ensure_basic_pipeline_data(data_dir)

    conn = duckdb.connect()
    for parquet in sorted(data_dir.glob("*.parquet")):
        table = parquet.stem
        conn.execute(
            f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_parquet(?)",
            [str(parquet)],
        )

    for step in order_steps(definition):
        conn.execute(step.sql)

    tables: dict[str, int] = {}
    profiles: dict[str, TableStatistics] = {}
    for step in definition.steps:
        for output in step.outputs:
            count = conn.execute(f"SELECT COUNT(*) FROM {output}").fetchone()
            if count is not None:
                tables[output] = int(count[0])
            if with_profiles and output in tables:
                profiles[output] = profile_table(conn, output)

    conn.close()
    return PipelineRunResult(tables=tables, profiles=profiles)
