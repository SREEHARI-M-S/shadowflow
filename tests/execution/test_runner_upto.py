from pathlib import Path

from shadowflow.execution.runner import run_pipeline
from shadowflow.graph.builder import load_pipeline_from_dir


def test_run_upto_stops_before_downstream_tables(tmp_path: Path) -> None:
    project = Path("examples/basic_pipeline")
    definition = load_pipeline_from_dir(project / "pipeline")
    result = run_pipeline(
        definition,
        tmp_path / "data",
        seed_sample_data=True,
        upto_table="enriched_users",
    )
    assert "enriched_users" in result.tables
    assert "customer_metrics" not in result.tables
