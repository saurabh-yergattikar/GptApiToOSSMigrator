"""Command-line interface for HarmonyMigrator."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .core.config import Config
from .core.models import BackendType, ModelType, ReasoningEffort
from .scanner import Scanner
from .converter import Converter

app = typer.Typer(
    name="harmony-migrator",
    help="Migrate OpenAI API calls to local GPT-OSS models via Harmony format",
    add_completion=False,
)
console = Console()


@app.command()
def scan(
    repo_path: str = typer.Argument(
        ".",
        help="Path to repository or directory to scan"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output file for scan results (JSON/CSV)"
    ),
    format: str = typer.Option(
        "json",
        "--format",
        help="Output format (json, csv, table)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable verbose output"
    ),
    exclude: Optional[str] = typer.Option(
        None,
        "--exclude",
        help="Exclude patterns (glob)"
    ),
):
    """Scan a codebase for OpenAI API calls."""
    try:
        # Load configuration
        config = Config.load_default()
        config.verbose = verbose
        
        if exclude:
            config.scanning.exclude_patterns.append(exclude)
        
        # Initialize scanner
        scanner = Scanner(config)
        
        # Scan repository
        repo_path_obj = Path(repo_path).resolve()
        if not repo_path_obj.exists():
            console.print(f"[red]Error: Path '{repo_path}' does not exist[/red]")
            raise typer.Exit(1)
        
        result = scanner.scan_repository(repo_path_obj)
        
        # Print summary
        scanner.print_summary(result)
        
        # Save output if specified
        if output:
            if format == "json":
                with open(output, "w") as f:
                    json.dump(result.dict(), f, indent=2, default=str)
                console.print(f"[green]Results saved to {output}[/green]")
            elif format == "csv":
                # TODO: Implement CSV export
                console.print("[yellow]CSV export not yet implemented[/yellow]")
            else:
                console.print(f"[red]Unsupported format: {format}[/red]")
                raise typer.Exit(1)
        
        # Exit with error if no API calls found and output not specified
        if result.api_calls_found == 0 and not output:
            console.print("[yellow]No OpenAI API calls found. No migration needed![/yellow]")
            raise typer.Exit(0)
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def convert(
    repo_path: str = typer.Option(
        ".",
        "--repo", "-r",
        help="Repository path to convert"
    ),
    model: ModelType = typer.Option(
        ModelType.GPT_OSS_20B,
        "--model",
        help="GPT-OSS model to use"
    ),
    backend: BackendType = typer.Option(
        BackendType.OLLAMA,
        "--backend",
        help="Inference backend to use"
    ),
    reasoning_effort: ReasoningEffort = typer.Option(
        ReasoningEffort.MEDIUM,
        "--reasoning-effort",
        help="Harmony reasoning effort level"
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Apply changes to files (default: dry-run)"
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run",
        help="Preview changes without applying"
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        help="Output directory for converted files"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable verbose output"
    ),
):
    """Convert OpenAI API calls to Harmony format."""
    try:
        # Load configuration
        config = Config.load_default()
        config.model = model
        config.backend = backend
        config.reasoning_effort = reasoning_effort
        config.verbose = verbose
        
        # Initialize components
        scanner = Scanner(config)
        converter = Converter(config)
        
        # Scan repository first
        repo_path_obj = Path(repo_path).resolve()
        if not repo_path_obj.exists():
            console.print(f"[red]Error: Path '{repo_path}' does not exist[/red]")
            raise typer.Exit(1)
        
        console.print(f"[bold blue]Scanning repository: {repo_path_obj}[/bold blue]")
        scan_result = scanner.scan_repository(repo_path_obj)
        
        if scan_result.api_calls_found == 0:
            console.print("[yellow]No OpenAI API calls found. Nothing to convert![/yellow]")
            raise typer.Exit(0)
        
        # Convert API calls
        console.print(f"[bold blue]Converting {scan_result.api_calls_found} API calls...[/bold blue]")
        conversion_results = converter.convert_calls(scan_result.calls)
        
        # Print conversion summary
        converter.print_conversion_summary(conversion_results)
        
        # Apply changes if requested
        if apply and not dry_run:
            console.print("[bold green]Applying changes to files...[/bold green]")
            # TODO: Implement file modification
            console.print("[yellow]File modification not yet implemented[/yellow]")
        elif dry_run:
            console.print("[bold yellow]Dry run mode - no changes applied[/bold yellow]")
            console.print("Use --apply to actually modify files")
        
        # Save converted code if output directory specified
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]Saving converted code to {output_dir}[/green]")
            # TODO: Implement file saving
            console.print("[yellow]File saving not yet implemented[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def test(
    model: ModelType = typer.Option(
        ModelType.GPT_OSS_20B,
        "--model",
        help="GPT-OSS model to test"
    ),
    backend: BackendType = typer.Option(
        BackendType.OLLAMA,
        "--backend",
        help="Inference backend to test"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable verbose output"
    ),
):
    """Test local inference setup."""
    try:
        from .inference import LocalInference
        
        console.print(f"[bold blue]Testing {backend.value} backend with {model.value}...[/bold blue]")
        
        # Initialize inference
        inference = LocalInference(model=model.value, backend=backend.value)
        
        # Test connection
        if inference.test_connection():
            console.print("[green]✅ Backend connection successful[/green]")
        else:
            console.print("[red]❌ Backend connection failed[/red]")
            console.print(f"[yellow]Make sure {backend.value} is running and accessible[/yellow]")
            raise typer.Exit(1)
        
        # Get model info
        model_info = inference.get_model_info()
        if verbose:
            console.print(f"[blue]Model info: {model_info}[/blue]")
        
        # Test generation
        test_conversation = {
            "roles": [
                {"name": "developer", "content": "Hello! How are you?"}
            ],
            "channels": [
                {"name": "final", "content": ""}
            ]
        }
        
        console.print("[blue]Testing generation...[/blue]")
        response = inference.generate(test_conversation)
        
        console.print(f"[green]✅ Generation successful![/green]")
        console.print(f"[blue]Response: {response.content[:100]}...[/blue]")
        console.print(f"[blue]Response time: {response.response_time:.2f}s[/blue]")
        
        if response.tokens_used:
            console.print(f"[blue]Tokens used: {response.tokens_used}[/blue]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def config(
    show: bool = typer.Option(
        False,
        "--show",
        help="Show current configuration"
    ),
    init: bool = typer.Option(
        False,
        "--init",
        help="Initialize configuration file"
    ),
    set: Optional[str] = typer.Option(
        None,
        "--set",
        help="Set configuration value (format: key=value)"
    ),
):
    """Manage HarmonyMigrator configuration."""
    try:
        config_path = Path(".harmony-migrator.toml")
        
        if init:
            config = Config()
            config.save_to_file(config_path)
            console.print(f"[green]Configuration file created: {config_path}[/green]")
            return
        
        if set:
            # TODO: Implement configuration setting
            console.print("[yellow]Configuration setting not yet implemented[/yellow]")
            return
        
        if show:
            config = Config.load_default()
            
            table = Table(title="Current Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Model", config.model.value)
            table.add_row("Backend", config.backend.value)
            table.add_row("Reasoning Effort", config.reasoning_effort.value)
            table.add_row("Verbose", str(config.verbose))
            table.add_row("Color Output", str(config.color))
            
            console.print(table)
            return
        
        # Default: show help
        console.print("[yellow]Use --show to display configuration or --init to create config file[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """Show HarmonyMigrator version."""
    from . import __version__
    console.print(f"HarmonyMigrator v{__version__}")


def main():
    """Main entry point."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    main() 