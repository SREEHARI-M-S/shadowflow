from shadowflow.diff.row_diff import TableRowDelta
from shadowflow.impact.propagation import estimate_from_row_delta


def test_estimate_direct_seed() -> None:
    delta = TableRowDelta(table="clean_users", before=100, after=110)
    impacts = estimate_from_row_delta({"clean_users"}, delta)
    assert len(impacts) == 1
    assert impacts[0].estimated_pct_change == 10.0
