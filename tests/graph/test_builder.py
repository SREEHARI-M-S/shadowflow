from pathlib import Path

from shadowflow.graph.builder import build_graph, load_pipeline_from_dir


def test_basic_pipeline_graph() -> None:
    root = Path("examples/basic_pipeline/pipeline")
    definition = load_pipeline_from_dir(root)
    graph = build_graph(definition)
    assert len(graph.edges) >= 3
    names = {n.name for n in graph.nodes}
    assert "users" in names
    assert "customer_metrics" in names
