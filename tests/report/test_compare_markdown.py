from shadowflow.diff.compare_rows import DatasetCompareRow
from shadowflow.diff.pipeline_compare import PipelineCompareReport
from shadowflow.impact.propagation import PropagatedImpact
from shadowflow.report.compare_markdown import compare_report_markdown


def test_compare_report_markdown_includes_tables() -> None:
    report = PipelineCompareReport(
        changed_sql=["pipeline/01_clean_users.sql"],
        affected_datasets=["users_clean"],
        datasets=[
            DatasetCompareRow(
                dataset="users_clean",
                row_before=100,
                row_after=95,
                row_delta=-5,
                schema_changed=False,
            ),
        ],
        propagated=[
            PropagatedImpact(dataset="users_clean", estimated_pct_change=-5.0, source="direct"),
        ],
    )
    md = compare_report_markdown(report)
    assert "users_clean" in md
    assert "| 100 | 95 | -5 |" in md
    assert "Estimated propagation" in md
