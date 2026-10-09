# ShadowFlow

**Debug your data, not just your code.**

ShadowFlow predicts the behavioral impact of data pipeline changes by replaying
old and new versions against historical data, diffing outputs, and propagating
impact through the dependency graph.

## Status

Early development — Phase 1 (parser, graph, CLI) is in place.

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
```

## Docs

See [docs/architecture.md](docs/architecture.md).

## License

MIT
