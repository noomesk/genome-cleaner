"""
Unit tests for parser module.

Author: noomesk
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.parser import load_sequences, _parse_fasta, _parse_fastq, detect_file_format, ParsingError


class TestParser:
    """Test cases for the parser module."""
    
    def test_parse_fasta_simple(self):
        """Test parsing simple FASTA format."""
        fasta_content = ">seq1\nACGTACGT\n>seq2\nTTTTAAAA\n"
        
        result = _parse_fasta(fasta_content)
        
        assert len(result) == 2
        assert result[0] == ("seq1", "ACGTACGT")
        assert result[1] == ("seq2", "TTTTAAAA")
    
    def test_parse_fasta_multiline(self):
        """Test parsing FASTA with multiline sequences."""
        fasta_content = ">seq1\nACGT\nACGT\nACGT\n>seq2\nTTTTAAAA\n"
        
        result = _parse_fasta(fasta_content)
        
        assert len(result) == 2
        assert result[0] == ("seq1", "ACGTACGTACGT")
        assert result[1] == ("seq2", "TTTTAAAA")
    
    def test_parse_fasta_with_empty_lines(self):
        """Test parsing FASTA with empty lines."""
        fasta_content = ">seq1\nACGT\n\n>seq2\nTTTT\n\n"
        
        result = _parse_fasta(fasta_content)
        
        assert len(result) == 2
        assert result[0] == ("seq1", "ACGT")
        assert result[1] == ("seq2", "TTTT")
    
    def test_parse_fasta_with_headers_only(self):
        """Test parsing FASTA with only headers (no sequences)."""
        fasta_content = ">seq1\n>seq2\n"
        
        result = _parse_fasta(fasta_content)
        
        assert len(result) == 0  # No sequences should be added
    
    def test_parse_fastq_simple(self):
        """Test parsing simple FASTQ format."""
        fastq_content = "@seq1\nACGTACGT\n+\nIIIIIIII\n@seq2\nTTTTAAAA\n+\nTTTTTTTT\n"
        
        result = _parse_fastq(fastq_content)
        
        assert len(result) == 2
        assert result[0] == ("seq1", "ACGTACGT")
        assert result[1] == ("seq2", "TTTTAAAA")
    
    def test_parse_fastq_incomplete_record(self):
        """Test parsing FASTQ with incomplete records."""
        fastq_content = "@seq1\nACGTACGT\n+\nIIIIIII\n@seq2\n"  # Incomplete second record
        
        result = _parse_fastq(fastq_content)
        
        assert len(result) == 1
        assert result[0] == ("seq1", "ACGTACGT")
    
    def test_load_sequences_fasta_file(self):
        """Test loading sequences from FASTA file."""
        fasta_content = ">seq1\nACGTACGT\n>seq2\nTTTTAAAA\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(fasta_content)
            temp_path = f.name
        
        try:
            result = load_sequences(temp_path)
            
            assert len(result) == 2
            assert result[0] == ("seq1", "ACGTACGT")
            assert result[1] == ("seq2", "TTTTAAAA")
        finally:
            os.unlink(temp_path)
    
    def test_load_sequences_fastq_file(self):
        """Test loading sequences from FASTQ file."""
        fastq_content = "@seq1\nACGTACGT\n+\nIIIIIIII\n@seq2\nTTTTAAAA\n+\nTTTTTTTT\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fastq', delete=False) as f:
            f.write(fastq_content)
            temp_path = f.name
        
        try:
            result = load_sequences(temp_path)
            
            assert len(result) == 2
            assert result[0] == ("seq1", "ACGTACGT")
            assert result[1] == ("seq2", "TTTTAAAA")
        finally:
            os.unlink(temp_path)
    
    def test_load_sequences_empty_file(self):
        """Test loading from empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            with pytest.raises(ParsingError, match="File is empty"):
                load_sequences(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_sequences_nonexistent_file(self):
        """Test loading from non-existent file."""
        with pytest.raises(ParsingError):
            load_sequences("nonexistent_file.fasta")
    
    def test_load_sequences_invalid_format(self):
        """Test loading from file with invalid format."""
        invalid_content = "This is not FASTA or FASTQ format"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(invalid_content)
            temp_path = f.name
        
        try:
            with pytest.raises(ParsingError, match="No valid sequences found"):
                load_sequences(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_detect_file_format_fasta(self):
        """Test detecting FASTA format."""
        fasta_content = ">seq1\nACGTACGT\n>seq2\nTTTTAAAA\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(fasta_content)
            temp_path = f.name
        
        try:
            result = detect_file_format(temp_path)
            assert result == "fasta"
        finally:
            os.unlink(temp_path)
    
    def test_detect_file_format_fastq(self):
        """Test detecting FASTQ format."""
        fastq_content = "@seq1\nACGTACGT\n+\nIIIIIIII\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fastq', delete=False) as f:
            f.write(fastq_content)
            temp_path = f.name
        
        try:
            result = detect_file_format(temp_path)
            assert result == "fastq"
        finally:
            os.unlink(temp_path)
    
    def test_detect_file_format_unknown(self):
        """Test detecting unknown format."""
        unknown_content = "random text without headers"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(unknown_content)
            temp_path = f.name
        
        try:
            result = detect_file_format(temp_path)
            assert result == "unknown"
        finally:
            os.unlink(temp_path)
    
    def test_load_sequences_with_special_characters_in_headers(self):
        """Test parsing headers with special characters."""
        fasta_content = ">seq_1|description|extra\nACGTACGT\n>seq-2.description\nTTTTAAAA\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(fasta_content)
            temp_path = f.name
        
        try:
            result = load_sequences(temp_path)
            
            assert len(result) == 2
            assert result[0][0] == "seq_1|description|extra"
            assert result[1][0] == "seq-2.description"
        finally:
            os.unlink(temp_path)
    
    def test_load_sequences_whitespace_handling(self):
        """Test handling of whitespace in sequences."""
        fasta_content = ">seq1\nA C G T\n\tA C G T\n>seq2\nT T T T\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(fasta_content)
            temp_path = f.name
        
        try:
            result = load_sequences(temp_path)
            
            assert len(result) == 2
            # Parser preserves whitespace as-is when joining lines
            assert result[0][1] == "A C G TA C G T"  # Whitespace preserved
            assert result[1][1] == "T T T T"
        finally:
            os.unlink(temp_path)
