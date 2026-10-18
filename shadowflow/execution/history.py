from __future__ import annotations

import json
from pathlib import Path

from shadowflow.diff.pipeline_compare import PipelineCompareReport


def save_compare_report(project: Path, report: PipelineCompareReport) -> Path:
    out_dir = project / ".shadowflow"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / "last-compare.json"
    path.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
    return path


def load_compare_report(project: Path) -> PipelineCompareReport | None:
    path = project / ".shadowflow" / "last-compare.json"
    if not path.is_file():
        return None
    return PipelineCompareReport.model_validate_json(path.read_text(encoding="utf-8"))
