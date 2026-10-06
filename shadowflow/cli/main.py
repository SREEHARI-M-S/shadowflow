from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
        from shadowflow.graph.analyzer import topological_layers
from shadowflow.graph.builder import build_graph, load_pipeline_from_dir, to_networkx

app = typer.Typer(no_args_is_help=True, help="ShadowFlow — pipeline impact analysis")
console = Console()


@app.command()
def graph(
    project: Path = typer.Argument(..., help="Path to example pipeline root"),
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
                raise typer.Exit(code=1) from exc

            for layer in layers:
        console.print(" → ".join(layer))

    console.print(f"\n[dim]{len(pg.nodes)} nodes, {len(pg.edges)} edges[/dim]")


@app.command()
def version() -> None:
    from shadowflow import __version__

    console.print(f"shadowflow {__version__}")


if __name__ == "__main__":
    app()
