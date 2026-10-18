from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from shadowflow.diff.row_diff import RowCountDiff
from shadowflow.diff.schema_diff import FingerprintSchemaDiff, diff_fingerprint_schemas
from shadowflow.execution.fingerprint import build_fingerprint
from shadowflow.execution.runner import run_pipeline
from shadowflow.graph.builder import build_graph, to_networkx
from shadowflow.graph.change_detection import outputs_for_changed_sql
from shadowflow.impact.blast_radius import BlastRadiusReport, compute_blast_radius
from shadowflow.diff.compare_rows import DatasetCompareRow
from shadowflow.impact.propagation import PropagatedImpact, estimate_propagated_impacts
from shadowflow.impact.risk import RiskAssessment, assess_blast_radius
from shadowflow.models.pipeline import PipelineDefinition
from shadowflow.pipeline.variants import apply_sql_overrides

# Re-export for callers that import from pipeline_compare
__all__ = ["DatasetCompareRow", "PipelineCompareReport", "compare_pipeline_variants"]


class PipelineCompareReport(BaseModel):
    changed_sql: list[str] = Field(default_factory=list)
    affected_datasets: list[str] = Field(default_factory=list)
    datasets: list[DatasetCompareRow] = Field(default_factory=list)
    propagated: list[PropagatedImpact] = Field(default_factory=list)
    blast_radius: BlastRadiusReport | None = None
    risk: RiskAssessment | None = None
    row_diff: RowCountDiff | None = None
    schema_diff: FingerprintSchemaDiff | None = None


def compare_pipeline_variants(
    definition: PipelineDefinition,
    data_dir: Path,
    before_overrides: dict[str, str],
    after_overrides: dict[str, str],
    *,
    changed_paths: set[str],
    seed_sample_data: bool = False,
) -> PipelineCompareReport:
    before_def = apply_sql_overrides(definition, before_overrides)
    after_def = apply_sql_overrides(definition, after_overrides)

    before_run = run_pipeline(before_def, data_dir, seed_sample_data=seed_sample_data, with_profiles=True)
    after_run = run_pipeline(after_def, data_dir, seed_sample_data=False, with_profiles=True)

    seeds = outputs_for_changed_sql(definition, changed_paths)
    graph = to_networkx(build_graph(definition))
    blast = compute_blast_radius(graph, seeds)
    affected = set(blast.all_affected)

    before_fp = build_fingerprint(before_run.profiles, before_run.tables)
    after_fp = build_fingerprint(after_run.profiles, after_run.tables)
    row_diff = RowCountDiff.compare(before_run.tables, after_run.tables)
    schema_diff = diff_fingerprint_schemas(
        {d.table: d.columns for d in before_fp.datasets},
        {d.table: d.columns for d in after_fp.datasets},
    )

    schema_by_table = {t.table: t.diff.changed for t in schema_diff.tables}
    datasets: list[DatasetCompareRow] = []
    for name in sorted(affected):
        if name not in before_run.tables and name not in after_run.tables:
            continue
        before_count = before_run.tables.get(name, 0)
        after_count = after_run.tables.get(name, 0)
        datasets.append(
            DatasetCompareRow(
                dataset=name,
                row_before=before_count,
                row_after=after_count,
                row_delta=after_count - before_count,
                schema_changed=schema_by_table.get(name, False),
            ),
        )

    propagated = estimate_propagated_impacts(graph, seeds, datasets)
    return PipelineCompareReport(
        changed_sql=sorted(changed_paths),
        affected_datasets=sorted(affected),
        datasets=datasets,
        propagated=propagated,
        blast_radius=blast,
        risk=assess_blast_radius(blast),
        row_diff=row_diff,
        schema_diff=schema_diff,
    )
