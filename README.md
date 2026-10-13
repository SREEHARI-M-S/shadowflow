# ShadowFlow

[![version](https://img.shields.io/badge/version-0.1.6-blue)](https://github.com/SREEHARI-M-S/shadowflow/commits/main)

**Repository:** [github.com/SREEHARI-M-S/shadowflow](https://github.com/SREEHARI-M-S/shadowflow)  
**Latest on `main`:** [commit history](https://github.com/SREEHARI-M-S/shadowflow/commits/main) (look for `0e00641` or newer)

**Debug your data, not just your code.**

ShadowFlow predicts the behavioral impact of data pipeline changes by replaying
old and new versions against historical data, diffing outputs, and propagating
impact through the dependency graph.

## Status

Active development — CLI, DuckDB runs, impact/risk/report, YAML config. See [CHANGELOG.md](CHANGELOG.md).

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e ".[dev]"
shadowflow --help
shadowflow init .
shadowflow graph examples/basic_pipeline
shadowflow graph examples/basic_pipeline --format json
shadowflow analyze examples/basic_pipeline
shadowflow impact examples/basic_pipeline --changed-sql pipeline/01_clean_users.sql
shadowflow run examples/basic_pipeline --seed --profile
shadowflow report examples/basic_pipeline --changed-sql pipeline/01_clean_users.sql -o impact.md
shadowflow risk examples/basic_pipeline --changed-sql pipeline/01_clean_users.sql
```

## Docs

See [docs/architecture.md](docs/architecture.md).

## License

MIT
