from __future__ import annotations

from pathlib import Path

import networkx as nx

from shadowflow.graph.models import DatasetNode, DependencyEdge, NodeKind, PipelineGraph
from shadowflow.models.pipeline import PipelineDefinition, SqlStep
from shadowflow.parser.sql_parser import extract_table_dependencies


def load_pipeline_from_dir(pipeline_dir: Path) -> PipelineDefinition:
    steps: list[SqlStep] = []
    for path in sorted(pipeline_dir.glob("*.sql")):
        sql = path.read_text(encoding="utf-8")
        inputs, outputs = extract_table_dependencies(sql)
        steps.append(
            SqlStep(path=str(path), sql=sql, inputs=inputs, outputs=outputs),
        )
    return PipelineDefinition(name=pipeline_dir.name, steps=steps)


def build_graph(definition: PipelineDefinition) -> PipelineGraph:
    node_names: set[str] = set()
    edges: list[DependencyEdge] = []

    for step in definition.steps:
        for name in step.inputs + step.outputs:
            node_names.add(name)
        for out in step.outputs:
            for inp in step.inputs:
                edges.append(DependencyEdge(source=inp, target=out))

    nodes = [
        DatasetNode(name=n, kind=NodeKind.EXTERNAL if _is_external(n, definition) else NodeKind.DATASET)
        for n in sorted(node_names)
    ]
    return PipelineGraph(nodes=nodes, edges=edges)


def to_networkx(graph: PipelineGraph) -> nx.DiGraph:
    g: nx.DiGraph = nx.DiGraph()
    for node in graph.nodes:
        g.add_node(node.name, kind=node.kind.value)
    for edge in graph.edges:
        g.add_edge(edge.source, edge.target)
    return g


def _is_external(name: str, definition: PipelineDefinition) -> bool:
    produced = {out for step in definition.steps for out in step.outputs}
    return name not in produced
