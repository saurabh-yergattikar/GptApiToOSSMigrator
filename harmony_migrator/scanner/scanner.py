"""Main scanner class for detecting OpenAI API calls."""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.config import Config
from ..core.models import APICall, CallType, ComplexityLevel, ScanResult
from .detectors import PythonDetector, JavaScriptDetector


class Scanner:
    """Scans codebases for OpenAI API calls and generates reports."""
    
    def __init__(self, config: Config):
        self.config = config
        self.console = Console()
        self.detectors = {
            ".py": PythonDetector(),
            ".js": JavaScriptDetector(),
            ".ts": JavaScriptDetector(),
        }
    
    def scan_repository(self, repo_path: Path) -> ScanResult:
        """Scan a repository for OpenAI API calls."""
        self.console.print(f"[bold blue]Scanning repository: {repo_path}[/bold blue]")
        
        # Find all relevant files
        files_to_scan = self._find_files_to_scan(repo_path)
        
        if not files_to_scan:
            self.console.print("[yellow]No files found to scan.[/yellow]")
            return ScanResult(
                total_files_scanned=0,
                api_calls_found=0,
                estimated_monthly_savings="$0.00",
                migration_complexity=ComplexityLevel.SIMPLE,
                calls=[],
            )
        
        # Scan files for API calls
        all_calls = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Scanning files...", total=len(files_to_scan))
            
            for file_path in files_to_scan:
                progress.update(task, description=f"Scanning {file_path.name}")
                calls = self._scan_file(file_path)
                all_calls.extend(calls)
                progress.advance(task)
        
        # Generate report
        return self._generate_scan_result(all_calls, len(files_to_scan))
    
    def _find_files_to_scan(self, repo_path: Path) -> List[Path]:
        """Find all files that should be scanned."""
        files = []
        
        # Convert exclude patterns to regex patterns
        exclude_patterns = []
        for pattern in self.config.scanning.exclude_patterns:
            # Convert glob patterns to regex
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            exclude_patterns.append(re.compile(regex_pattern))
        
        # Parse max file size
        max_size = self._parse_file_size(self.config.scanning.max_file_size)
        
        for file_path in repo_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            # Check file extension
            if file_path.suffix not in self.detectors:
                continue
            
            # Check exclude patterns
            relative_path = file_path.relative_to(repo_path)
            if any(pattern.match(str(relative_path)) for pattern in exclude_patterns):
                continue
            
            # Check file size
            if file_path.stat().st_size > max_size:
                continue
            
            files.append(file_path)
        
        return files
    
    def _scan_file(self, file_path: Path) -> List[APICall]:
        """Scan a single file for OpenAI API calls."""
        try:
            detector = self.detectors.get(file_path.suffix)
            if not detector:
                return []
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            return detector.detect_calls(content, file_path)
        
        except Exception as e:
            if self.config.verbose:
                self.console.print(f"[red]Error scanning {file_path}: {e}[/red]")
            return []
    
    def _generate_scan_result(self, calls: List[APICall], files_scanned: int) -> ScanResult:
        """Generate a scan result from detected calls."""
        if not calls:
            return ScanResult(
                total_files_scanned=files_scanned,
                api_calls_found=0,
                estimated_monthly_savings="$0.00",
                migration_complexity=ComplexityLevel.SIMPLE,
                calls=[],
            )
        
        # Calculate complexity
        complexity = self._calculate_complexity(calls)
        
        # Estimate monthly savings
        total_tokens = sum(call.estimated_tokens for call in calls)
        monthly_savings = self._estimate_monthly_savings(total_tokens)
        
        return ScanResult(
            total_files_scanned=files_scanned,
            api_calls_found=len(calls),
            estimated_monthly_savings=monthly_savings,
            migration_complexity=complexity,
            calls=calls,
        )
    
    def _calculate_complexity(self, calls: List[APICall]) -> ComplexityLevel:
        """Calculate the overall complexity of migration."""
        if not calls:
            return ComplexityLevel.SIMPLE
        
        # Count different types of calls
        call_types = {}
        for call in calls:
            call_types[call.call_type] = call_types.get(call.call_type, 0) + 1
        
        # Determine complexity based on call types and counts
        total_calls = len(calls)
        has_functions = CallType.FUNCTION_CALL in call_types
        
        if total_calls <= 5 and not has_functions:
            return ComplexityLevel.SIMPLE
        elif total_calls <= 20 or (has_functions and total_calls <= 10):
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.COMPLEX
    
    def _estimate_monthly_savings(self, total_tokens: int) -> str:
        """Estimate monthly cost savings based on token count."""
        # Rough estimate: $0.002 per 1K tokens for GPT-3.5-turbo
        # Assuming 100 API calls per month
        monthly_calls = 100
        cost_per_1k_tokens = 0.002
        monthly_tokens = total_tokens * monthly_calls
        monthly_cost = (monthly_tokens / 1000) * cost_per_1k_tokens
        
        return f"${monthly_cost:.2f}"
    
    def _parse_file_size(self, size_str: str) -> int:
        """Parse file size string to bytes."""
        size_str = size_str.upper()
        
        if size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith("B"):
            return int(size_str[:-1])
        else:
            return int(size_str)
    
    def print_summary(self, result: ScanResult) -> None:
        """Print a summary of scan results."""
        self.console.print("\n[bold green]Scan Complete![/bold green]\n")
        
        # Summary table
        summary_data = [
            ["Files Scanned", str(result.total_files_scanned)],
            ["API Calls Found", str(result.api_calls_found)],
            ["Migration Complexity", result.migration_complexity.value.title()],
            ["Estimated Monthly Savings", result.estimated_monthly_savings],
        ]
        
        from rich.table import Table
        table = Table(title="Scan Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        for metric, value in summary_data:
            table.add_row(metric, value)
        
        self.console.print(table)
        
        # Call details
        if result.calls:
            self.console.print("\n[bold]Detected API Calls:[/bold]")
            for i, call in enumerate(result.calls[:10], 1):  # Show first 10
                self.console.print(
                    f"  {i}. {call.file_path.name}:{call.line_number} "
                    f"({call.call_type.value}) - {call.complexity.value}"
                )
            
            if len(result.calls) > 10:
                self.console.print(f"  ... and {len(result.calls) - 10} more calls")
        
        # Recommendations
        self.console.print("\n[bold]Recommendations:[/bold]")
        if result.api_calls_found == 0:
            self.console.print("  ✅ No OpenAI API calls found - no migration needed!")
        elif result.migration_complexity == ComplexityLevel.SIMPLE:
            self.console.print("  🟢 Simple migration - ready to convert!")
        elif result.migration_complexity == ComplexityLevel.MEDIUM:
            self.console.print("  🟡 Medium complexity - review function calls")
        else:
            self.console.print("  🔴 Complex migration - manual review recommended") 