from pathlib import Path

from shadowflow.diff.pipeline_compare import DatasetCompareRow, PipelineCompareReport
from shadowflow.execution.history import load_compare_report, save_compare_report


def test_save_and_load_compare_report(tmp_path: Path) -> None:
    report = PipelineCompareReport(
        datasets=[
            DatasetCompareRow(
                dataset="t",
                row_before=1,
                row_after=2,
                row_delta=1,
                schema_changed=False,
            ),
        ],
    )
    path = save_compare_report(tmp_path, report)
    assert path.is_file()
    loaded = load_compare_report(tmp_path)
    assert loaded is not None
    assert loaded.datasets[0].row_after == 2
