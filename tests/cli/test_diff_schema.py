from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_diff_schema_no_changes(tmp_path: Path) -> None:
    project = Path("examples/basic_pipeline")
    fp = tmp_path / "fp.json"
    r1 = runner.invoke(app, ["fingerprint", str(project), "--seed", "-o", str(fp)])
    assert r1.exit_code == 0
    r2 = runner.invoke(app, ["diff-schema", str(fp), str(fp), "--json"])
    assert r2.exit_code == 0
    assert '"tables"' in r2.stdout and "[]" in r2.stdout
