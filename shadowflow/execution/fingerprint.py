from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, Field

from shadowflow.diff.statistics import TableStatistics


class DatasetFingerprint(BaseModel):
    table: str
    row_count: int
    schema_hash: str
    columns: list[str] = Field(default_factory=list)


class PipelineFingerprint(BaseModel):
    datasets: list[DatasetFingerprint] = Field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2, sort_keys=True)


def schema_hash(columns: list[str]) -> str:
    payload = ",".join(columns).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def load_fingerprint(path: Path) -> PipelineFingerprint:
    data = json.loads(path.read_text(encoding="utf-8"))
    return PipelineFingerprint.model_validate(data)


def build_fingerprint(profiles: dict[str, TableStatistics], counts: dict[str, int]) -> PipelineFingerprint:
    datasets: list[DatasetFingerprint] = []
    for name in sorted(counts):
        stats = profiles.get(name)
        columns = stats.columns if stats else []
        datasets.append(
            DatasetFingerprint(
                table=name,
                row_count=counts[name],
                schema_hash=schema_hash(columns),
                columns=columns,
            ),
        )
    return PipelineFingerprint(datasets=datasets)
