from __future__ import annotations

from pathlib import Path

from shadowflow.models.pipeline import PipelineDefinition, SqlStep
from shadowflow.parser.sql_parser import extract_table_dependencies


def apply_sql_overrides(
    definition: PipelineDefinition,
    overrides: dict[str, str],
) -> PipelineDefinition:
    """Return a copy of the pipeline with selected steps replaced by override SQL."""
    if not overrides:
        return definition

    normalized = {_normalize_key(k): v for k, v in overrides.items()}
    steps: list[SqlStep] = []
    for step in definition.steps:
        key = _normalize_key(step.path)
        basename = _normalize_key(Path(step.path).name)
        sql = normalized.get(key, normalized.get(basename, step.sql))
        if sql == step.sql:
            steps.append(step)
            continue
        inputs, outputs = extract_table_dependencies(sql)
        steps.append(SqlStep(path=step.path, sql=sql, inputs=inputs, outputs=outputs))
    return PipelineDefinition(name=definition.name, steps=steps)


def _normalize_key(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")
