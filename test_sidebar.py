"""
Minimal Streamlit Test - Sidebar Visibility Check
"""

import streamlit as st

# Configure page
st.set_page_config(
    page_title="Sidebar Test",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main content
st.title("🧬 Sidebar Visibility Test")
st.write("This is a minimal test to check if the sidebar appears.")

# Sidebar
with st.sidebar:
    st.header("📁 SIDEBAR IS HERE!")
    st.write("If you can see this, the sidebar is working!")
    
    uploaded_file = st.file_uploader(
        "Upload FASTA/FASTQ file",
        type=['fasta', 'fa', 'fastq', 'fq']
    )
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
    
    st.button("Test Button")

# Main area instructions
st.markdown("---")
st.markdown("""
### Instructions:
1. Look to the **LEFT** side of this page
2. You should see a sidebar with "SIDEBAR IS HERE!" text
3. If you don't see it, look for a **> arrow** in the top-left corner and click it
4. The sidebar contains the file uploader

### Troubleshooting:
- Try refreshing the page (F5)
- Try making your browser window wider
- Check if there's a collapse button (< or >) in the top-left
""")

st.info("👈 The sidebar should be visible on the left side of this page")
