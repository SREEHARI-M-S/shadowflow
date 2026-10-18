from __future__ import annotations

import networkx as nx
from pydantic import BaseModel, Field

from shadowflow.diff.compare_rows import DatasetCompareRow


class PropagatedImpact(BaseModel):
    dataset: str
    estimated_pct_change: float | None = None
    source: str = Field(description="direct or propagated")


def estimate_propagated_impacts(
    graph: nx.DiGraph,
    seeds: set[str],
    dataset_rows: list[DatasetCompareRow],
) -> list[PropagatedImpact]:
    """Estimate % row change on direct seeds and propagate the same factor downstream."""
    pct_by_seed: dict[str, float] = {}
    for row in dataset_rows:
        if row.dataset not in seeds:
            continue
        if row.row_before <= 0:
            continue
        pct_by_seed[row.dataset] = (row.row_delta / row.row_before) * 100.0

    impacts: list[PropagatedImpact] = []
    seen: set[str] = set()
    for seed, pct in pct_by_seed.items():
        for dataset in [seed, *nx.descendants(graph, seed)]:
            if dataset in seen:
                continue
            seen.add(dataset)
            impacts.append(
                PropagatedImpact(
                    dataset=dataset,
                    estimated_pct_change=round(pct, 4),
                    source="direct" if dataset == seed else f"from:{seed}",
                ),
            )
    return sorted(impacts, key=lambda i: i.dataset)
