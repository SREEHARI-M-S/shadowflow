from pathlib import Path

from typer.testing import CliRunner

from shadowflow.cli.main import app

runner = CliRunner()


def test_fingerprint_and_diff_counts(tmp_path: Path) -> None:
    project = Path("examples/basic_pipeline")
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    r1 = runner.invoke(app, ["fingerprint", str(project), "--seed", "-o", str(before)])
    assert r1.exit_code == 0
    r2 = runner.invoke(app, ["fingerprint", str(project), "--seed", "-o", str(after)])
    assert r2.exit_code == 0
    r3 = runner.invoke(app, ["diff-counts", str(before), str(after), "--json"])
    assert r3.exit_code == 0
    assert '"tables"' in r3.stdout
