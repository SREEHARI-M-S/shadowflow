from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console

from shadowflow.graph.analyzer import topological_layers
from shadowflow.graph.builder import build_graph, load_pipeline_from_dir, to_networkx
from shadowflow.graph.models import PipelineGraph

app = typer.Typer(no_args_is_help=True, help="ShadowFlow — pipeline impact analysis")
console = Console()

DEFAULT_CONFIG = """\
project:
  name: my-pipeline

pipeline:
  directory: ./pipeline

data:
  directory: ./data

execution:
  engine: duckdb
"""


class GraphFormat(str, Enum):
    text = "text"
    json = "json"


@app.command()
def init(
    path: Path = typer.Argument(Path("."), help="Project directory to initialize"),
) -> None:
    """Write a default shadowflow.yaml in the project directory."""
    config_path = path / "shadowflow.yaml"
    if config_path.exists():
        console.print(f"[yellow]Already exists:[/yellow] {config_path}")
        raise typer.Exit(code=1)
    config_path.write_text(DEFAULT_CONFIG, encoding="utf-8")
    (path / "pipeline").mkdir(exist_ok=True)
    (path / "data").mkdir(exist_ok=True)
    console.print(f"[green]Created[/green] {config_path}")


@app.command()
def graph(
    project: Path = typer.Argument(..., help="Path to example pipeline root"),
    fmt: GraphFormat = typer.Option(GraphFormat.text, "--format", "-f", help="Output format"),
) -> None:
    """Build and print the dependency graph from SQL files in pipeline/."""
    pipeline_dir = project / "pipeline"
    if not pipeline_dir.is_dir():
        raise typer.BadParameter(f"Missing pipeline directory: {pipeline_dir}")

    definition = load_pipeline_from_dir(pipeline_dir)
    pg = build_graph(definition)
    nx_graph = to_networkx(pg)

    try:
        layers = topological_layers(nx_graph)
    except ValueError as exc:
        console.print(f"[red]Invalid graph:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if fmt == GraphFormat.json:
        console.print(json.dumps(_graph_to_dict(pg, layers), indent=2))
        return

    for layer in layers:
        console.print(" → ".join(layer))
    console.print(f"\n[dim]{len(pg.nodes)} nodes, {len(pg.edges)} edges[/dim]")


def _graph_to_dict(pg: PipelineGraph, layers: list[list[str]]) -> dict[str, object]:
    return {
        "nodes": [n.model_dump() for n in pg.nodes],
        "edges": [e.model_dump() for e in pg.edges],
        "layers": layers,
    }


@app.command()
def version() -> None:
    from shadowflow import __version__

    console.print(f"shadowflow {__version__}")


if __name__ == "__main__":
    app()
