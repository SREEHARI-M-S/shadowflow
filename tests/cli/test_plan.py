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
