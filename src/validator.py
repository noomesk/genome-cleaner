"""
Sequence Validation and Cleaning Module

This module provides functions to validate sequences against various criteria
and clean/sanitize sequences when requested.

Author: noomesk
"""

import re
from typing import Dict, List, Optional, Set
from collections import Counter


def validate_sequence(header: str, sequence: str, min_length: int = 20, sanitize: bool = False) -> Dict:
    """Validate a single sequence against various criteria.
    
    Args:
        header (str): Sequence header/identifier
        sequence (str): DNA sequence
        min_length (int): Minimum acceptable sequence length
        sanitize (bool): If True, attempt to clean invalid characters
        
    Returns:
        Dict: Validation result containing:
            - is_valid (bool): Whether sequence passed all validations
            - errors (List[str]): List of validation errors
            - corrected_sequence (str): Sanitized sequence (if sanitize=True)
            - warnings (List[str]): List of warnings
    """
    result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "corrected_sequence": sequence if sanitize else None,
        "header": header,
        "original_length": len(sequence),
        "corrected_length": len(sequence) if sanitize else None
    }
    
    # Check for empty sequence
    if not sequence.strip():
        result["is_valid"] = False
        result["errors"].append("Empty sequence")
        return result
    
    # Convert to uppercase for processing
    seq_upper = sequence.upper().replace(" ", "").replace("\t", "").replace("\n", "")
    
    # Check for invalid characters
    valid_chars_pattern = r'^[ACGTN]*$'  # Only A, C, G, T, N allowed
    invalid_chars = []
    
    if not re.match(valid_chars_pattern, seq_upper):
        # Find which characters are invalid
        for char in seq_upper:
            if char not in 'ACGTN':
                invalid_chars.append(char)
        
        if invalid_chars:
            error_msg = f"Invalid characters found: {', '.join(set(invalid_chars))}"
            result["errors"].append(error_msg)
            result["is_valid"] = False
            
            if sanitize:
                # Remove invalid characters and replace with 'N'
                corrected = re.sub(r'[^ACGTN]', 'N', seq_upper)
                result["corrected_sequence"] = corrected
                result["corrected_length"] = len(corrected)
    else:
        result["corrected_sequence"] = seq_upper if sanitize else sequence
    
    # Check minimum length
    final_sequence = result["corrected_sequence"] if sanitize else seq_upper
    if len(final_sequence) < min_length:
        error_msg = f"Sequence too short: {len(final_sequence)} bp (minimum: {min_length} bp)"
        result["errors"].append(error_msg)
        result["is_valid"] = False
    
    # Check for sequences with only N's (likely low quality)
    if final_sequence and all(char == 'N' for char in final_sequence):
        result["warnings"].append("Sequence contains only N characters (likely low quality)")
    
    # Check for very low complexity (repetitive sequences)
    if _is_low_complexity(final_sequence):
        result["warnings"].append("Low complexity sequence detected")
    
    return result


def validate_sequences(sequences: List[tuple], min_length: int = 20, sanitize: bool = False) -> List[Dict]:
    """Validate multiple sequences and detect duplicate headers.
    
    Args:
        sequences (List[tuple]): List of (header, sequence) tuples
        min_length (int): Minimum acceptable sequence length
        sanitize (bool): If True, attempt to clean invalid characters
        
    Returns:
        List[Dict]: List of validation results for each sequence
    """
    # First pass: collect all headers to detect duplicates
    headers = [seq[0] for seq in sequences]
    header_counts = Counter(headers)
    duplicate_headers = {header for header, count in header_counts.items() if count > 1}
    
    results = []
    
    for i, (header, sequence) in enumerate(sequences):
        result = validate_sequence(header, sequence, min_length, sanitize)
        
        # Add duplicate header check
        if header in duplicate_headers:
            duplicate_count = header_counts[header]
            error_msg = f"Duplicate header found ({duplicate_count} occurrences)"
            result["errors"].append(error_msg)
            result["is_valid"] = False
        
        # Add sequence index for reference
        result["sequence_index"] = i
        
        results.append(result)
    
    return results


