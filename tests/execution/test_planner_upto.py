from pathlib import Path

from shadowflow.execution.planner import order_steps, steps_upto
from shadowflow.graph.builder import load_pipeline_from_dir


def test_steps_upto_stops_at_target_table() -> None:
    definition = load_pipeline_from_dir(Path("examples/basic_pipeline/pipeline"))
    ordered = order_steps(definition)
    prefix = steps_upto(ordered, "enriched_users")
    outputs = {table for step in prefix for table in step.outputs}
    assert "enriched_users" in outputs
    assert "customer_metrics" not in outputs
