# Architecture

```text
Git → CLI → SQL parser → Pipeline graph → Execution (DuckDB) → Diff → Impact → Report
```

Pre-merge analysis lives here. Production event forensics belong in **DataTrace**.
