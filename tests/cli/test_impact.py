from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_impact_with_changed_sql() -> None:
    project = Path("examples/basic_pipeline")
    result = runner.invoke(
        app,
        [
            "impact",
            str(project),
            "--changed-sql",
            "pipeline/01_clean_users.sql",
        ],
    )
    assert result.exit_code == 0
    assert "clean_users" in result.stdout
    assert "enriched_users" in result.stdout
