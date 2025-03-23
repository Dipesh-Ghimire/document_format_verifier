import fitz
from src.exception import CustomException
from src.logger import logging
import os;import sys
import re
from collections import Counter
import json

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
# Figure Data Extraction
def figure_data_extractor(doc):
    page_width = doc[0].rect.width  # Get the width of the first page for alignment checks

    figure_placements = []  # Store placement data
    caption_positions = []  # Store caption positions
    caption_font_sizes = []  # Store caption font sizes

    for page_num in range(len(doc)):  # Loop through all pages
        page = doc[page_num]
        images = page.get_images(full=True)  # Extract all images (figures)

        for img_index, img in enumerate(images):
            xref = img[0]  # Get image reference
            bbox = page.get_image_rects(xref)[0]  # Get bounding box of image (figure)

            # Determine figure alignment
            fig_x0, fig_y0, fig_x1, fig_y1 = bbox
            fig_width = fig_x1 - fig_x0
            page_center_x = page_width / 2

            if abs((fig_x0 + fig_x1) / 2 - page_center_x) < fig_width * 0.1:
                placement = "center"
            elif fig_x0 < page_width * 0.3:
                placement = "left"
            else:
                placement = "right"

            # Find figure caption (text near the figure)
            figure_caption, caption_font_size, caption_position = find_figure_caption(page, bbox)

            if caption_font_size:
                caption_font_sizes.append(caption_font_size)

            if placement:
                figure_placements.append(placement)

            if caption_position:
                caption_positions.append(caption_position)

    # Determine most frequent values
    most_common_placement = most_frequent(figure_placements)
    most_common_caption_position = most_frequent(caption_positions)
    most_common_caption_font_size = most_frequent(caption_font_sizes)

    return {
        "figure_placement": {
            "figure_caption_font_size": most_common_caption_font_size,
            "figure_placement": most_common_placement,
            "figure_caption_position": most_common_caption_position
        }
    }

def find_figure_caption(page, bbox):
    """
    Find the caption text near the figure.
    - If text appears *below* the figure, return "below"
    - If text appears *above* the figure, return "above"
    """
    fig_x0, fig_y0, fig_x1, fig_y1 = bbox
    caption_text = None
    caption_font_size = None
    caption_position = None

    for block in page.get_text("dict")["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text_y0 = line["bbox"][1]  # Get Y-position of text
                    font_size = round(span["size"])  # Extract font size
                    line_text = span["text"].strip()

                    # Check if text is directly below the figure
                    if fig_y1 < text_y0 < fig_y1 + font_size * 3:
                        caption_text = line_text
                        caption_font_size = font_size
                        caption_position = "below"
                        return caption_text, caption_font_size, caption_position

                    # Check if text is directly above the figure
                    if fig_y0 - font_size * 3 < text_y0 < fig_y0:
                        caption_text = line_text
                        caption_font_size = font_size
                        caption_position = "above"
                        return caption_text, caption_font_size, caption_position

    return caption_text, caption_font_size, caption_position

def most_frequent(lst):
    """Find the most common element in a list"""
    if not lst:
        return None
    return Counter(lst).most_common(1)[0][0]

# Table Data Extraction
def table_data_extractor(doc):
    page_width = doc[0].rect.width  # Get the width of the first page for alignment checks

    table_placements = []  # Store table alignment
    caption_positions = []  # Store caption positions
    caption_font_sizes = []  # Store caption font sizes

    for page_num in range(len(doc)):  # Loop through all pages
        page = doc[page_num]
        tables = find_tables(page)  # Find potential table bounding boxes

        for table_bbox in tables:
            # Determine table alignment
            table_x0, table_y0, table_x1, table_y1 = table_bbox
            table_width = table_x1 - table_x0
            page_center_x = page_width / 2

            if abs((table_x0 + table_x1) / 2 - page_center_x) < table_width * 0.1:
                placement = "center"
            elif table_x0 < page_width * 0.3:
                placement = "left"
            else:
                placement = "right"

            # Find table caption (text near the table)
            table_caption, caption_font_size, caption_position = find_table_caption(page, table_bbox)

            if caption_font_size:
                caption_font_sizes.append(caption_font_size)

            if placement:
                table_placements.append(placement)

            if caption_position:
                caption_positions.append(caption_position)

    # Determine most frequent values
    most_common_placement = most_frequent(table_placements)
    most_common_caption_position = most_frequent(caption_positions)
    most_common_caption_font_size = most_frequent(caption_font_sizes)

    return {
        "table_placement": {
            "table_caption_font_size": most_common_caption_font_size,
            "table_placement": most_common_placement,
            "table_caption_position": most_common_caption_position
        }
    }

def find_tables(page):
    """
    Identify potential tables by detecting large structured text blocks.
    - Looks for multiple consecutive text lines forming a structured shape.
    """
    table_bboxes = []

    for block in page.get_text("dict")["blocks"]:
        if "lines" in block and len(block["lines"]) > 2:  # More than 2 rows indicates a possible table
            bbox = block["bbox"]
            table_bboxes.append(bbox)

    return table_bboxes

def find_table_caption(page, bbox):
    """
    Find the caption text near the table.
    - If text appears *below* the table, return "below"
    - If text appears *above* the table, return "above"
    """
    table_x0, table_y0, table_x1, table_y1 = bbox
    caption_text = None
    caption_font_size = None
    caption_position = None

    for block in page.get_text("dict")["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text_y0 = line["bbox"][1]  # Get Y-position of text
                    font_size = round(span["size"])  # Extract font size
                    line_text = span["text"].strip()

                    # Check if text is directly below the table
                    if table_y1 < text_y0 < table_y1 + font_size * 3:
                        caption_text = line_text
                        caption_font_size = font_size
                        caption_position = "below"
                        return caption_text, caption_font_size, caption_position

                    # Check if text is directly above the table
                    if table_y0 - font_size * 3 < text_y0 < table_y0:
                        caption_text = line_text
                        caption_font_size = font_size
                        caption_position = "above"
                        return caption_text, caption_font_size, caption_position

    return caption_text, caption_font_size, caption_position

    