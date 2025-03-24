import asyncio
import os
import sys
import tempfile
import streamlit as st
if sys.platform == "linux" or sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Import your ML pipeline
from src.pipelines.format_verifier_pipeline import FormatVerifierPipeline
from src.pipelines.metadata_extraction_pipeline import MetadataExtractionPipeline

# Streamlit UI
st.title("PDF Metadata Extractor & Formatting Compliance Analyzer")

# File Upload
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Expandable Section for Format Verification Input Template
with st.expander("🔧 Configure Format Verification Inputs (Optional)"):
    # Table of Contents
    toc_present = st.checkbox("Table of Contents Present", value=True, key="toc_present")
    heading_font_size = st.number_input("Heading Font Size", value=16, min_value=8, max_value=50, key="heading_font_size")
    subheading_font_size = st.number_input("Subheading Font Size", value=14, min_value=8, max_value=50, key="subheading_font_size")

    # List of Figures
    lof_present = st.checkbox("List of Figures Present", value=True, key="lof_present")
    figure_caption_font_size = st.number_input("Figure Caption Font Size", value=12, min_value=8, max_value=50, key="figure_caption_font_size")

    # Abbreviations Section
    abbreviations_section_present = st.checkbox("Abbreviations Section Present", value=True, key="abbreviations_section_present")
    abbreviations_sorted = st.selectbox("Abbreviations Sorted", ["asc", "desc"], index=0, key="abbreviations_sorted")

    # Font Type & Size
    body_font_type = st.text_input("Body Font Type", value="Times New Roman", key="body_font_type")
    body_font_size = st.number_input("Body Font Size", value=12, min_value=8, max_value=50, key="body_font_size")
    heading_font_type = st.text_input("Heading Font Type", value="Arial", key="heading_font_type")
    heading_font_size = st.number_input("Heading Font Size", value=16, min_value=8, max_value=50, key="heading_font_size2")

    # Margins
    left_margin = st.number_input("Left Margin (inches)", value=1.0, min_value=0.1, max_value=5.0, key="left_margin")
    right_margin = st.number_input("Right Margin (inches)", value=1.0, min_value=0.1, max_value=5.0, key="right_margin")
    top_margin = st.number_input("Top Margin (inches)", value=1.0, min_value=0.1, max_value=5.0, key="top_margin")
    bottom_margin = st.number_input("Bottom Margin (inches)", value=1.0, min_value=0.1, max_value=5.0, key="bottom_margin")

    # Text Alignment
    text_alignment = st.selectbox("Text Alignment", ["Left", "Right", "Center", "Justified"], index=3, key="text_alignment")

    # Figure Placement
    figure_placement = st.selectbox("Figure Placement", ["left", "center", "right"], index=1, key="figure_placement")
    figure_caption_position = st.selectbox("Figure Caption Position", ["above", "below"], index=1, key="figure_caption_position")

    # Table Placement
    table_placement = st.selectbox("Table Placement", ["left", "center", "right"], index=1, key="table_placement")
    table_caption_position = st.selectbox("Table Caption Position", ["above", "below"], index=0, key="table_caption_position")

    # References Formatting
    references_format = st.selectbox("References Format", ["IEEE", "APA", "MLA"], index=0, key="references_format")
    citations_consistent = st.checkbox("Citations Consistent", value=True, key="citations_consistent")