def _is_low_complexity(sequence: str, min_unique_chars: int = 4, min_unique_ratio: float = 0.3) -> bool:
    """Check if a sequence has low complexity (repetitive).
    
    Args:
        sequence (str): DNA sequence
        min_unique_chars (int): Minimum number of unique characters
        min_unique_ratio (float): Minimum ratio of unique to total characters
        
    Returns:
        bool: True if sequence appears to have low complexity
    """
    if len(sequence) < 10:  # Skip very short sequences
        return False
    
    unique_chars = set(sequence.upper())
    unique_ratio = len(unique_chars) / len(sequence)
    
    return len(unique_chars) < min_unique_chars or unique_ratio < min_unique_ratio


def calculate_gc_content(sequence: str) -> float:
    """Calculate GC content percentage of a sequence.
    
    Args:
        sequence (str): DNA sequence
        
    Returns:
        float: GC content percentage (0-100)
    """
    if not sequence:
        return 0.0
    
    seq_upper = sequence.upper()
    gc_count = seq_upper.count('G') + seq_upper.count('C')
    at_count = seq_upper.count('A') + seq_upper.count('T')
    valid_bases = gc_count + at_count
    
    if valid_bases == 0:
        return 0.0
    
    return (gc_count / valid_bases) * 100


def calculate_sequence_stats(sequence: str) -> Dict:
    """Calculate various statistics for a sequence.
    
    Args:
        sequence (str): DNA sequence
        
    Returns:
        Dict: Sequence statistics
    """
    if not sequence:
        return {
            "length": 0,
            "gc_content": 0.0,
            "a_count": 0,
            "t_count": 0,
            "g_count": 0,
            "c_count": 0,
            "n_count": 0,
            "valid_chars": 0
        }
    
    seq_upper = sequence.upper()
    
    stats = {
        "length": len(seq_upper),
        "gc_content": calculate_gc_content(seq_upper),
        "a_count": seq_upper.count('A'),
        "t_count": seq_upper.count('T'),
        "g_count": seq_upper.count('G'),
        "c_count": seq_upper.count('C'),
        "n_count": seq_upper.count('N'),
        "valid_chars": seq_upper.count('A') + seq_upper.count('T') + 
                      seq_upper.count('G') + seq_upper.count('C')
    }
    
    return stats


def filter_valid_sequences(validation_results: List[Dict]) -> List[Dict]:
    """Filter validation results to return only valid sequences.
    
    Args:
        validation_results (List[Dict]): List of validation results
        
    Returns:
        List[Dict]: List of validation results for valid sequences only
    """
    return [result for result in validation_results if result["is_valid"]]


def get_validation_summary(validation_results: List[Dict]) -> Dict:
    """Generate a summary of validation results.
    
    Args:
        validation_results (List[Dict]): List of validation results
        
    Returns:
        Dict: Summary statistics
    """
    if not validation_results:
        return {
            "total_sequences": 0,
            "valid_sequences": 0,
            "invalid_sequences": 0,
            "sanitized_sequences": 0,
            "duplicate_headers": 0,
            "total_errors": 0,
            "error_types": {}
        }
    
    total = len(validation_results)
    valid = sum(1 for result in validation_results if result["is_valid"])
    invalid = total - valid
    
    sanitized = sum(1 for result in validation_results 
                   if result.get("corrected_sequence") and 
                   result.get("corrected_sequence") != result.get("original_sequence", ""))
    
    # Count duplicate headers
    duplicate_headers = sum(1 for result in validation_results 
                          if any("Duplicate header" in error for error in result["errors"]))
    
    # Count total errors and types
    all_errors = []
    for result in validation_results:
        all_errors.extend(result["errors"])
    
    error_type_counts = Counter()
    for error in all_errors:
        if "Invalid characters" in error:
            error_type_counts["Invalid characters"] += 1
        elif "too short" in error:
            error_type_counts["Too short"] += 1
        elif "Duplicate header" in error:
            error_type_counts["Duplicate headers"] += 1
        elif "Empty sequence" in error:
            error_type_counts["Empty sequence"] += 1
        else:
            error_type_counts["Other"] += 1
    
    return {
        "total_sequences": total,
        "valid_sequences": valid,
        "invalid_sequences": invalid,
        "sanitized_sequences": sanitized,
        "duplicate_headers": duplicate_headers,
        "total_errors": len(all_errors),
        "error_types": dict(error_type_counts),
        "validity_percentage": (valid / total) * 100 if total > 0 else 0
    }
