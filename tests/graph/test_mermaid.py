from pathlib import Path

from shadowflow.graph.builder import build_graph, load_pipeline_from_dir
from shadowflow.graph.mermaid import graph_to_mermaid


def test_graph_to_mermaid_contains_edges() -> None:
    definition = load_pipeline_from_dir(Path("examples/basic_pipeline/pipeline"))
    pg = build_graph(definition)
    md = graph_to_mermaid(pg)
    assert "flowchart LR" in md
    assert "-->" in md