if uploaded_file is not None:
    st.toast("File uploaded successfully!", icon="✅") 

    if st.button("Analyze the PDF"):
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(uploaded_file.getbuffer())
            temp_filename = temp_pdf.name  # Get the temporary file path
        
        try:
            # Prepare format verification input template
            format_verification_input = {
                "table_of_contents": {
                    "toc_present": toc_present,
                    "heading_font_size": heading_font_size,
                    "subheading_font_size": subheading_font_size,
                },
                "list_of_figures": {
                    "lof_present": lof_present,
                    "figure_caption_font_size": figure_caption_font_size,
                },
                "abbreviations_section": {
                    "abbreviations_section_present": abbreviations_section_present,
                    "abbreviations_sorted": abbreviations_sorted,
                },
                "font_type_size": {
                    "body_font_type": body_font_type,
                    "body_font_size": body_font_size,
                    "heading_font_type": heading_font_type,
                    "heading_font_size": heading_font_size,
                },
                "margins": {
                    "left_margin_inch": left_margin,
                    "right_margin_inch": right_margin,
                    "top_margin_inch": top_margin,
                    "bottom_margin_inch": bottom_margin,
                },
                "text_alignment": {
                    "text_alignment": text_alignment,
                },
                "figure_placement": {
                    "figure_placement": figure_placement,
                    "figure_caption_position": figure_caption_position,
                    "figure_caption_font_size": figure_caption_font_size,
                },
                "table_placement": {
                    "table_placement": table_placement,
                    "table_caption_position": table_caption_position,
                    "table_caption_font_size": figure_caption_font_size,
                },
                "references_formatting": {
                    "references_format": references_format,
                    "citations_consistent": citations_consistent,
                },
            }
            # Call the ML pipeline with the file path
            # Call your ML pipeline function (Ensure analyze_pdf returns two dictionaries)
            me_pipeline = MetadataExtractionPipeline()
            metadata_results, compliance_results = me_pipeline.extract(temp_filename)
            
            # Formatting Compliance Analysis
            fv_pipeline = FormatVerifierPipeline(temp_filename, format_verification_input)
            compliance_report,extracted_format = fv_pipeline.initiate_format_verification()
            #compliance_report_format = {'Table of Contents (ToC)': 'Non-compliant', 'List of Figures (LoF)': 'Non-compliant', 'Abbreviations Section': 'Non-compliant', 'Font Type & Size': 'Incorrect', 'Header Fonts': 'Incorrect', 'Margins': 'Incorrect', 'Text Alignment': 'Justified', 'Figure Placement': 'Incorrect', 'Table Placement': 'Incorrect', 'References Formatting': 'Non-compliant'}
            #extracted_format = {'table_of_contents': {'toc_present': True, 'heading_font_size': 16, 'subheading_font_size': 12}, 'list_of_figures': {'lof_present': True, 'figure_caption_font_size': 12}, 'abbreviations_section': {'abbreviations_section_present': True, 'abbreviations_sorted': 'asc'}, 'font_type_size': {'body_font_type': 'TimesNewRomanPSMT', 'body_font_size': 12, 'heading_font_type': 'TimesNewRomanPS-BoldMT', 'heading_font_size': 18}, 'margins': {'left_margin_inch': 1, 'right_margin_inch': 1, 'top_margin_inch': 2, 'bottom_margin_inch': 1}, 'text_alignment': {'text_alignment': 'Justified'}, 'figure_placement': {'figure_caption_font_size': 12, 'figure_placement': 'center', 'figure_caption_position': 'above'}, 'table_placement': {'table_caption_font_size': 12, 'table_placement': 'right', 'table_caption_position': 'above'}, 'references_formatting': {'references_format': None, 'citations_consistent': False}}
            
            # Create two columns
            col1, col2 = st.columns([3, 3])

            with col1:
                st.subheader("Extracted Metadata using Fine Tuned BERT")
                st.json(metadata_results)

            with col2:
                st.subheader("Actual Metadata of uploaded PDF")
                st.json(compliance_results)
            # Create two more columns for Compliance Report and Extracted Format
            col3, col4 = st.columns([3, 3])

            with col3:
                st.subheader("📌 Compliance Report")
                compliance_df = [{"Category": key, "Compliance Status": value} for key, value in compliance_report.items()]
                st.table(compliance_df)

            with col4:
                st.subheader("📌 Extracted Format")
                
                extracted_format_data = []
                for category, details in extracted_format.items():
                    for key, value in details.items():
                        extracted_format_data.append({
                            "Category": category, 
                            "Property": key, 
                            "Extracted Value": str(value)  # Convert all values to string
                        })
                
                st.table(extracted_format_data)



        finally:
            # Clean up the temporary file
            os.remove(temp_filename)

