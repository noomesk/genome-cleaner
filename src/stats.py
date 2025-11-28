"""
Statistics and Reporting Module

This module provides functions to generate statistical reports and save them
in various formats (CSV, JSON).

Author: noomesk
"""

import json
import csv
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path


def generate_report(validation_results: List[Dict]) -> Dict:
    """Generate comprehensive statistical report from validation results.
    
    Args:
        validation_results (List[Dict]): List of validation results from validator
        
    Returns:
        Dict: Comprehensive report containing all statistics
    """
    if not validation_results:
        return _empty_report()
    
    # Basic counts
    total_seqs = len(validation_results)
    valid_seqs = sum(1 for result in validation_results if result["is_valid"])
    invalid_seqs = total_seqs - valid_seqs
    sanitized_seqs = 0
    duplicate_headers = 0
    
    # Length statistics
    lengths = []
    gc_contents = []
    sequence_stats = []
    
    # Error tracking
    error_details = []
    invalid_sequences = []
    
    for i, result in enumerate(validation_results):
        # Track sanitization
        if (result.get("corrected_sequence") and 
            result.get("corrected_sequence") != result.get("original_sequence", "")):
            sanitized_seqs += 1
        
        # Track duplicates
        if any("Duplicate header" in error for error in result["errors"]):
            duplicate_headers += 1
        
        # Get sequence for statistics
        sequence = result.get("corrected_sequence") or result.get("original_sequence", "")
        
        if sequence:
            lengths.append(len(sequence))
            
            # Calculate GC content directly to avoid circular import
            seq_upper = sequence.upper()
            gc_count = seq_upper.count('G') + seq_upper.count('C')
            at_count = seq_upper.count('A') + seq_upper.count('T')
            valid_bases = gc_count + at_count
            
            if valid_bases > 0:
                gc_content = (gc_count / valid_bases) * 100
            else:
                gc_content = 0.0
                
            gc_contents.append(gc_content)
            
            # Calculate sequence stats directly
            stats = {
                "length": len(seq_upper),
                "gc_content": gc_content,
                "a_count": seq_upper.count('A'),
                "t_count": seq_upper.count('T'),
                "g_count": seq_upper.count('G'),
                "c_count": seq_upper.count('C'),
                "n_count": seq_upper.count('N'),
                "valid_chars": seq_upper.count('A') + seq_upper.count('T') + 
                              seq_upper.count('G') + seq_upper.count('C')
            }
            
            stats["sequence_index"] = i
            stats["header"] = result["header"]
            stats["is_valid"] = result["is_valid"]
            sequence_stats.append(stats)
        
        # Track errors
        if not result["is_valid"]:
            invalid_sequences.append({
                "index": i,
                "header": result["header"],
                "errors": result["errors"],
                "warnings": result["warnings"],
                "length": result.get("original_length", 0)
            })
            
            error_details.extend([{
                "sequence_index": i,
                "header": result["header"],
                "error": error,
                "error_type": _classify_error(error)
            } for error in result["errors"]])
    
    # Calculate length statistics
    length_stats = _calculate_length_stats(lengths) if lengths else {}
    gc_stats = _calculate_gc_stats(gc_contents) if gc_contents else {}
    
    # Top 10 longest sequences
    top_10_longest = _get_top_10_longest(sequence_stats)
    
    # Error analysis
    error_analysis = _analyze_errors(error_details)
    
    # Quality distribution
    quality_distribution = _calculate_quality_distribution(validation_results)
    
    # Generate final report
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_sequences": total_seqs,
            "tool_version": "1.0.0"
        },
        "summary": {
            "total_sequences": total_seqs,
            "valid_sequences": valid_seqs,
            "invalid_sequences": invalid_seqs,
            "sanitized_sequences": sanitized_seqs,
            "duplicate_headers": duplicate_headers,
            "validity_percentage": (valid_seqs / total_seqs) * 100 if total_seqs > 0 else 0,
            "sanitization_rate": (sanitized_seqs / total_seqs) * 100 if total_seqs > 0 else 0
        },
        "sequence_lengths": length_stats,
        "gc_content": gc_stats,
        "top_10_longest": top_10_longest,
        "quality_distribution": quality_distribution,
        "error_analysis": error_analysis,
        "invalid_sequences_detail": invalid_sequences,
        "sequence_statistics": sequence_stats
    }
    
    return report


