from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_plan_json_lists_steps_in_order() -> None:
    project = Path("examples/basic_pipeline")
    result = runner.invoke(app, ["plan", str(project), "--json"])
    assert result.exit_code == 0
    assert "01_clean_users.sql" in result.stdout
    assert result.stdout.index("01_clean_users") < result.stdout.index("03_customer_metrics")


def test_plan_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "plan.json"
    project = Path("examples/basic_pipeline")
    result = runner.invoke(app, ["plan", str(project), "-o", str(out)])
    assert result.exit_code == 0
    assert out.read_text(encoding="utf-8").strip().startswith("[")


def test_plan_upto_limits_steps() -> None:
    project = Path("examples/basic_pipeline")
    result = runner.invoke(app, ["plan", str(project), "--json", "--upto", "enriched_users"])
    assert result.exit_code == 0
    assert "03_customer_metrics" not in result.stdout
    assert "02_enrich_users.sql" in result.stdout
