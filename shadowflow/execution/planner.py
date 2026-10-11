from __future__ import annotations

import networkx as nx

from shadowflow.graph.builder import build_graph, to_networkx
from shadowflow.models.pipeline import PipelineDefinition, SqlStep


def order_steps(definition: PipelineDefinition) -> list[SqlStep]:
    """Return pipeline steps in dependency order (inputs before outputs)."""
    graph = to_networkx(build_graph(definition))
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Pipeline graph contains a cycle")

    step_by_output: dict[str, SqlStep] = {}
    for step in definition.steps:
        for output in step.outputs:
            step_by_output[output] = step

    ordered_outputs: list[str] = []
    for layer in nx.topological_generations(graph):
        for node in layer:
            if node in step_by_output:
                ordered_outputs.append(node)

    seen: set[str] = set()
    ordered_steps: list[SqlStep] = []
    for output in ordered_outputs:
        step = step_by_output[output]
        key = step.path
        if key in seen:
            continue
        seen.add(key)
        ordered_steps.append(step)

    for step in definition.steps:
        if step.path not in seen:
            ordered_steps.append(step)
    return ordered_steps
