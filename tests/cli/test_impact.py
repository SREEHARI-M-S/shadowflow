import json
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


def test_impact_json_includes_risk() -> None:
    project = Path("examples/basic_pipeline")
    result = runner.invoke(
        app,
        ["impact", str(project), "--changed-sql", "pipeline/01_clean_users.sql", "--json"],
    )
    assert result.exit_code == 0
    assert '"risk"' in result.stdout
    assert '"level"' in result.stdout


def test_impact_writes_output_file(tmp_path: Path) -> None:
    out = tmp_path / "impact.json"
    project = Path("examples/basic_pipeline")
    result = runner.invoke(
        app,
        ["impact", str(project), "--changed-sql", "pipeline/01_clean_users.sql", "-o", str(out)],
    )
    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "clean_users" in payload["direct"] or payload["direct"]
