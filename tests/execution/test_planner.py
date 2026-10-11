from shadowflow.execution.planner import order_steps
from shadowflow.graph.builder import load_pipeline_from_dir
from pathlib import Path


def test_steps_ordered_by_dependencies() -> None:
    definition = load_pipeline_from_dir(Path("examples/basic_pipeline/pipeline"))
    steps = order_steps(definition)
    names = [Path(s.path).name for s in steps]
    assert names.index("01_clean_users.sql") < names.index("02_enrich_users.sql")
    assert names.index("02_enrich_users.sql") < names.index("03_customer_metrics.sql")
