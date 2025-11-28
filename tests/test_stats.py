"""
Unit tests for stats module.

Author: noomesk
"""

import pytest
import tempfile
import json
import os
from pathlib import Path

from src.stats import (
    generate_report, 
    save_report, 
    _calculate_length_stats,
    _calculate_gc_stats,
    _get_top_10_longest,
    _analyze_errors,
    _calculate_quartiles,
    _classify_error
)


class TestStats:
    """Test cases for the stats module."""
    
    def test_generate_report_empty(self):
        """Test generating report with empty results."""
        report = generate_report([])
        
        assert report["metadata"]["total_sequences"] == 0
        assert report["summary"]["total_sequences"] == 0
        assert report["summary"]["valid_sequences"] == 0
        assert report["sequence_lengths"] == {}
        assert report["gc_content"] == {}
        assert report["top_10_longest"] == []
    
    def test_generate_report_single_sequence(self):
        """Test generating report with single valid sequence."""
        validation_results = [
            {
                "sequence_index": 0,
                "header": "seq1",
                "original_sequence": "ACGTACGT",
                "corrected_sequence": "ACGTACGT",
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
        ]
        
        report = generate_report(validation_results)
        
        assert report["summary"]["total_sequences"] == 1
        assert report["summary"]["valid_sequences"] == 1
        assert report["summary"]["validity_percentage"] == 100.0
        assert report["sequence_lengths"]["min"] == 8
        assert report["sequence_lengths"]["max"] == 8
        assert report["sequence_lengths"]["mean"] == 8.0
        assert report["gc_content"]["min"] == 50.0
        assert report["gc_content"]["max"] == 50.0
        assert report["gc_content"]["mean"] == 50.0
    
    def test_generate_report_multiple_sequences(self):
        """Test generating report with multiple sequences."""
        validation_results = [
            {
                "sequence_index": 0,
                "header": "seq1",
                "original_sequence": "AAAAAA",  # Low GC
                "is_valid": True,
                "errors": [],
                "warnings": []
            },
            {
                "sequence_index": 1,
                "header": "seq2",
                "original_sequence": "GGGGGG",  # High GC
                "is_valid": True,
                "errors": [],
                "warnings": []
            },
            {
                "sequence_index": 2,
                "header": "seq3",
                "original_sequence": "ACGT",  # Too short
                "is_valid": False,
                "errors": ["Sequence too short"],
                "warnings": []
            }
        ]
        
        report = generate_report(validation_results)
        
        assert report["summary"]["total_sequences"] == 3
        assert report["summary"]["valid_sequences"] == 2
        assert report["summary"]["invalid_sequences"] == 1
        assert report["summary"]["validity_percentage"] == 66.67  # 2/3 * 100
        
        # Check length statistics
        assert report["sequence_lengths"]["min"] == 4
        assert report["sequence_lengths"]["max"] == 6
        assert report["sequence_lengths"]["mean"] == 5.33  # (6+6+4)/3
        
        # Check GC statistics (only for valid sequences: 0% and 100%)
        assert report["gc_content"]["min"] == 0.0
        assert report["gc_content"]["max"] == 100.0
        assert report["gc_content"]["mean"] == 50.0  # (0+100)/2
    
    def test_save_report_json(self):
        """Test saving report as JSON."""
        validation_results = [
            {
                "sequence_index": 0,
                "header": "seq1",
                "original_sequence": "ACGT",
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
        ]
        
        report = generate_report(validation_results)
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            saved_path = save_report(report, 'json', tmp_path)
            
            # Check file was created and contains valid JSON
            assert os.path.exists(saved_path)
            
            with open(saved_path, 'r') as f:
                loaded_report = json.load(f)
            
            assert loaded_report["summary"]["total_sequences"] == 1
            assert loaded_report["metadata"]["tool_version"] == "1.0.0"
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_save_report_csv(self):
        """Test saving report as CSV."""
        validation_results = [
            {
                "sequence_index": 0,
                "header": "seq1",
                "original_sequence": "ACGT",
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
        ]
        
        report = generate_report(validation_results)
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            saved_path = save_report(report, 'csv', tmp_path)
            
            # Check file was created and contains CSV data
            assert os.path.exists(saved_path)
            
            with open(saved_path, 'r') as f:
                content = f.read()
            
            # Basic CSV content check
            assert "Summary" in content
            assert "seq1" in content
            assert "Total Sequences" in content
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_save_report_invalid_format(self):
        """Test saving report with invalid format."""
        validation_results = [
            {
                "sequence_index": 0,
                "header": "seq1",
                "original_sequence": "ACGT",
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
        ]
        
        report = generate_report(validation_results)
        
        with pytest.raises(ValueError, match="Unsupported format"):
            save_report(report, 'invalid_format')
    
    def test_calculate_length_stats(self):
        """Test length statistics calculation."""
        lengths = [10, 20, 30, 40, 50]
        
        stats = _calculate_length_stats(lengths)
        
        assert stats["min"] == 10
        assert stats["max"] == 50
        assert stats["mean"] == 30.0
        assert stats["total"] == 150
        assert stats["count"] == 5
    
    def test_calculate_length_stats_empty(self):
        """Test length statistics with empty list."""
        stats = _calculate_length_stats([])
        
        assert stats == {}
    
    def test_calculate_gc_stats(self):
        """Test GC content statistics calculation."""
        gc_contents = [25.0, 50.0, 75.0, 100.0]
        
        stats = _calculate_gc_stats(gc_contents)
        
        assert stats["min"] == 25.0
        assert stats["max"] == 100.0
        assert stats["mean"] == 62.5
        assert stats["count"] == 4
    
    def test_calculate_gc_stats_empty(self):
        """Test GC statistics with empty list."""
        stats = _calculate_gc_stats([])
        
        assert stats == {}
    
    def test_get_top_10_longest(self):
        """Test getting top 10 longest sequences."""
        sequence_stats = [
            {
                "sequence_index": 0,
                "header": "short_seq",
                "length": 10,
                "gc_content": 50.0
            },
            {
                "sequence_index": 1,
                "header": "long_seq",
                "length": 100,
                "gc_content": 60.0
            },
            {
                "sequence_index": 2,
                "header": "medium_seq",
                "length": 50,
                "gc_content": 40.0
            }
        ]
        
        top_10 = _get_top_10_longest(sequence_stats)
        
        assert len(top_10) == 3
        assert top_10[0]["rank"] == 1
        assert top_10[0]["header"] == "long_seq"
        assert top_10[0]["length"] == 100
        assert top_10[1]["rank"] == 2
        assert top_10[1]["header"] == "medium_seq"
        assert top_10[2]["rank"] == 3
        assert top_10[2]["header"] == "short_seq"
    
    def test_classify_error(self):
        """Test error classification."""
        assert _classify_error("Invalid characters found: X") == "Invalid characters"
        assert _classify_error("Sequence too short: 5 bp") == "Too short"
        assert _classify_error("Duplicate header found") == "Duplicate header"
        assert _classify_error("Empty sequence") == "Empty sequence"
        assert _classify_error("Some other error") == "Other"
    
    def test_analyze_errors(self):
        """Test error analysis."""
        error_details = [
            {"error": "Invalid characters found", "error_type": "Invalid characters"},
            {"error": "Invalid characters found", "error_type": "Invalid characters"},
            {"error": "Sequence too short", "error_type": "Too short"},
            {"error": "Duplicate header", "error_type": "Duplicate header"}
        ]
        
        analysis = _analyze_errors(error_details)
        
        assert analysis["total_errors"] == 4
        assert analysis["error_types"]["Invalid characters"] == 2
        assert analysis["error_types"]["Too short"] == 1
        assert analysis["error_types"]["Duplicate header"] == 1
        assert analysis["most_common_error"] == "Invalid characters"
        assert analysis["most_common_count"] == 2
    
    def test_analyze_errors_empty(self):
        """Test error analysis with no errors."""
        analysis = _analyze_errors([])
        
        assert analysis["total_errors"] == 0
        assert analysis["error_types"] == {}
        assert analysis["most_common_error"] is None
        assert analysis["most_common_count"] == 0
    
    def test_calculate_quartiles(self):
        """Test quartile calculation."""
        values = [1, 2, 3, 4, 5, 6, 7, 8]  # 8 values
        
        quartiles = _calculate_quartiles(values)
        
        assert quartiles["q1"] == 3  # 8//4 = 2, index 2 = value 3
        assert quartiles["q2"] == 4  # median
        assert quartiles["q3"] == 6  # 3*8//4 = 6, index 6 = value 7
    
    def test_calculate_quartiles_empty(self):
        """Test quartile calculation with empty list."""
        quartiles = _calculate_quartiles([])
        
        assert quartiles["q1"] == 0
        assert quartiles["q2"] == 0
        assert quartiles["q3"] == 0
    
    def test_generate_report_sanitization_tracking(self):
        """Test report generation tracks sanitization."""
        validation_results = [
            {
                "sequence_index": 0,
                "header": "seq1",
                "original_sequence": "ACXT",
                "corrected_sequence": "ACGT",  # Was sanitized
                "is_valid": True,
                "errors": [],
                "warnings": []
            },
            {
                "sequence_index": 1,
                "header": "seq2",
                "original_sequence": "TTTT",
                "corrected_sequence": "TTTT",  # No change
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
        ]
        
        report = generate_report(validation_results)
        
        assert report["summary"]["sanitized_sequences"] == 1
        assert report["summary"]["sanitization_rate"] == 50.0
    
    def test_generate_report_error_analysis(self):
        """Test report includes detailed error analysis."""
        validation_results = [
            {
                "sequence_index": 0,
                "header": "seq1",
                "original_sequence": "ACXT",
                "is_valid": False,
                "errors": ["Invalid characters found: X"],
                "warnings": []
            },
            {
                "sequence_index": 1,
                "header": "seq2",
                "original_sequence": "A",  # Too short
                "is_valid": False,
                "errors": ["Sequence too short: 1 bp"],
                "warnings": []
            },
            {
                "sequence_index": 2,
                "header": "seq3",
                "original_sequence": "NNNN",
                "is_valid": True,
                "errors": [],
                "warnings": ["Sequence contains only N characters"]
            }
        ]
        
        report = generate_report(validation_results)
        
        assert report["error_analysis"]["total_errors"] == 2
        assert report["error_analysis"]["error_types"]["Invalid characters"] == 1
        assert report["error_analysis"]["error_types"]["Too short"] == 1
        assert report["invalid_sequences_detail"][0]["header"] == "seq1"
        assert report["invalid_sequences_detail"][1]["header"] == "seq2"
    
    def test_generate_report_duplicate_headers(self):
        """Test report tracks duplicate headers."""
        # Note: In actual usage, duplicates would be detected in validator
        # This test simulates what the validator would return
        validation_results = [
            {
                "sequence_index": 0,
                "header": "dup_seq",
                "original_sequence": "ACGT",
                "is_valid": False,
                "errors": ["Duplicate header found (2 occurrences)"],
                "warnings": []
            },
            {
                "sequence_index": 1,
                "header": "dup_seq",
                "original_sequence": "TTTT",
                "is_valid": False,
                "errors": ["Duplicate header found (2 occurrences)"],
                "warnings": []
            }
        ]
        
        report = generate_report(validation_results)
        
        assert report["summary"]["duplicate_headers"] == 2
    
    def test_save_report_file_creation_error(self):
        """Test error handling when file cannot be created."""
        validation_results = [
            {
                "sequence_index": 0,
                "header": "seq1",
                "original_sequence": "ACGT",
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
        ]
        
        report = generate_report(validation_results)
        
        # Try to save to a path that doesn't exist and can't be created
        with pytest.raises(IOError, match="Error saving report"):
            save_report(report, 'json', '/nonexistent/path/report.json')
    
    def test_generate_report_metadata(self):
        """Test report includes proper metadata."""
        validation_results = [
            {
                "sequence_index": 0,
                "header": "seq1",
                "original_sequence": "ACGT",
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
        ]
        
        report = generate_report(validation_results)
        
        assert "metadata" in report
        assert "generated_at" in report["metadata"]
        assert report["metadata"]["total_sequences"] == 1
        assert report["metadata"]["tool_version"] == "1.0.0"
        
        # Check timestamp is valid ISO format
        from datetime import datetime
        datetime.fromisoformat(report["metadata"]["generated_at"])
