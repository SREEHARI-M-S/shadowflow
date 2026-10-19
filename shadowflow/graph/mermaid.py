from __future__ import annotations

from shadowflow.graph.models import PipelineGraph


def graph_to_mermaid(pg: PipelineGraph) -> str:
    lines = ["flowchart LR"]
    for edge in pg.edges:
        src = _mermaid_id(edge.source)
        tgt = _mermaid_id(edge.target)
        lines.append(f"  {src} --> {tgt}")
    if not pg.edges:
        for node in pg.nodes:
            lines.append(f"  {_mermaid_id(node.name)}")
    return "\n".join(lines) + "\n"


def _mermaid_id(name: str) -> str:
    safe = name.replace("-", "_").replace(".", "_")
    return f"n_{safe}"
