"""CLI for GEOFlow Agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from geoflow.pipeline import GEOFlowPipeline

app = typer.Typer(help="GEOFlow Agent — AI-citable real estate content")
console = Console()


@app.command()
def run(
    input_file: str = typer.Argument(..., help="JSON file with raw listings"),
    output: str = typer.Option("./geo-content", "--output", "-o"),
    min_trust: float = typer.Option(0.0, "--min-trust", "-t"),
    market_avg: float = typer.Option(0.0, "--market-avg", "-m"),
) -> None:
    """Process listings through GEO pipeline."""
    data = json.loads(Path(input_file).read_text(encoding="utf-8"))
    listings = data if isinstance(data, list) else data.get("listings", [])

    pipeline = GEOFlowPipeline(
        output_dir=output,
        min_trust=min_trust,
        market_avg=market_avg,
    )
    published = pipeline.run(listings)

    table = Table(title="GEOFlow Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Scraped", str(pipeline.stats["scraped"]))
    table.add_row("Entities", str(pipeline.stats["entities"]))
    table.add_row("Published", str(pipeline.stats["published"]))
    table.add_row("Avg Trust", str(pipeline.stats["avg_trust"]))

    console.print(table)
    console.print(f"[bold green]Output: {output}[/bold green]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
