"""
Unit tests for validator module.

Author: noomesk
"""

import pytest

from src.validator import (
    validate_sequence, 
    validate_sequences, 
    calculate_gc_content, 
    calculate_sequence_stats,
    filter_valid_sequences,
    get_validation_summary
)


class TestValidator:
    """Test cases for the validator module."""
    
    def test_validate_sequence_valid(self):
        """Test validation of valid sequence."""
        result = validate_sequence("seq1", "ACGTACGT", min_length=20, sanitize=False)
        
        assert result["is_valid"] is False  # Too short for min_length=20
        assert len(result["errors"]) == 1
        assert "too short" in result["errors"][0]
        assert result["corrected_sequence"] is None
    
    def test_validate_sequence_valid_short(self):
        """Test validation of valid short sequence."""
        result = validate_sequence("seq1", "ACGTACGT", min_length=5, sanitize=False)
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert result["corrected_sequence"] is None
    
    def test_validate_sequence_invalid_characters(self):
        """Test validation with invalid characters."""
        result = validate_sequence("seq1", "ACGTAXGT", min_length=5, sanitize=False)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) == 1
        assert "Invalid characters" in result["errors"][0]
        assert "X" in result["errors"][0]
    
    def test_validate_sequence_with_sanitization(self):
        """Test sequence sanitization."""
        result = validate_sequence("seq1", "ACGTAXGT", min_length=5, sanitize=True)
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert result["corrected_sequence"] == "ACGTANGT"  # X replaced with N
        assert result["corrected_length"] == 8
    
    def test_validate_sequence_empty(self):
        """Test validation of empty sequence."""
        result = validate_sequence("seq1", "", min_length=5, sanitize=False)
        
        assert result["is_valid"] is False
        assert "Empty sequence" in result["errors"]
    
    def test_validate_sequence_only_n(self):
        """Test sequence with only N characters."""
        result = validate_sequence("seq1", "NNNN", min_length=2, sanitize=False)
        
        assert result["is_valid"] is True  # Valid format, just low quality
        assert "only N characters" in result["warnings"]
    
    def test_validate_sequence_low_complexity(self):
        """Test low complexity sequence detection."""
        result = validate_sequence("seq1", "AAAAAAATTTTTTT", min_length=5, sanitize=False)
        
        assert result["is_valid"] is True
        assert "Low complexity" in result["warnings"]
    
    def test_calculate_gc_content(self):
        """Test GC content calculation."""
        assert calculate_gc_content("GCGCGC") == 100.0
        assert calculate_gc_content("ATATAT") == 0.0
        assert calculate_gc_content("ATGC") == 50.0
        assert calculate_gc_content("") == 0.0
        assert calculate_gc_content("NNNN") == 0.0  # N's don't count
    
    def test_calculate_sequence_stats(self):
        """Test sequence statistics calculation."""
        stats = calculate_sequence_stats("AATCGG")
        
        assert stats["length"] == 6
        assert stats["a_count"] == 2
        assert stats["t_count"] == 1
        assert stats["g_count"] == 2
        assert stats["c_count"] == 1
        assert stats["n_count"] == 0
        assert stats["valid_chars"] == 6
        assert stats["gc_content"] == 50.0
    
    def test_validate_sequences_duplicate_headers(self):
        """Test validation with duplicate headers."""
        sequences = [
            ("seq1", "ACGT"),
            ("seq2", "TTTT"),
            ("seq1", "GGGG")  # Duplicate header
        ]
        
        results = validate_sequences(sequences, min_length=2, sanitize=False)
        
        assert len(results) == 3
        
        # Check duplicate header detection
        duplicate_results = [r for r in results if "Duplicate header" in r["errors"]]
        assert len(duplicate_results) == 2  # Both occurrences of "seq1"
    
    def test_filter_valid_sequences(self):
        """Test filtering valid sequences."""
        results = [
            {"is_valid": True, "header": "seq1"},
            {"is_valid": False, "header": "seq2"},
            {"is_valid": True, "header": "seq3"},
            {"is_valid": False, "header": "seq4"}
        ]
        
        valid_only = filter_valid_sequences(results)
        
        assert len(valid_only) == 2
        assert valid_only[0]["header"] == "seq1"
        assert valid_only[1]["header"] == "seq3"
    
    def test_get_validation_summary_empty(self):
        """Test summary with no results."""
        summary = get_validation_summary([])
        
        assert summary["total_sequences"] == 0
        assert summary["valid_sequences"] == 0
        assert summary["invalid_sequences"] == 0
        assert summary["sanitized_sequences"] == 0
        assert summary["duplicate_headers"] == 0
    
    def test_get_validation_summary_mixed(self):
        """Test summary with mixed results."""
        results = [
            {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "sequence_index": 0
            },
            {
                "is_valid": False,
                "errors": ["Invalid characters"],
                "warnings": [],
                "sequence_index": 1
            },
            {
                "is_valid": False,
                "errors": ["Duplicate header"],
                "warnings": [],
                "sequence_index": 2
            }
        ]
        
        summary = get_validation_summary(results)
        
        assert summary["total_sequences"] == 3
        assert summary["valid_sequences"] == 1
        assert summary["invalid_sequences"] == 2
        assert summary["total_errors"] == 2
        assert summary["error_types"]["Invalid characters"] == 1
        assert summary["error_types"]["Duplicate headers"] == 1
    
    def test_validate_sequence_with_lowercase(self):
        """Test validation with lowercase characters."""
        result = validate_sequence("seq1", "acgtacgt", min_length=5, sanitize=False)
        
        # Should be valid - lowercase characters are allowed
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_sequence_sanitization_mixed_case(self):
        """Test sanitization with mixed case and invalid chars."""
        result = validate_sequence("seq1", "AcGtXyZ", min_length=5, sanitize=True)
        
        assert result["is_valid"] is True
        assert result["corrected_sequence"] == "ACGTNNN"  # Invalid chars replaced with N
    
    def test_validate_sequence_very_short(self):
        """Test validation with very short sequence."""
        result = validate_sequence("seq1", "A", min_length=20, sanitize=False)
        
        assert result["is_valid"] is False
        assert "too short" in result["errors"][0]
        assert result["errors"][0] == "Sequence too short: 1 bp (minimum: 20 bp)"
    
    def test_validate_sequence_whitespace(self):
        """Test validation with whitespace."""
        result = validate_sequence("seq1", "ACGT ACGT", min_length=5, sanitize=False)
        
        assert result["is_valid"] is False
        assert "Invalid characters" in result["errors"][0]
        # Spaces are invalid characters
    
    def test_validate_sequence_newlines_tabs(self):
        """Test validation with newlines and tabs."""
        result = validate_sequence("seq1", "ACGT\nACGT\tACGT", min_length=5, sanitize=False)
        
        assert result["is_valid"] is False
        assert "Invalid characters" in result["errors"][0]
    
    def test_calculate_gc_content_with_n(self):
        """Test GC content calculation with N characters."""
        # GC content should only consider A, C, G, T - N's are ignored
        assert calculate_gc_content("GCGCNN") == 100.0  # 4/4 valid bases are GC
        assert calculate_gc_content("ATATNN") == 0.0    # 4/4 valid bases are AT
    
    def test_calculate_sequence_stats_empty(self):
        """Test stats calculation for empty sequence."""
        stats = calculate_sequence_stats("")
        
        assert stats["length"] == 0
        assert stats["gc_content"] == 0.0
        assert stats["a_count"] == 0
        assert stats["t_count"] == 0
        assert stats["g_count"] == 0
        assert stats["c_count"] == 0
        assert stats["n_count"] == 0
        assert stats["valid_chars"] == 0
    
    def test_validate_sequence_no_nucleotides(self):
        """Test sequence with no valid nucleotides."""
        result = validate_sequence("seq1", "XXXXX", min_length=2, sanitize=False)
        
        assert result["is_valid"] is False
        assert "Invalid characters" in result["errors"][0]
        assert len(result["warnings"]) == 0  # Only N sequences get low quality warning
    
    def test_validate_sequence_sanitization_comprehensive(self):
        """Test comprehensive sanitization scenario."""
        result = validate_sequence(
            "seq1 with|spaces", 
            "acg T xyz\nN\tG", 
            min_length=5, 
            sanitize=True
        )
        
        assert result["is_valid"] is True
        assert result["corrected_sequence"] == "ACGTNNNG"  # All cleaned up
        assert result["header"] == "seq1 with|spaces"
    
    def test_validation_summary_sanitization_stats(self):
        """Test sanitization statistics in summary."""
        results = [
            {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "corrected_sequence": "ACGT",
                "original_sequence": "ACXT",  # Was sanitized
                "sequence_index": 0
            },
            {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "corrected_sequence": "TTTT",
                "original_sequence": "TTTT",  # No change needed
                "sequence_index": 1
            }
        ]
        
        summary = get_validation_summary(results)
        
        assert summary["sanitized_sequences"] == 1
        assert summary["sanitization_rate"] == 50.0
