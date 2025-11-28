"""
Command Line Interface for Genome Cleaner

This module provides a CLI interface to replicate the main functionality
of the Streamlit application for automation and batch processing.

Author: noomesk
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from .parser import load_sequences, detect_file_format, ParsingError
from .validator import validate_sequences, get_validation_summary
from .stats import generate_report, save_report


console = Console()


def main():
    """Main CLI entry point."""
    cli()


@click.group(invoke_without_command=True)
@click.option('--input', '-i', 'input_file', 
              type=click.Path(exists=True), 
              help='Input FASTA/FASTQ file path')
@click.option('--sanitize', '-s', is_flag=True, 
              help='Enable sanitization mode (clean invalid characters)')
@click.option('--min-length', '-m', default=20, 
              type=int, help='Minimum sequence length (default: 20)')
@click.option('--output', '-o', 
              type=click.Path(), help='Output file path for cleaned sequences')
@click.option('--report', '-r', is_flag=True, 
              help='Generate statistical report')
@click.option('--format', 'report_format', 
              type=click.Choice(['json', 'csv']), 
              default='json', help='Report format (default: json)')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose output')
@click.pass_context
def cli(ctx, input_file, sanitize, min_length, output, report, report_format, verbose):
    """Genome Cleaner - Clean and validate FASTA/FASTQ sequences."""
    
    if ctx.invoked_subcommand is None:
        # Run main processing if no subcommand is specified
        if not input_file:
            click.echo("Error: --input/-i parameter is required when not using subcommands")
            ctx.exit(1)
        
        try:
            process_file(input_file, sanitize, min_length, output, report, report_format, verbose)
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, 
              type=click.Path(exists=True), 
              help='Input file')
@click.option('--output', '-o', required=True, 
              type=click.Path(), 
              help='Output file for cleaned sequences')
@click.option('--min-length', '-m', default=20, 
              type=int, help='Minimum sequence length')
def clean(input_file: str, output: str, min_length: int):
    """Clean sequences by removing invalid characters."""
    sanitize = True
    process_file(input_file, sanitize, min_length, output, report=False, verbose=True)


@cli.command()
@click.option('--input', '-i', required=True, 
              type=click.Path(exists=True), 
              help='Input file')
@click.option('--format', 'report_format', 
              type=click.Choice(['json', 'csv']), 
              default='json', help='Report format')
@click.option('--output', '-o', 
              type=click.Path(), help='Custom report output path')
def report(input_file: str, report_format: str, output: Optional[str]):
    """Generate statistical report only."""
    report = True
    process_file(input_file, sanitize=False, min_length=20, output=None, 
                report=report, report_format=report_format, verbose=True, 
                custom_report_path=output)


def process_file(input_file: str, sanitize: bool, min_length: int, 
                output: Optional[str], report: bool, report_format: str, 
                verbose: bool, custom_report_path: Optional[str] = None):
    """Process a file with validation and optionally generate reports."""
    
    console.print(Panel.fit(
        "[bold blue]Genome Cleaner[/bold blue]\n"
        "Processing sequences...",
        border_style="blue"
    ))
    
    # Detect file format
    file_format = detect_file_format(input_file)
    if verbose:
        console.print(f"[green]Detected format:[/green] {file_format.upper()}")
    
    # Load sequences
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Loading sequences...", total=None)
        
        try:
            sequences = load_sequences(input_file)
            progress.update(task, description="Sequences loaded successfully")
        except ParsingError as e:
            progress.update(task, description="[red]Failed to load sequences[/red]")
            raise click.ClickException(f"Error parsing file: {str(e)}")
        except Exception as e:
            progress.update(task, description="[red]Unexpected error[/red]")
            raise click.ClickException(f"Unexpected error: {str(e)}")
    
    if verbose:
        console.print(f"[green]Loaded {len(sequences)} sequences[/green]")
    
    # Validate sequences
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Validating sequences...", total=len(sequences))
        
        validation_results = validate_sequences(sequences, min_length, sanitize)
        
        progress.update(task, description="Validation complete")
    
    # Generate summary
    summary = get_validation_summary(validation_results)
    
    # Display summary
    _display_summary(summary)
    
    # Save cleaned sequences if requested
    if sanitize and output:
        _save_cleaned_sequences(validation_results, output, verbose)
    
    # Generate report if requested
    if report:
        report_data = generate_report(validation_results)
        report_path = custom_report_path or f"report_{Path(input_file).stem}.{report_format}"
        
        try:
            saved_path = save_report(report_data, report_format, report_path)
            console.print(f"[green]Report saved to: {saved_path}[/green]")
        except Exception as e:
            raise click.ClickException(f"Error saving report: {str(e)}")
    
    # Display invalid sequences if any
    if summary['invalid_sequences'] > 0 and verbose:
        _display_invalid_sequences(validation_results)


def _display_summary(summary: dict):
    """Display validation summary in a nice table."""
    table = Table(title="Validation Summary", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Sequences", str(summary['total_sequences']))
    table.add_row("Valid Sequences", str(summary['valid_sequences']))
    table.add_row("Invalid Sequences", str(summary['invalid_sequences']))
    table.add_row("Sanitized Sequences", str(summary['sanitized_sequences']))
    table.add_row("Duplicate Headers", str(summary['duplicate_headers']))
    table.add_row("Validity Percentage", f"{summary['validity_percentage']:.1f}%")
    
    if summary['error_types']:
        table.add_row("", "")
        table.add_row("Error Types:", "")
        for error_type, count in summary['error_types'].items():
            table.add_row(f"  {error_type}", str(count))
    
    console.print(table)


def _display_invalid_sequences(validation_results: List[dict], limit: int = 10):
    """Display details of invalid sequences."""
    invalid_seqs = [r for r in validation_results if not r['is_valid']]
    
    if not invalid_seqs:
        return
    
    console.print(f"\n[yellow]First {min(limit, len(invalid_seqs))} invalid sequences:[/yellow]")
    
    table = Table(show_header=True)
    table.add_column("Index", style="red")
    table.add_column("Header", style="yellow")
    table.add_column("Length", style="blue")
    table.add_column("Errors", style="red")
    
    for seq in invalid_seqs[:limit]:
        errors = "; ".join(seq['errors'][:2])  # Show first 2 errors
        if len(seq['errors']) > 2:
            errors += f" (+{len(seq['errors'])-2} more)"
        
        table.add_row(
            str(seq['sequence_index']),
            seq['header'][:50] + ("..." if len(seq['header']) > 50 else ""),
            str(seq.get('original_length', 0)),
            errors
        )
    
    console.print(table)
    
    if len(invalid_seqs) > limit:
        console.print(f"[dim]... and {len(invalid_seqs) - limit} more invalid sequences[/dim]")


def _save_cleaned_sequences(validation_results: List[dict], output_path: str, verbose: bool):
    """Save cleaned sequences to file."""
    try:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            for result in validation_results:
                sequence = result.get('corrected_sequence') or result.get('original_sequence', '')
                if sequence:
                    f.write(f">{result['header']}\n")
                    # Write sequence in lines of 60 characters
                    for i in range(0, len(sequence), 60):
                        f.write(sequence[i:i+60] + "\n")
                    f.write("\n")
        
        if verbose:
            console.print(f"[green]Cleaned sequences saved to: {output_path}[/green]")
            
    except Exception as e:
        raise click.ClickException(f"Error saving cleaned sequences: {str(e)}")


if __name__ == "__main__":
    main()
