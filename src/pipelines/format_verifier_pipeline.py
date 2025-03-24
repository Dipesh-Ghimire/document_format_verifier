import os
import sys
from src.components.extraction.format_extractor import FormatExtractor
from src.exception import CustomException
from src.components.extraction.format_verifier import generate_formatting_compliance_report

class FormatVerifierPipeline:
    def __init__(self, pdf_path, input_format):
        self.input_format = input_format
        self.format_extractor = FormatExtractor(pdf_path)
        self.extracted_format = None
    
    def initiate_format_verification(self):
        try:
            # Extract all the format from the pdf
            self.extracted_format = self.format_extractor.extract_all()

            # Generate the compliance report
            compliance_report = generate_formatting_compliance_report(self.input_format, self.extracted_format)
            return (compliance_report, self.extracted_format)
        except CustomException as e:
            raise CustomException(e,sys)

if __name__ == "__main__":
    pdf_path = os.path.join(os.getcwd(), "dataset", "pdfs", "toxicMeter.pdf")
    input_format = {
        "table_of_contents": {
            "toc_present": True,
            "heading_font_size": 12,
            "subheading_font_size": 10,
        },
        "list_of_figures": {
            "lof_present": True,
            "figure_caption_font_size": 10,
        },
        "abbreviations_section": {
            "abbreviations_section_present": True,
            "abbreviations_sorted": True,
        },
        "font_type_size": {
            "body_font_type": "Times New Roman",
            "body_font_size": 12,
            "heading_font_type": "Times New Roman",
            "heading_font_size": 12,
        },
        "margins": {
            "left_margin_inch": 1,
            "right_margin_inch": 1,
            "top_margin_inch": 1,
            "bottom_margin_inch": 1,
        },
        "text_alignment": {
            "text_alignment": "Justified",
        },
        "figure_placement": {
            "figure_placement": "center",
            "figure_caption_position": "bottom",
            "figure_caption_font_size": 10,
        },
        "table_placement": {
            "table_placement": "center",
            "table_caption_position": "bottom",
            "table_caption_font_size": 10,
        },
        "references_formatting": {
            "references_format": "APA",
            "citations_consistent": True,
        },
    }
    fvp = FormatVerifierPipeline(pdf_path, input_format)
    fvp.initiate_format_verification()