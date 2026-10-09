import networkx as nx

from shadowflow.impact.blast_radius import compute_blast_radius


def test_blast_radius_direct_and_indirect() -> None:
    graph = nx.DiGraph()
    graph.add_edges_from(
        [
            ("users", "clean_users"),
            ("clean_users", "enriched_users"),
            ("enriched_users", "customer_metrics"),
        ],
    )
    report = compute_blast_radius(graph, {"clean_users"})
    assert report.direct == ["clean_users"]
    assert report.indirect == ["customer_metrics", "enriched_users"]
