from __future__ import annotations

from pathlib import Path

from shadowflow.models.pipeline import PipelineDefinition


def outputs_for_changed_sql(definition: PipelineDefinition, changed_paths: set[str]) -> set[str]:
    """Map changed SQL file paths (any relative form) to output dataset names."""
    normalized = {_normalize_path(p) for p in changed_paths}
    outputs: set[str] = set()
    for step in definition.steps:
        step_path = _normalize_path(step.path)
        step_name = Path(step.path).name
        if step_path in normalized or step_name in normalized:
            outputs.update(step.outputs)
            continue
        if any(p.endswith(step_name) or p.endswith(step_path) for p in normalized):
            outputs.update(step.outputs)
    return outputs


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")
