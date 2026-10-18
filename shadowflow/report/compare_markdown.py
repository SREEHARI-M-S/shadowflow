from __future__ import annotations

from shadowflow.diff.pipeline_compare import PipelineCompareReport


def compare_report_markdown(report: PipelineCompareReport) -> str:
    lines = [
        "# ShadowFlow differential compare",
        "",
        "## Changed SQL",
        "",
    ]
    if report.changed_sql:
        lines.extend(f"- `{path}`" for path in report.changed_sql)
    else:
        lines.append("- _(none listed)_")
    lines.extend(
        [
            "",
            "## Dataset row counts",
            "",
            "| Dataset | Before | After | Delta | Schema changed |",
            "| --- | ---: | ---: | ---: | --- |",
        ],
    )
    for row in report.datasets:
        schema = "yes" if row.schema_changed else "no"
        lines.append(
            f"| `{row.dataset}` | {row.row_before} | {row.row_after} | {row.row_delta} | {schema} |",
        )
    if report.propagated:
        lines.extend(
            [
                "",
                "## Estimated propagation",
                "",
                "| Dataset | Est. % change | Source |",
                "| --- | ---: | --- |",
            ],
        )
        for item in report.propagated:
            pct = f"{item.estimated_pct_change:.2f}" if item.estimated_pct_change is not None else "—"
            lines.append(f"| `{item.dataset}` | {pct} | {item.source} |")
    if report.risk is not None:
        lines.extend(
            [
                "",
                "## Risk",
                "",
                f"**Level:** {report.risk.level}  ",
                f"**Score:** {report.risk.score}",
                "",
            ],
        )
    lines.append(f"**Affected datasets:** {len(report.affected_datasets)}")
    lines.append("")
    return "\n".join(lines)
