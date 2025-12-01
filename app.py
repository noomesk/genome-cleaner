"""
Genome Cleaner - Streamlit Web Application

This is main Streamlit application for cleaning and validating FASTA/FASTQ sequences.
It provides an interactive web interface with visualizations and reporting capabilities.

Author: noomesk
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
import json
from pathlib import Path

# Import our custom modules
from src.parser import load_sequences, detect_file_format, ParsingError
from src.validator import validate_sequences, get_validation_summary, calculate_gc_content
from src.stats import generate_report, save_report


# Configure Streamlit page
st.set_page_config(
    page_title="Genome Cleaner",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main Streamlit application."""
    
    # --- ESTILO DARK (FALTA INTERACTIVIDAD Y ANIMACIONES)---
    st.markdown("""
    <style>
        /* --- PALETA Y TIPOGRAFÍA DE DARK THEME--- */
        :root {
            --bg-color: #010409; /* Fondo negro puro de GitHub/Render */
            --surface-color: #0d1117; /* Gris oscuro para tarjetas */
            --border-color: #21262d; /* Bordes más definidos */
            --text-primary: #c9d1d9; /* Texto principal gris claro */
            --text-secondary: #8b949e; /* Texto secundario más apagado */
            --accent-color: #238636; /* Verde característico de GitHub/Render */
            --accent-hover: #2ea043;
        }

        /* --- TIPOGRAFÍA INTER (JAJA INSP EN GITHUB/RENDER) --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, .stApp {
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-size: 16px;
            line-height: 1.5;
        }
        
        /* --- CONTENEDOR PRINCIPAL --- */
        .main .block-container {
            background-color: var(--surface-color);
            padding: 2rem 3rem;
            margin-top: 0;
            border: 1px solid var(--border-color);
            box-shadow: none;
        }

        /* --- SIDEBAR --- */
        .stSidebar {
            background-color: var(--surface-color);
            border-right: 1px solid var(--border-color);
        }
        .stSidebar .block-container {
            background-color: transparent;
            padding: 1rem 1.5rem;
        }

        /* --- TÍTULOS Y TEXTO --- */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1.25;
        }
        
        h1 { font-size: 2.5rem; font-weight: 700; }
        h2 { font-size: 2rem; }
        h3 { font-size: 1.5rem; }
        
        p, li, div[data-testid="stMarkdownContainer"] > p {
            color: var(--text-secondary);
            font-size: 1rem;
            line-height: 1.6;
        }
        
        strong, b {
            color: var(--text-primary);
            font-weight: 600;
        }

        /* --- MÉTRICAS --- */
        div[data-testid="metric-container"] {
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            padding: 1rem 1.5rem;
            border-radius: 6px;
        }
        label[data-testid="stMetricLabel"] {
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 0.9rem;
        }
        div[data-testid="stMetricValue"] {
            color: var(--text-primary);
            font-weight: 700;
        }

        /* --- TABS --- */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--surface-color);
            border-bottom: 1px solid var(--border-color);
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            padding: 12px 20px;
            font-weight: 500;
            color: var(--text-secondary);
        }
        .stTabs [aria-selected="true"] {
            color: var(--text-primary);
            background-color: var(--bg-color);
            border-bottom: 2px solid var(--accent-color);
        }

        /* --- BOTONES --- */
        .stButton > button {
            background-color: var(--accent-color);
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s ease-in-out;
        }
        .stButton > button:hover {
            background-color: var(--accent-hover);
        }
        
        /* --- DATAFRAMES --- */
        .stDataFrame {
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }
        
        /* --- EXPANDERS --- */
        .streamlit-expanderHeader {
            background-color: var(--bg-color);
            font-weight: 600;
        }
        
        /* --- INFO/ÉXITO/ADVERTENCIA --- */
        .stInfo {
            background-color: rgba(56, 139, 253, 0.1);
            border: 1px solid rgba(56, 139, 253, 0.3);
            color: var(--text-primary);
        }
        .stSuccess {
            background-color: rgba(35, 134, 54, 0.1);
            border: 1px solid rgba(35, 134, 54, 0.3);
            color: var(--text-primary);
        }
        .stWarning {
            background-color: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
            color: var(--text-primary);
        }

        /* --- OCULTAR ELEMENTOS DE STREAMLIT --- */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* --- HEADER PERSONALIZADO --- */
        .custom-header {
            text-align: center;
            padding: 3rem 0;
            background-color: var(--surface-color);
            border-bottom: 1px solid var(--border-color);
            margin: 0 -3rem 0 -3rem;
        }
        .custom-header h1 {
            color: var(--text-primary);
            font-size: 3rem;
            font-weight: 700;
            margin: 0;
        }
        .custom-header p {
            color: var(--text-secondary);
            font-size: 1.2rem;
            margin: 0.5rem 0 0 0;
        }
        
        /* --- ESTILOS PARA LA PÁGINA DE BIENVENIDA --- */
        .welcome-feature {
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.5rem;
            height: 100%;
            transition: transform 0.2s ease-in-out, border-color 0.2s ease-in-out;
        }
        .welcome-feature:hover {
            transform: translateY(-5px);
            border-color: var(--accent-color);
        }
        .welcome-feature h3 {
            margin-top: 0;
            color: var(--text-primary);
        }

    </style>
    """, unsafe_allow_html=True)
    # --- FIN DEL BLOQUE DE ESTILO ---
    
    # Header personalizado
    st.markdown("""
    <div class="custom-header">
        <h1>🧬 Genome Cleaner</h1>
        <p>Professional FASTA/FASTQ Sequence Cleaning and Validation Tool</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = []
    if 'sequences' not in st.session_state:
        st.session_state.sequences = []
    if 'processed_file' not in st.session_state:
        st.session_state.processed_file = None
    
    # Sidebar for file upload and options
    with st.sidebar:
        st.header("File Upload & Settings")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload FASTA/FASTQ file",
            type=['fasta', 'fa', 'fastq', 'fq'],
            help="Upload your sequence file for processing"
        )
        
        if uploaded_file:
            # Save uploaded file temporarily
            temp_file = save_uploaded_file(uploaded_file)
            
            # Processing options
            st.subheader("Processing Options")
            
            sanitize_mode = st.checkbox(
                "Enable Sanitization Mode",
                value=False,
                help="Clean invalid characters and convert to uppercase"
            )
            
            min_length = st.slider(
                "Minimum Sequence Length",
                min_value=10,
                max_value=1000,
                value=20,
                step=10,
                help="Sequences shorter than this will be marked as invalid"
            )
            
            # Process button
            if st.button("Process File", type="primary", use_container_width=True):
                with st.spinner("Processing sequences..."):
                    try:
                        process_sequences(temp_file, sanitize_mode, min_length)
                        st.success("Processing complete!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Clear data button
        if st.session_state.validation_results:
            if st.button("Clear All Data", use_container_width=True):
                st.session_state.validation_results = []
                st.session_state.sequences = []
                st.session_state.processed_file = None
                st.rerun()
    
    # Main content area
    if st.session_state.validation_results:
        display_results()
    else:
        display_welcome()


def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to temporary location."""
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    temp_file = temp_dir / uploaded_file.name
    with open(temp_file, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return str(temp_file)


def process_sequences(file_path: str, sanitize: bool, min_length: int):
    """Process sequences and store results in session state."""
    try:
        # Load sequences
        sequences = load_sequences(file_path)
        st.session_state.sequences = sequences
        
        # Validate sequences
        validation_results = validate_sequences(sequences, min_length, sanitize)
        st.session_state.validation_results = validation_results
        st.session_state.processed_file = file_path
        
        # Clean up temp file
        temp_file = Path(file_path)
        if temp_file.parent.name == "temp":
            temp_file.unlink()
        
    except ParsingError as e:
        st.error(f"File parsing error: {str(e)}")
        return
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return


def display_welcome():
    """Display welcome screen with a full-width, balanced layout."""
    st.markdown("---") # Separador
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="welcome-feature">
            <h3>Validate</h3>
            <p>Ensure your FASTA/FASTQ sequences adhere to standard formats and detect any structural errors.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="welcome-feature">
            <h3>Clean</h3>
            <p>Automatically sanitize invalid characters and prepare your data for downstream analysis.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="welcome-feature">
            <h3>Analyze</h3>
            <p>Generate comprehensive statistics on sequence length, GC content, and more.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---") # Separador

    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown("""
        <div class="welcome-feature">
            <h3>Visualize</h3>
            <p>Create interactive charts and plots to understand the distribution and quality of your data.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown("""
        <div class="welcome-feature">
            <h3>Export</h3>
            <p>Download your cleaned sequences and detailed reports in various formats (FASTA, CSV, JSON).</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---") # Separador

    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h2>Ready to get started?</h2>
        <p style="font-size: 1.1rem; color: var(--text-secondary);">
            Upload your file in the sidebar and click "Process File" to begin the analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)


def display_results():
    """Display processing results in organized tabs."""
    
    summary = get_validation_summary(st.session_state.validation_results)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Summary", 
        "Cleaning & Validation", 
        "Visualizations", 
        "Reports"
    ])
    
    with tab1:
        display_summary_tab(summary)
    
    with tab2:
        display_validation_tab()
    
    with tab3:
        display_visualizations_tab()
    
    with tab4:
        display_reports_tab(summary)


