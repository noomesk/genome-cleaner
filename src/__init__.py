# Genome Cleaner - Bioinformatic Sequence Processing Tool
# Author: noomesk
# License: MIT License


"""
Genome Cleaner: A comprehensive tool for cleaning and validating FASTA/FASTQ sequences.

This package provides:
- FASTA/FASTQ file parsing
- Sequence validation and sanitization
- Statistical analysis and reporting
- Streamlit web interface
- Command-line interface
"""

__version__ = "1.0.0"
__author__ = "noomesk"

from .parser import load_sequences
from .validator import validate_sequence
from .stats import generate_report, save_report

__all__ = [
    "load_sequences",
    "validate_sequence", 
    "generate_report",
    "save_report"
]
