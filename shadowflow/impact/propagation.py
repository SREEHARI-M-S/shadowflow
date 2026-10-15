from __future__ import annotations

from pydantic import BaseModel, Field

from shadowflow.diff.row_diff import TableRowDelta


class PropagatedImpact(BaseModel):
    """Estimated relative row-count change per dataset (direct seeds only for now)."""

    dataset: str
    estimated_pct_change: float | None = None
    source: str = Field(description="direct seed or propagated")


def estimate_from_row_delta(
    seeds: set[str],
    delta: TableRowDelta,
) -> list[PropagatedImpact]:
    """Map a direct table row delta to seed + placeholder downstream estimates."""
    impacts: list[PropagatedImpact] = []
    if delta.table in seeds:
        impacts.append(
            PropagatedImpact(
                dataset=delta.table,
                estimated_pct_change=delta.pct_change,
                source="direct",
            ),
        )
    return impacts
