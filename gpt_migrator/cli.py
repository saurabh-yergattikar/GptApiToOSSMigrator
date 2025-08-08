"""Command-line interface for HarmonyMigrator."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .analyzer.cost_analyzer import CostAnalyzer
from .migrator.basic_migrator import BasicMigrator
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
    console.print(f"🔄 Migrating: {path}")
    
    # Read the file
    try:
        with open(path, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        console.print(f"❌ File not found: {path}")
        return
    
    # Check if we can migrate this code
    migrator = BasicMigrator()
    if not migrator.can_migrate(code):
        console.print("❌ This code cannot be migrated with current version")
        console.print("Supported patterns:")
        for pattern in migrator.supported_patterns:
            console.print(f"  - {pattern}")
        return
    
    # Perform migration
    result = migrator.migrate_chat_completion(code)
    
    # Show results
    console.print("\n📝 Migration Results:")
    console.print("=" * 30)
    
    for change in result.changes_made:
        console.print(f"✅ {change}")
    
    if result.warnings:
        console.print("\n⚠️  Warnings:")
        for warning in result.warnings:
            console.print(f"  - {warning}")
    
    if dry_run:
        console.print("\n📄 Migrated Code Preview:")
        console.print("-" * 30)
        console.print(result.migrated_code)
        
        console.print("\n🔧 Response Parser Code:")
        console.print("-" * 30)
        console.print(migrator.generate_response_parser(code))
    else:
        # Write migrated code
        backup_path = f"{path}.backup"
        with open(backup_path, 'w') as f:
            f.write(result.original_code)
        
        with open(path, 'w') as f:
            f.write(result.migrated_code)
        
        console.print(f"\n✅ Migration completed!")
        console.print(f"📁 Backup saved to: {backup_path}")
        console.print(f"📝 Original file updated: {path}")


if __name__ == "__main__":
    app()