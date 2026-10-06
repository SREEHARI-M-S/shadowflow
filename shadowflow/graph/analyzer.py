from __future__ import annotations

import networkx as nx


def descendants(graph: nx.DiGraph, node: str) -> set[str]:
    if node not in graph:
        return set()
    return nx.descendants(graph, node)


def ancestors(graph: nx.DiGraph, node: str) -> set[str]:
    if node not in graph:
        return set()
    return nx.ancestors(graph, node)


def topological_layers(graph: nx.DiGraph) -> list[list[str]]:
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Pipeline graph contains a cycle")
    layers: list[list[str]] = []
    for generation in nx.topological_generations(graph):
        layers.append(list(generation))
    return layers
