#!/usr/bin/env python3
"""
Demo script to show Genome Cleaner functionality

Author: noomesk
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.parser import load_sequences
from src.validator import validate_sequences, get_validation_summary
from src.stats import generate_report

def demo_basic_functionality():
    """Demonstrate basic functionality of Genome Cleaner."""
    
    print("🧬 Genome Cleaner - Demo Script")
    print("=" * 50)
    
    # Test 1: Load and process clean sequences
    print("\n1. Testing with clean FASTA file:")
    try:
        sequences = load_sequences('examples/sample_sequences.fasta')
        print(f"   ✅ Loaded {len(sequences)} sequences successfully")
        
        results = validate_sequences(sequences, min_length=20, sanitize=True)
        summary = get_validation_summary(results)
        
        print(f"   📊 Valid sequences: {summary['valid_sequences']}/{summary['total_sequences']}")
        print(f"   📈 Validity rate: {summary['validity_percentage']:.1f}%")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Load and process sequences with errors
    print("\n2. Testing with sequences containing errors:")
    try:
        sequences = load_sequences('examples/sample_with_errors.fasta')
        print(f"   ✅ Loaded {len(sequences)} sequences successfully")
        
        results = validate_sequences(sequences, min_length=20, sanitize=True)
        summary = get_validation_summary(results)
        
        print(f"   📊 Valid sequences: {summary['valid_sequences']}/{summary['total_sequences']}")
        print(f"   📈 Validity rate: {summary['validity_percentage']:.1f}%")
        print(f"   🔧 Sanitized sequences: {summary['sanitized_sequences']}")
        
        if summary['error_types']:
            print("   🚨 Error breakdown:")
            for error_type, count in summary['error_types'].items():
                print(f"      - {error_type}: {count}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Generate comprehensive report
    print("\n3. Generating comprehensive report:")
    try:
        report = generate_report(results)
        
        print(f"   ✅ Report generated for {report['metadata']['total_sequences']} sequences")
        print(f"   📋 Report sections: {len(report.keys())}")
        
        # Show some key statistics
        if report['sequence_lengths']:
            print(f"   📏 Length stats - Min: {report['sequence_lengths']['min']} bp")
            print(f"   📏 Length stats - Max: {report['sequence_lengths']['max']} bp")
            print(f"   📏 Length stats - Mean: {report['sequence_lengths']['mean']:.1f} bp")
        
        if report['gc_content']:
            print(f"   🧬 GC content - Min: {report['gc_content']['min']:.1f}%")
            print(f"   🧬 GC content - Max: {report['gc_content']['max']:.1f}%")
            print(f"   🧬 GC content - Mean: {report['gc_content']['mean']:.1f}%")
        
        if report['top_10_longest']:
            print(f"   🏆 Longest sequence: {report['top_10_longest'][0]['length']} bp")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Save reports
    print("\n4. Testing report export:")
    try:
        from src.stats import save_report
        
        json_path = save_report(report, 'json', 'demo_report.json')
        print(f"   ✅ JSON report saved to: {json_path}")
        
        csv_path = save_report(report, 'csv', 'demo_report.csv')
        print(f"   ✅ CSV report saved to: {csv_path}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Demo CLI functionality (show command structure)
    print("\n5. CLI Commands available:")
    print("   💻 streamlit run app.py                    # Web interface")
    print("   💻 python -m src.cli --help               # CLI help")
    print("   💻 python -m src.cli --input file.fasta  # Basic validation")
    print("   💻 python -m src.cli --input file.fasta --sanitize --report")
    
    print("\n🎉 Demo completed successfully!")
    print("🌐 To try the web interface: streamlit run app.py")

if __name__ == "__main__":
    demo_basic_functionality()
