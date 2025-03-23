import fitz
from src.exception import CustomException
from src.logger import logging
import os;import sys
import re

def open_pdf_file(pdf_path):
    doc = fitz.open(pdf_path)
    return doc
def table_of_content_extractor(doc):
    toc_text = ""
    toc_found = False  # Flag to track if ToC has started
    potential_toc = []  # Store potential ToC lines
    toc_fonts = []  # Store font size information
    toc_heading_size = None  # Track ToC heading font size (only once)
    subheading_sizes = set()  # Track unique subheading font sizes

    # Iterate through first few pages (ToC is usually at the beginning)
    for page_num in range(min(10, len(doc))):  # Scan first 10 pages
        text_blocks = doc[page_num].get_text("dict")["blocks"]

        for block in text_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_size = round(span["size"])  # Extract font size
                        line_text = span["text"].strip()

                        # Detect ToC heading (ensure we only capture the first occurrence)
                        if re.search(r"\b(Table\s*of\s*Contents|Contents|Index)\b", line_text, re.IGNORECASE):
                            if not toc_found:  # Only set once
                                toc_found = True  
                                toc_heading_size = font_size  # Store only the first ToC heading font size
                                toc_fonts.append(("Heading", line_text, font_size))
                            toc_text += line_text + "\n"
                            continue

                        # If ToC has started, keep extracting until a matching font size is detected
                        if toc_found:
                            # Stop when encountering a section heading of the same size as the ToC heading
                            if font_size == toc_heading_size:
                                return {
                                    "table_of_contents": {
                                        "toc_present": True,
                                        "heading_font_size": toc_heading_size,
                                        "subheading_font_size": max(subheading_sizes) if subheading_sizes else None
                                    }
                                }

                            # Identify ToC subheadings based on detected text patterns
                            if re.match(r"^\d+(\.\d+)*\s+[A-Za-z\s]+", line_text):  
                                subheading_sizes.add(font_size)  # Store unique subheading font sizes
                                toc_fonts.append(("Subheading", line_text, font_size))
                            else:
                                toc_fonts.append(("Regular", line_text, font_size))

                            potential_toc.append(line_text)
                            toc_text += line_text + "\n"

    # If no ToC found, return False
    return {
        "table_of_contents": {
            "toc_present": False,
            "heading_font_size": None,
            "subheading_font_size": None
        }
    }

def list_of_figures_extractor(pdf_path):
    doc = fitz.open(pdf_path)
    lof_text = ""
    lof_found = False  # Flag to track if LoF has started
    figure_caption_sizes = set()  # Store unique font sizes of figure captions
    lof_heading_size = None  # Track LoF heading font size

    # Iterate through first few pages (LoF is usually at the beginning)
    for page_num in range(min(10, len(doc))):  # Scan first 10 pages
        text_blocks = doc[page_num].get_text("dict")["blocks"]

        for block in text_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_size = round(span["size"])  # Extract font size
                        line_text = span["text"].strip()

                        # Detect LoF heading (ensuring we only capture the first occurrence)
                        if re.search(r"\b(List\s*of\s*Figures|Figures|Figure Index)\b", line_text, re.IGNORECASE):
                            if not lof_found:  # Only set once
                                lof_found = True  
                                lof_heading_size = font_size  # Store LoF heading font size
                            lof_text += line_text + "\n"
                            continue

                        # If LoF has started, keep extracting until a matching font size is detected
                        if lof_found:
                            # Identify figure captions (likely smaller font size than heading)
                            if re.match(r"^(Figure|Fig\.|Table)\s+\d+[:.\s]", line_text):  
                                figure_caption_sizes.add(font_size)  # Store caption font size

                            # Stop when encountering a section heading of the same size as the LoF heading,
                            # BUT only if we have already captured some figure captions.
                            if font_size == lof_heading_size and figure_caption_sizes:
                                return {
                                    "list_of_figures": {
                                        "lof_present": True,
                                        "figure_caption_font_size": max(figure_caption_sizes)  # Return largest detected caption font
                                    }
                                }

                            lof_text += line_text + "\n"

    # If no LoF found, return False
    return {
        "list_of_figures": {
            "lof_present": False,
            "figure_caption_font_size": None
        }
    }

def abbreviations_extractor(doc):
    return True
def references_extractor(doc):
    return True
def font_data_extractor(doc):
    return True
def margin_data_extractor(doc):
    return True
def text_alignment_extractor(doc):
    return True
def figure_data_extractor(doc):
    return True
def table_data_extractor(doc):
    return True

    