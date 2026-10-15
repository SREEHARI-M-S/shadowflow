from __future__ import annotations

from pydantic import BaseModel, Field


class TableRowDelta(BaseModel):
    table: str
    before: int
    after: int

    @property
    def delta(self) -> int:
        return self.after - self.before

    @property
    def pct_change(self) -> float | None:
        if self.before == 0:
            return None
        return (self.delta / self.before) * 100.0


class RowCountDiff(BaseModel):
    tables: list[TableRowDelta] = Field(default_factory=list)

    @classmethod
    def compare(cls, before: dict[str, int], after: dict[str, int]) -> RowCountDiff:
        names = sorted(set(before) | set(after))
        deltas = [
            TableRowDelta(
                table=name,
                before=before.get(name, 0),
                after=after.get(name, 0),
            )
            for name in names
        ]
        return cls(tables=deltas)