def save_report(report: Dict, format: str, output_path: str = None) -> str:
    """Save report to file in specified format.
    
    Args:
        report (Dict): Report dictionary
        format (str): Output format ("csv" or "json")
        output_path (str, optional): Custom output path
        
    Returns:
        str: Path to the saved file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"genome_cleaner_report_{timestamp}.{format}"
    else:
        filename = output_path
    
    try:
        if format.lower() == "json":
            _save_json_report(report, filename)
        elif format.lower() == "csv":
            _save_csv_report(report, filename)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'csv'")
        
        return str(Path(filename).resolve())
        
    except Exception as e:
        raise IOError(f"Error saving report: {str(e)}")


def _empty_report() -> Dict:
    """Generate an empty report structure."""
    return {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_sequences": 0,
            "tool_version": "1.0.0"
        },
        "summary": {
            "total_sequences": 0,
            "valid_sequences": 0,
            "invalid_sequences": 0,
            "sanitized_sequences": 0,
            "duplicate_headers": 0,
            "validity_percentage": 0.0,
            "sanitization_rate": 0.0
        },
        "sequence_lengths": {},
        "gc_content": {},
        "top_10_longest": [],
        "quality_distribution": {},
        "error_analysis": {},
        "invalid_sequences_detail": [],
        "sequence_statistics": []
    }


def _calculate_length_stats(lengths: List[int]) -> Dict:
    """Calculate statistics for sequence lengths."""
    if not lengths:
        return {}
    
    return {
        "min": min(lengths),
        "max": max(lengths),
        "mean": sum(lengths) / len(lengths),
        "median": sorted(lengths)[len(lengths) // 2],
        "total": sum(lengths),
        "count": len(lengths),
        "quartiles": _calculate_quartiles(lengths)
    }


def _calculate_gc_stats(gc_contents: List[float]) -> Dict:
    """Calculate statistics for GC content."""
    if not gc_contents:
        return {}
    
    return {
        "min": min(gc_contents),
        "max": max(gc_contents),
        "mean": sum(gc_contents) / len(gc_contents),
        "median": sorted(gc_contents)[len(gc_contents) // 2],
        "count": len(gc_contents)
    }


def _calculate_quartiles(values: List[int]) -> Dict:
    """Calculate quartile statistics."""
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    return {
        "q1": sorted_values[n // 4] if n > 0 else 0,
        "q2": sorted_values[n // 2] if n > 0 else 0,  # median
        "q3": sorted_values[3 * n // 4] if n > 0 else 0
    }


def _get_top_10_longest(sequence_stats: List[Dict]) -> List[Dict]:
    """Get top 10 longest sequences."""
    # Sort by length descending
    sorted_stats = sorted(sequence_stats, key=lambda x: x.get("length", 0), reverse=True)
    
    top_10 = []
    for i, stats in enumerate(sorted_stats[:10]):
        top_10.append({
            "rank": i + 1,
            "header": stats["header"],
            "length": stats["length"],
            "gc_content": stats["gc_content"],
            "sequence_index": stats["sequence_index"]
        })
    
    return top_10


def _classify_error(error: str) -> str:
    """Classify error type based on error message."""
    if "Invalid characters" in error:
        return "Invalid characters"
    elif "too short" in error:
        return "Too short"
    elif "Duplicate header" in error:
        return "Duplicate header"
    elif "Empty sequence" in error:
        return "Empty sequence"
    else:
        return "Other"


def _analyze_errors(error_details: List[Dict]) -> Dict:
    """Analyze error patterns and frequencies."""
    if not error_details:
        return {
            "total_errors": 0,
            "error_types": {},
            "most_common_error": None
        }
    
    error_types = {}
    for error_detail in error_details:
        error_type = error_detail["error_type"]
        error_types[error_type] = error_types.get(error_type, 0) + 1
    
    most_common = max(error_types.items(), key=lambda x: x[1]) if error_types else None
    
    return {
        "total_errors": len(error_details),
        "error_types": error_types,
        "most_common_error": most_common[0] if most_common else None,
        "most_common_count": most_common[1] if most_common else 0
    }


def _calculate_quality_distribution(validation_results: List[Dict]) -> Dict:
    """Calculate distribution of sequence quality levels."""
    if not validation_results:
        return {}
    
    quality_levels = {
        "high_quality": 0,  # valid, long, no warnings
        "medium_quality": 0,  # valid with warnings
        "low_quality": 0,  # invalid but can be sanitized
        "unusable": 0  # invalid and cannot be fixed
    }
    
    for result in validation_results:
        has_errors = len(result["errors"]) > 0
        has_warnings = len(result["warnings"]) > 0
        
        if not has_errors:
            if not has_warnings:
                quality_levels["high_quality"] += 1
            else:
                quality_levels["medium_quality"] += 1
        else:
            # Check if errors can be fixed by sanitization
            can_be_sanitized = any("Invalid characters" in error for error in result["errors"])
            if can_be_sanitized:
                quality_levels["low_quality"] += 1
            else:
                quality_levels["unusable"] += 1
    
    return quality_levels


def _save_json_report(report: Dict, filename: str) -> None:
    """Save report as JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def _save_csv_report(report: Dict, filename: str) -> None:
    """Save report as CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(["Genome Cleaner Report"])
        writer.writerow([f"Generated: {report['metadata']['generated_at']}"])
        writer.writerow([])
        
        # Summary section
        writer.writerow(["SUMMARY"])
        summary = report['summary']
        for key, value in summary.items():
            writer.writerow([key.replace('_', ' ').title(), value])
        writer.writerow([])
        
        # Sequence length statistics
        writer.writerow(["SEQUENCE LENGTH STATISTICS"])
        length_stats = report.get('sequence_lengths', {})
        for key, value in length_stats.items():
            if isinstance(value, dict):
                writer.writerow([f"{key.title()}:"])
                for subkey, subvalue in value.items():
                    writer.writerow([f"  {subkey}", subvalue])
            else:
                writer.writerow([key.title(), value])
        writer.writerow([])
        
        # GC content statistics
        writer.writerow(["GC CONTENT STATISTICS"])
        gc_stats = report.get('gc_content', {})
        for key, value in gc_stats.items():
            writer.writerow([key.title(), value])
        writer.writerow([])
        
        # Top 10 longest
        writer.writerow(["TOP 10 LONGEST SEQUENCES"])
        writer.writerow(["Rank", "Header", "Length", "GC Content"])
        for seq in report.get('top_10_longest', []):
            writer.writerow([seq['rank'], seq['header'], seq['length'], f"{seq['gc_content']:.2f}%"])
        writer.writerow([])
        
        # Error analysis
        writer.writerow(["ERROR ANALYSIS"])
        error_analysis = report.get('error_analysis', {})
        writer.writerow(["Total Errors", error_analysis.get('total_errors', 0)])
        writer.writerow(["Most Common Error", error_analysis.get('most_common_error', 'None')])
        writer.writerow(["Most Common Count", error_analysis.get('most_common_count', 0)])
