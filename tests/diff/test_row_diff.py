from shadowflow.diff.row_diff import RowCountDiff


def test_row_count_diff() -> None:
    diff = RowCountDiff.compare({"a": 10}, {"a": 15, "b": 1})
    assert diff.tables[0].delta == 5
    assert any(t.table == "b" for t in diff.tables)
