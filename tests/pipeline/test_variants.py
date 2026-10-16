from shadowflow.graph.builder import load_pipeline_from_dir
from shadowflow.pipeline.variants import apply_sql_overrides
from pathlib import Path


def test_apply_sql_override_reparses_dependencies() -> None:
    definition = load_pipeline_from_dir(Path("examples/basic_pipeline/pipeline"))
    new_sql = "CREATE TABLE clean_users AS SELECT user_id FROM users WHERE active = true;"
    updated = apply_sql_overrides(definition, {"01_clean_users.sql": new_sql})
    step = next(s for s in updated.steps if s.path.endswith("01_clean_users.sql"))
    assert step.outputs == ["clean_users"]
    assert "users" in step.inputs
