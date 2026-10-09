from __future__ import annotations

from pydantic import BaseModel, Field

import networkx as nx

from shadowflow.graph.analyzer import descendants


class BlastRadiusReport(BaseModel):
    direct: list[str] = Field(default_factory=list)
    indirect: list[str] = Field(default_factory=list)

    @property
    def all_affected(self) -> list[str]:
        return sorted(set(self.direct) | set(self.indirect))


def compute_blast_radius(graph: nx.DiGraph, changed_datasets: set[str]) -> BlastRadiusReport:
    """Mark directly changed datasets and all downstream dependents."""
    direct = sorted(changed_datasets)
    indirect_set: set[str] = set()
    for name in changed_datasets:
        indirect_set |= descendants(graph, name)
    indirect_set -= set(direct)
    return BlastRadiusReport(direct=direct, indirect=sorted(indirect_set))
