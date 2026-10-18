import networkx as nx

from shadowflow.diff.pipeline_compare import DatasetCompareRow
from shadowflow.impact.propagation import estimate_propagated_impacts


def test_propagate_to_descendants() -> None:
    graph = nx.DiGraph()
    graph.add_edges_from([("clean_users", "enriched_users"), ("enriched_users", "customer_metrics")])
    rows = [
        DatasetCompareRow(
            dataset="clean_users",
            row_before=100,
            row_after=110,
            row_delta=10,
            schema_changed=False,
        ),
    ]
    impacts = estimate_propagated_impacts(graph, {"clean_users"}, rows)
    names = {i.dataset for i in impacts}
    assert names == {"clean_users", "enriched_users", "customer_metrics"}
    direct = next(i for i in impacts if i.dataset == "clean_users")
    assert direct.estimated_pct_change == 10.0
