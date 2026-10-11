from shadowflow.diff.schema_diff import diff_schema
from shadowflow.diff.statistics import TableStatistics


def test_schema_diff_detects_column_changes() -> None:
    before = TableStatistics(name="t", row_count=1, columns=["a", "b"])
    after = TableStatistics(name="t", row_count=1, columns=["a", "c"])
    diff = diff_schema(before, after)
    assert diff.added_columns == ["c"]
    assert diff.removed_columns == ["b"]