def display_summary_tab(summary: Dict):
    """Display summary metrics."""
    st.header("Processing Summary")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Sequences", 
            summary['total_sequences'],
            delta=None
        )
    
    with col2:
        validity_delta = summary['validity_percentage'] - 100 if summary['total_sequences'] > 0 else 0
        st.metric(
            "Valid Sequences", 
            summary['valid_sequences'],
            delta=f"{summary['validity_percentage']:.1f}% valid"
        )
    
    with col3:
        st.metric(
            "Invalid Sequences", 
            summary['invalid_sequences']
        )
    
    with col4:
        if summary['sanitized_sequences'] > 0:
            st.metric(
                "Sanitized", 
                summary['sanitized_sequences'],
                delta=f"{summary['sanitization_rate']:.1f}%"
            )
        else:
            st.metric("Sanitized", 0)
    
    # Error breakdown
    if summary['error_types']:
        st.subheader("Error Breakdown")
        
        error_df = pd.DataFrame(
            list(summary['error_types'].items()),
            columns=['Error Type', 'Count']
        )
        
        # Create bar chart for errors
        fig = px.bar(
            error_df, 
            x='Error Type', 
            y='Count',
            title="Distribution of Validation Errors",
            color='Count',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(
            xaxis_title="Error Type",
            yaxis_title="Number of Sequences",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Quality distribution
    st.subheader("Quality Distribution")
    
    # Calculate quality distribution
    quality_dist = calculate_quality_distribution(st.session_state.validation_results)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart for quality
        if any(quality_dist.values()):
            fig_pie = px.pie(
                values=list(quality_dist.values()),
                names=list(quality_dist.keys()),
                title="Sequence Quality Distribution",
                color_discrete_map={
                    'High Quality': '#2ecc71',
                    'Medium Quality': '#f39c12', 
                    'Low Quality': '#e74c3c',
                    'Unusable': '#95a5a6'
                }
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Quality metrics
        st.markdown("### Quality Metrics")
        for quality, count in quality_dist.items():
            if count > 0:
                percentage = (count / summary['total_sequences']) * 100
                st.metric(quality, f"{count} ({percentage:.1f}%)")


def display_validation_tab():
    """Display detailed validation results table."""
    st.header("Cleaning & Validation Results")
    
    if not st.session_state.validation_results:
        st.warning("No validation results available.")
        return
    
    # Prepare data for table
    table_data = []
    for result in st.session_state.validation_results:
        row = {
            'Index': result['sequence_index'],
            'Header': result['header'],
            'Length': result.get('original_length', 0),
            'Status': 'Valid' if result['is_valid'] else 'Invalid',
            'Errors': '; '.join(result['errors']) if result['errors'] else 'None',
            'Warnings': '; '.join(result['warnings']) if result['warnings'] else 'None',
            'GC Content %': f"{calculate_gc_content(result.get('corrected_sequence', result.get('original_sequence', ''))):.2f}",
            'Sanitized': 'Yes' if result.get('corrected_sequence') != result.get('original_sequence', '') else 'No'
        }
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    
    # Add filtering options
    st.subheader("Filter and Search")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ['All', 'Valid', 'Invalid'],
            index=0
        )
    
    with col2:
        sanitized_filter = st.selectbox(
            "Filter by Sanitization",
            ['All', 'Sanitized', 'Not Sanitized'],
            index=0
        )
    
    with col3:
        search_term = st.text_input(
            "Search in Headers",
            placeholder="Type to search..."
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if status_filter != 'All':
        if status_filter == 'Valid':
            filtered_df = filtered_df[filtered_df['Status'].str.contains('Valid')]
        else:
            filtered_df = filtered_df[filtered_df['Status'].str.contains('Invalid')]
    
    if sanitized_filter != 'All':
        if sanitized_filter == 'Sanitized':
            filtered_df = filtered_df[filtered_df['Sanitized'] == 'Yes']
        else:
            filtered_df = filtered_df[filtered_df['Sanitized'] == 'No']
    
    if search_term:
        filtered_df = filtered_df[filtered_df['Header'].str.contains(search_term, case=False, na=False)]
    
    # Display results count
    st.info(f"Showing {len(filtered_df)} of {len(df)} sequences")
    
    # Display table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400,
        column_config={
            'Header': st.column_config.TextColumn(
                'Header',
                width='large'
            ),
            'Errors': st.column_config.TextColumn(
                'Errors',
                width='medium'
            ),
            'Warnings': st.column_config.TextColumn(
                'Warnings', 
                width='medium'
            )
        }
    )
    
    # Export filtered data
    if not filtered_df.empty:
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Results (CSV)",
            data=csv_data,
            file_name="validation_results.csv",
            mime="text/csv"
        )


def display_visualizations_tab():
    """Display interactive visualizations."""
    st.header("Sequence Visualizations")
    
    if not st.session_state.validation_results:
        st.warning("No data available for visualization.")
        return
    
    # Prepare data
    lengths = []
    gc_contents = []
    headers = []
    
    for result in st.session_state.validation_results:
        sequence = result.get('corrected_sequence') or result.get('original_sequence', '')
        if sequence:
            lengths.append(len(sequence))
            gc_contents.append(calculate_gc_content(sequence))
            headers.append(result['header'])
    
    if not lengths:
        st.warning("No valid sequences for visualization.")
        return
    
    # Create subplots
    col1, col2 = st.columns(2)
    
    with col1:
        # Length distribution histogram
        fig_length = px.histogram(
            x=lengths,
            nbins=30,
            title="Distribution of Sequence Lengths",
            labels={'x': 'Sequence Length (bp)', 'y': 'Frequency'}
        )
        
        fig_length.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Length (bp)",
            yaxis_title="Count"
        )
        
        st.plotly_chart(fig_length, use_container_width=True)
    
    with col2:
        # GC content distribution
        fig_gc = px.histogram(
            x=gc_contents,
            nbins=30,
            title="Distribution of GC Content",
            labels={'x': 'GC Content (%)', 'y': 'Frequency'}
        )
        
        fig_gc.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="GC Content (%)",
            yaxis_title="Count"
        )
        
        st.plotly_chart(fig_gc, use_container_width=True)
    
    # Scatter plot: Length vs GC Content
    st.subheader("Length vs GC Content Analysis")
    
    # Create scatter plot dataframe
    scatter_df = pd.DataFrame({
        'Length': lengths,
        'GC Content': gc_contents,
        'Header': [h[:30] + '...' if len(h) > 30 else h for h in headers],
        'Index': range(len(lengths))
    })
    
    fig_scatter = px.scatter(
        scatter_df,
        x='Length',
        y='GC Content',
        hover_data=['Header'],
        title="Sequence Length vs GC Content",
        labels={'Length': 'Length (bp)', 'GC Content': 'GC Content (%)'}
    )
    
    fig_scatter.update_layout(
        height=500,
        xaxis_title="Sequence Length (bp)",
        yaxis_title="GC Content (%)"
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Box plot for GC content by length categories
    st.subheader("GC Content by Length Categories")
    
    # Create length categories
    scatter_df['Length Category'] = pd.cut(
        scatter_df['Length'], 
        bins=5, 
        labels=['Very Short', 'Short', 'Medium', 'Long', 'Very Long']
    )
    
    fig_box = px.box(
        scatter_df,
        x='Length Category',
        y='GC Content',
        title="GC Content Distribution by Length Category"
    )
    
    fig_box.update_layout(
        height=400,
        xaxis_title="Length Category",
        yaxis_title="GC Content (%)"
    )
    
    st.plotly_chart(fig_box, use_container_width=True)


def display_reports_tab(summary: Dict):
    """Display and download reports."""
    st.header("Reports & Export")
    
    # Generate comprehensive report
    if st.button("Generate Comprehensive Report"):
        with st.spinner("Generating report..."):
            try:
                report_data = generate_report(st.session_state.validation_results)
                st.session_state.generated_report = report_data
                st.success("Report generated successfully!")
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
    
    # Display report if available
    if hasattr(st.session_state, 'generated_report'):
        report = st.session_state.generated_report
        
        # Report preview
        st.subheader("Report Preview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Sequences", report['metadata']['total_sequences'])
            st.metric("Valid Sequences", report['summary']['valid_sequences'])
            st.metric("GC Content (Mean)", f"{report['gc_content'].get('mean', 0):.2f}%")
        
        with col2:
            st.metric("Average Length", f"{report['sequence_lengths'].get('mean', 0):.0f} bp")
            st.metric("Max Length", f"{report['sequence_lengths'].get('max', 0)} bp")
            st.metric("Validity Rate", f"{report['summary']['validity_percentage']:.1f}%")
        
        # Download buttons
        st.subheader("Download Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON report
            json_data = json.dumps(report, indent=2)
            st.download_button(
                label="Download JSON Report",
                data=json_data,
                file_name="genome_cleaner_report.json",
                mime="application/json"
            )
        
        with col2:
            # CSV report
            if st.button("Generate CSV Report"):
                try:
                    csv_content = generate_csv_report(report)
                    st.download_button(
                        label="Download CSV Report", 
                        data=csv_content,
                        file_name="genome_cleaner_report.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Error generating CSV: {str(e)}")
    
    # Export cleaned sequences
    st.subheader("Export Cleaned Sequences")
    
    if st.button("Export Valid Sequences (FASTA)"):
        try:
            fasta_content = generate_fasta_export(st.session_state.validation_results)
            st.download_button(
                label="Download Clean FASTA",
                data=fasta_content,
                file_name="cleaned_sequences.fasta",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error generating FASTA: {str(e)}")


def calculate_quality_distribution(validation_results: List[Dict]) -> Dict:
    """Calculate sequence quality distribution."""
    quality_levels = {
        'High Quality': 0,
        'Medium Quality': 0, 
        'Low Quality': 0,
        'Unusable': 0
    }
    
    for result in validation_results:
        has_errors = len(result["errors"]) > 0
        has_warnings = len(result["warnings"]) > 0
        
        if not has_errors:
            if not has_warnings:
                quality_levels['High Quality'] += 1
            else:
                quality_levels['Medium Quality'] += 1
        else:
            can_be_sanitized = any("Invalid characters" in error for error in result["errors"])
            if can_be_sanitized:
                quality_levels['Low Quality'] += 1
            else:
                quality_levels['Unusable'] += 1
    
    return quality_levels


def generate_csv_report(report: Dict) -> str:
    """Generate CSV content from report data."""
    lines = ["Metric,Value"]
    
    # Add summary metrics
    for key, value in report['summary'].items():
        lines.append(f"{key.replace('_', ' ').title()},{value}")
    
    # Add top sequences
    lines.append("")
    lines.append("Top 10 Longest Sequences")
    lines.append("Rank,Header,Length,GC Content")
    for seq in report.get('top_10_longest', []):
        lines.append(f"{seq['rank']},{seq['header']},{seq['length']},{seq['gc_content']:.2f}")
    
    return "\n".join(lines)


def generate_fasta_export(validation_results: List[Dict]) -> str:
    """Generate FASTA content from valid sequences."""
    fasta_lines = []
    
    for result in validation_results:
        if result['is_valid']:
            sequence = result.get('corrected_sequence') or result.get('original_sequence', '')
            if sequence:
                fasta_lines.append(f">{result['header']}")
                # Split sequence into 60-character lines
                for i in range(0, len(sequence), 60):
                    fasta_lines.append(sequence[i:i+60])
                fasta_lines.append("")  # Empty line between sequences
    
    return "\n".join(fasta_lines)


if __name__ == "__main__":
    main()