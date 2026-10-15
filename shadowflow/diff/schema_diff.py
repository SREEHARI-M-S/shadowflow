from __future__ import annotations

from pydantic import BaseModel, Field

from shadowflow.diff.statistics import TableStatistics


class SchemaDiff(BaseModel):
    added_columns: list[str] = Field(default_factory=list)
    removed_columns: list[str] = Field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.added_columns or self.removed_columns)


class TableSchemaDiff(BaseModel):
    table: str
    diff: SchemaDiff


class FingerprintSchemaDiff(BaseModel):
    tables: list[TableSchemaDiff] = Field(default_factory=list)


def diff_fingerprint_schemas(
    before_columns: dict[str, list[str]],
    after_columns: dict[str, list[str]],
) -> FingerprintSchemaDiff:
    from shadowflow.diff.statistics import TableStatistics

    names = sorted(set(before_columns) | set(after_columns))
    tables: list[TableSchemaDiff] = []
    for name in names:
        diff = diff_schema(
            TableStatistics(name=name, row_count=0, columns=before_columns.get(name, [])),
            TableStatistics(name=name, row_count=0, columns=after_columns.get(name, [])),
        )
        if diff.changed:
            tables.append(TableSchemaDiff(table=name, diff=diff))
    return FingerprintSchemaDiff(tables=tables)


def diff_schema(before: TableStatistics, after: TableStatistics) -> SchemaDiff:
    before_cols = set(before.columns)
    after_cols = set(after.columns)
    return SchemaDiff(
        added_columns=sorted(after_cols - before_cols),
        removed_columns=sorted(before_cols - after_cols),
    )
