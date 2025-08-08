"""Command-line interface for HarmonyMigrator."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .analyzer.cost_analyzer import CostAnalyzer
from .scanner.scanner import Scanner

app = typer.Typer(help="Migrate OpenAI API calls to local models")
console = Console()


@app.command()
def scan(
    path: str = typer.Argument(..., help="Path to scan for OpenAI API calls"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
):
    """Scan codebase for OpenAI API calls."""
    console.print(f"🔍 Scanning: {path}")
    
    scanner = Scanner()
    api_calls = scanner.scan_directory(path)
    
    if not api_calls:
        console.print("✨ No OpenAI API calls found!")
        return
    
    # Create results table
    table = Table(title="📊 OpenAI API Calls Found")
    table.add_column("File", style="cyan")
    table.add_column("Line", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Complexity", style="yellow")
    
    for call in api_calls:
        table.add_row(
            Path(call.file).name,
            str(call.line),
            call.type,
            call.complexity
        )
    
    console.print(table)
    
    if verbose:
        for call in api_calls:
            console.print(f"\n[cyan]Details for {call.file}:{call.line}[/cyan]")
            console.print(call.to_dict())


@app.command()
def analyze(
    path: str = typer.Argument(..., help="Path to analyze for costs"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export results to file"),
):
    """Analyze OpenAI API costs."""
    console.print(f"💰 Analyzing costs for: {path}")
    
    # Scan for API calls
    scanner = Scanner()
    api_calls = scanner.scan_directory(path)
    
    if not api_calls:
        console.print("✨ No OpenAI API calls found!")
        return
    
    # Analyze costs
    analyzer = CostAnalyzer()
    estimate = analyzer.analyze_calls(api_calls)
    
    # Generate report
    report = analyzer.generate_report(estimate)
    console.print(report)
    
    if export:
        with open(export, 'w') as f:
            f.write(report)
        console.print(f"\n✅ Report exported to: {export}")


@app.command()
def migrate(
    path: str = typer.Argument(..., help="Path to migrate"),
    type: str = typer.Option("chat", help="Type of migration (chat, completion, embedding)"),
    dry_run: bool = typer.Option(True, help="Show changes without applying"),
):
    """Migrate OpenAI API calls to local models."""
    console.print("🚧 Migration feature coming soon!")
    console.print("Current support:")
    console.print("✅ API call detection")
    console.print("✅ Cost analysis")
    console.print("⏳ Basic chat migration (in development)")


if __name__ == "__main__":
    app()