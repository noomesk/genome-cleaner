# ENGLISH VERSION:
# INSTALLATION AND USAGE GUIDE

## Quick Start Guide for Genome Cleaner

### Installation Steps

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test Installation**:
   ```bash
   python demo.py
   ```

### Running the Web Interface

1. **Start Streamlit App**:
   ```bash
   streamlit run app.py
   ```

2. **Open Browser**: Navigate to `http://localhost:8501`

3. **Upload Files**: Drag and drop FASTA/FASTQ files in the sidebar

4. **Configure Options**: Set sanitization mode and minimum length threshold

5. **Process**: Click "Process File" to analyze sequences

6. **Explore Results**: Check the tabs for summary, validation table, visualizations, and reports

### Command Line Usage

1. **Basic Validation**:
   ```bash
   python -m src.cli --input examples/sample_sequences.fasta
   ```

2. **With Sanitization**:
   ```bash
   python -m src.cli --input examples/sample_sequences.fasta --sanitize --output cleaned.fasta
   ```

3. **Generate Report**:
   ```bash
   python -m src.cli --input examples/sample_sequences.fasta --report --format json
   ```

4. **Comprehensive Processing**:
   ```bash
   python -m src.cli --input examples/sample_with_errors.fasta --sanitize --min-length 20 --report --format csv
   ```

### File Format Support

**FASTA format**:
```
>header_description
ACGTACGTACGTACGT
>another_sequence
TTTTTTTTTTTTTTTT
```

**FASTQ format**:
```
@sequence_id
ACGTACGTACGTACGT
+
IIIIIIIIIIIIIIII
@another_sequence
TTTTTTTTTTTTTTTT
+
JJJJJJJJJJJJJJJJ
```

### Example Files

The project includes example files in the `examples/` directory:
- `sample_sequences.fasta`: Clean sequences for testing
- `sample_with_errors.fasta`: Sequences with common issues
- `sample_sequences.fastq`: FASTQ format example

### Validation Features

- **Character Validation**: Detects invalid DNA characters (A,C,G,T,N only)
- **Header Duplicates**: Finds and reports duplicate sequence headers
- **Length Filtering**: Identifies sequences below minimum length threshold
- **Sanitization**: Automatically cleans invalid characters (replaces with 'N')
- **Quality Metrics**: Calculates GC content and sequence statistics
- **Error Classification**: Categorizes different types of validation errors

### Web Interface Features

- **Real-time Metrics**: Live statistics during processing
- **Interactive Tables**: Sortable and filterable sequence results
- **Visualizations**: Histograms and scatter plots with Plotly
- **Report Generation**: Export comprehensive statistics
- **Data Export**: Download cleaned sequences and detailed reports
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Troubleshooting

**Common Issues**:

1. **"Module not found" errors**:
   - Ensure you're in the project root directory
   - Check that all dependencies are installed

2. **File upload fails**:
   - Verify file is FASTA (.fasta, .fa) or FASTQ (.fastq, .fq) format
   - Check file isn't corrupted or empty

3. **No sequences detected**:
   - Ensure file has proper FASTA/FASTQ formatting
   - Check that headers start with '>' (FASTA) or '@' (FASTQ)

4. **Validation shows unexpected errors**:
   - Verify sequences contain only A, C, G, T, N characters
   - Check minimum length threshold isn't too high

**Getting Help**:
- Run the demo script: `python demo.py`
- Check example files in `examples/` directory
- Review validation results in the web interface

### Performance Notes

- **Small files** (< 1000 sequences): Process instantly
- **Medium files** (1000-10000 sequences): 1-5 seconds
- **Large files** (> 10000 sequences): May take longer, consider using CLI for batch processing

### Advanced Usage

**Custom Thresholds**:
```bash
python -m src.cli --input file.fasta --min-length 50
```

**Batch Processing**:
```bash
# Process multiple files
for file in *.fasta; do
    python -m src.cli --input "$file" --sanitize --output "clean_$file"
done
```

**Pipeline Integration**:
```bash
# Use in bioinformatic pipelines
python -m src/cli --input raw_data.fasta --sanitize --min-length 100 --output clean_data.fasta --report
```

---

**Author**: noomesk  
**Version**: 1.0.0  
**License**: MIT
