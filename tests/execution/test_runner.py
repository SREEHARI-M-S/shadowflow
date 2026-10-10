from pathlib import Path

from shadowflow.execution.runner import run_pipeline
from shadowflow.graph.builder import load_pipeline_from_dir


def test_run_basic_pipeline_with_seed(tmp_path: Path) -> None:
    project = Path("examples/basic_pipeline")
    data_dir = tmp_path / "data"
    pipeline_dir = project / "pipeline"
    definition = load_pipeline_from_dir(pipeline_dir)
    result = run_pipeline(definition, data_dir, seed_sample_data=True)
    assert result.tables["clean_users"] == 2
    assert result.tables["enriched_users"] == 2
    assert result.tables["customer_metrics"] == 2
