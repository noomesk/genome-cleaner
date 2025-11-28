"""
FASTA/FASTQ Parser Module

This module provides functions to parse FASTA and FASTQ files and extract sequences
with their corresponding headers.

Author: noomesk
"""

import re
from typing import List, Tuple
from pathlib import Path


class ParsingError(Exception):
    """Custom exception for parsing errors."""
    pass


def _is_fasta_format(file_content: str) -> bool:
    """Check if the file content is in FASTA format.
    
    Args:
        file_content (str): Raw file content
        
    Returns:
        bool: True if file appears to be FASTA format
    """
    lines = file_content.strip().split('\n')
    if not lines:
        return False
    
    # FASTA files start with '>' and have sequences on subsequent lines
    for i, line in enumerate(lines[:10]):  # Check first 10 lines
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            return True
        # If we find sequence lines before any header, it's not FASTA
        if i > 0 and not line.startswith('>'):
            return False
    
    return False


def load_sequences(file_path: str) -> List[Tuple[str, str]]:
    """Load and parse sequences from FASTA or FASTQ files.
    
    Args:
        file_path (str): Path to the FASTA/FASTQ file
        
    Returns:
        List[Tuple[str, str]]: List of (header, sequence) tuples
        
    Raises:
        ParsingError: If the file format is invalid or cannot be read
        FileNotFoundError: If the file does not exist
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            raise ParsingError("File is empty")
        
        sequences = []
        
        if _is_fasta_format(content):
            sequences = _parse_fasta(content)
        else:
            sequences = _parse_fastq(content)
            
        if not sequences:
            raise ParsingError("No valid sequences found in file")
            
        return sequences
        
    except (IOError, OSError) as e:
        raise ParsingError(f"Error reading file: {str(e)}")
    except Exception as e:
        raise ParsingError(f"Unexpected error parsing file: {str(e)}")


def _parse_fasta(content: str) -> List[Tuple[str, str]]:
    """Parse FASTA format content.
    
    Args:
        content (str): FASTA file content
        
    Returns:
        List[Tuple[str, str]]: List of (header, sequence) tuples
    """
    sequences = []
    lines = content.strip().split('\n')
    current_header = None
    current_sequence = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('>'):
            # Save previous sequence if exists
            if current_header is not None:
                sequence = ''.join(current_sequence)
                if sequence:  # Only add if sequence is not empty
                    sequences.append((current_header, sequence))
            
            current_header = line[1:].strip()  # Remove '>' prefix
            current_sequence = []
        else:
            # Sequence line
            current_sequence.append(line)
    
    # Add the last sequence
    if current_header is not None:
        sequence = ''.join(current_sequence)
        if sequence:
            sequences.append((current_header, sequence))
    
    return sequences


def _parse_fastq(content: str) -> List[Tuple[str, str]]:
    """Parse FASTQ format content.
    
    Args:
        content (str): FASTQ file content
        
    Returns:
        List[Tuple[str, str]]: List of (header, sequence) tuples
    """
    sequences = []
    lines = content.strip().split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # FASTQ records start with '@'
        if line.startswith('@'):
            header = line[1:].strip()  # Remove '@' prefix
            
            # Next line should be the sequence
            if i + 1 < len(lines):
                sequence = lines[i + 1].strip()
                
                # Skip quality line and separator if they exist
                if i + 3 < len(lines):
                    i += 4  # Move past @header, sequence, +, quality
                else:
                    i += 2  # Move past header and sequence only
                
                if sequence:  # Only add if sequence is not empty
                    sequences.append((header, sequence))
            else:
                # Incomplete record, skip
                i += 1
        else:
            i += 1
    
    return sequences


def detect_file_format(file_path: str) -> str:
    """Detect whether a file is FASTA or FASTQ format.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: "fasta", "fastq", or "unknown"
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return "unknown"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read first few lines to detect format
            lines = []
            for _ in range(10):
                line = f.readline().strip()
                if line:
                    lines.append(line)
                else:
                    break
        
        if not lines:
            return "unknown"
        
        # Check for FASTQ (@ headers)
        for line in lines[:5]:
            if line.startswith('@'):
                # Check if next line contains valid sequence characters
                return "fastq"
        
        # Check for FASTA (> headers)
        for line in lines[:5]:
            if line.startswith('>'):
                return "fasta"
        
        return "unknown"
        
    except Exception:
        return "unknown"
