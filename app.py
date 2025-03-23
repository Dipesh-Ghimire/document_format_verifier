import asyncio
import os
import sys
import tempfile
import streamlit as st
if sys.platform == "linux" or sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Import your ML pipeline
from src.pipelines.metadata_extraction_pipeline import MetadataExtractionPipeline

# Streamlit UI
st.title("PDF Metadata Extractor & Formatting Compliance Analyzer")

# File Upload
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    st.toast("File uploaded successfully!", icon="✅") 

    if st.button("Analyze the PDF"):
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(uploaded_file.getbuffer())
            temp_filename = temp_pdf.name  # Get the temporary file path
        
        try:
            # Call the ML pipeline with the file path
            # Call your ML pipeline function (Ensure analyze_pdf returns two dictionaries)
            me_pipeline = MetadataExtractionPipeline()
            metadata_results, compliance_results = me_pipeline.extract(temp_filename)
            
            # Create two columns
            col1, col2 = st.columns([3, 3])

            with col1:
                st.subheader("Extracted Metadata")
                st.json(metadata_results)

            with col2:
                st.subheader("Formatting Compliance")
                st.json(compliance_results)


        finally:
            # Clean up the temporary file
            os.remove(temp_filename)

