from pathlib import Path

from shadowflow.diff.pipeline_compare import compare_pipeline_variants
from shadowflow.graph.builder import load_pipeline_from_dir


def test_compare_stricter_filter_reduces_rows() -> None:
    definition = load_pipeline_from_dir(Path("examples/basic_pipeline/pipeline"))
    baseline_sql = (Path("examples/basic_pipeline/pipeline/01_clean_users.sql")).read_text(
        encoding="utf-8",
    )
    stricter_sql = """
CREATE TABLE clean_users AS
SELECT *
FROM users
WHERE active = true AND user_id < 3;
"""
    report = compare_pipeline_variants(
        definition,
        Path("compare_test_data"),
        before_overrides={"01_clean_users.sql": baseline_sql},
        after_overrides={"01_clean_users.sql": stricter_sql},
        changed_paths={"pipeline/01_clean_users.sql"},
        seed_sample_data=True,
    )
    clean = next(r for r in report.datasets if r.dataset == "clean_users")
    assert clean.row_after < clean.row_before
    assert clean.row_delta < 0
