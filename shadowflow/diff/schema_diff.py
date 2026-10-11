from __future__ import annotations

from pydantic import BaseModel, Field

from shadowflow.diff.statistics import TableStatistics


class SchemaDiff(BaseModel):
    added_columns: list[str] = Field(default_factory=list)
    removed_columns: list[str] = Field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.added_columns or self.removed_columns)


def diff_schema(before: TableStatistics, after: TableStatistics) -> SchemaDiff:
    before_cols = set(before.columns)
    after_cols = set(after.columns)
    return SchemaDiff(
        added_columns=sorted(after_cols - before_cols),
        removed_columns=sorted(before_cols - after_cols),
    )
