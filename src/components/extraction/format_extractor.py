import fitz
from src.exception import CustomException
from src.logger import logging
import os;import sys
import re
from collections import Counter
import json

def open_pdf_file(pdf_path):
    doc = fitz.open(pdf_path)
    doc.delete_page(0)  # Remove the first page (cover page)
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

def list_of_figures_extractor(doc):
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

# Abbreviations Data Extraction
def abbreviations_extractor(doc):
    abbreviations = []  # Store extracted abbreviations
    abbreviations_found = False  # Track if we are in the abbreviations list

    for page_num in range(min(15, len(doc))):  # Scan first 15 pages
        text_blocks = doc[page_num].get_text("text").split("\n")  # Extract text line by line
        lines = [line.strip() for line in text_blocks if line.strip()]  # Remove empty lines

        for line in lines:
            # Detect Abbreviations heading
            if re.search(r"\b(Abbreviations|List of Abbreviations|Acronyms)\b", line, re.IGNORECASE):
                abbreviations_found = True  # Start collecting abbreviations
                continue  # Move to the next line

            # If in abbreviations section, extract valid abbreviation-long form pairs
            if abbreviations_found:
                match = re.match(r"^([A-Z0-9]{2,})\s*[-–—:]\s*(.+)$", line)  # Abbreviation - Long form
                if match:
                    abbreviations.append(match.group(1))  # Store the abbreviation
                else:
                    # If a capitalized word appears without a valid format, stop extraction (end of section)
                    if re.match(r"^[A-Z\s]+$", line) and len(line.split()) <= 5:
                        break

    # Determine sorting order
    abbreviations_sorted = check_sorting_order(abbreviations)
    print(abbreviations)
    return {
        "abbreviations_section": {
            "abbreviations_section_present": True if abbreviations else False,
            "abbreviations_sorted": abbreviations_sorted
        }
    }

def check_sorting_order(abbreviations):
    """Determine if abbreviations are sorted in ascending, descending, or no order."""
    if abbreviations == sorted(abbreviations):
        return "asc"
    elif abbreviations == sorted(abbreviations, reverse=True):
        return "desc"
    else:
        return "none"


# References Data Extraction
def references_extractor(doc):
    references_text = ""
    references_found = False  # Track if References section is found
    references_list = []  # Store extracted references
    reference_format = None

    for page_num in range(len(doc)):  # Loop through pages
        text_blocks = doc[page_num].get_text("text").split("\n")  # Extract text line by line

        for line in text_blocks:
            line = line.strip()

            # Detect References section heading
            if re.search(r"\b(References|Bibliography|Works Cited)\b", line, re.IGNORECASE):
                references_found = True
                continue  # Move to the next line

            # If References section is found, collect reference entries
            if references_found:
                if re.match(r"^\[?\d+\]?", line) or re.search(r"\(\d{4}\)", line) or re.match(r"^\w+\.", line):
                    references_list.append(line)

            # Stop extraction when encountering a new section (empty line or unrelated text)
            if references_found and line == "":
                break

    # Determine reference format
    reference_format = detect_reference_format(references_list)

    # Check citation consistency
    consistent_format = len(set(reference_format)) == 1 if reference_format else False

    return {
        "references_formatting": {
            "references_format": reference_format[0] if reference_format else None,
            "citations_consistent": consistent_format
        }
    }

def detect_reference_format(references):
    """
    Detect the reference format: IEEE, APA, or MLA.
    """
    formats_detected = []

    for ref in references:
        if re.match(r"^\[\d+\]", ref):  # IEEE format (numbered)
            formats_detected.append("IEEE")
        elif re.search(r"\(\d{4}\)", ref):  # APA format (year in parentheses)
            formats_detected.append("APA")
        elif re.match(r"^\w+\.", ref) and not re.search(r"\(\d{4}\)", ref):  # MLA format (author + title)
            formats_detected.append("MLA")

    return list(set(formats_detected))  # Return unique formats detected

# Font Data Extraction
def font_data_extractor(doc):
    # skip first page from doc
    font_sizes = []
    font_types = []
    heading_fonts = []
    
    for page in doc:
        text_blocks = page.get_text("dict")["blocks"]
        
        for block in text_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_size = round(span["size"])  # Extract font size
                        font_type = span["font"]  # Extract font type
                        font_sizes.append(font_size)
                        font_types.append(font_type)

    # Identify the most common font type & size for body text
    most_common_body_font = most_frequent(font_types)
    most_common_body_size = most_frequent(font_sizes)

    # Identify the most common font & size for headings (largest text)
    max_font_size = max(font_sizes) if font_sizes else None
    heading_fonts = [font for font, size in zip(font_types, font_sizes) if size == max_font_size]
    most_common_heading_font = most_frequent(heading_fonts)

    return {
        "font_type_size": {
            "body_font_type": most_common_body_font,
            "body_font_size": most_common_body_size,
            "heading_font_type": most_common_heading_font,
            "heading_font_size": max_font_size
        }
    }

# Margin Data Extraction
def margin_data_extractor(doc):
    margin_values = {"left": [], "right": [], "top": [], "bottom": []}

    for page in doc:
        page_width, page_height = page.rect.width, page.rect.height  # Page size in points
        text_blocks = page.get_text("dict")["blocks"]

        # Initialize extreme values for text placement
        leftmost = page_width
        rightmost = 0
        topmost = page_height
        bottommost = 0

        for block in text_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    x0, y0, x1, y1 = line["bbox"]  # Bounding box (left, top, right, bottom)
                    leftmost = min(leftmost, x0)
                    rightmost = max(rightmost, x1)
                    topmost = min(topmost, y0)
                    bottommost = max(bottommost, y1)

        # Calculate margins in inches (1 inch = 72 points)
        left_margin = round(leftmost / 72, 2)
        right_margin = round((page_width - rightmost) / 72, 2)
        top_margin = round(topmost / 72, 2)
        bottom_margin = round((page_height - bottommost) / 72, 2)

        margin_values["left"].append(left_margin)
        margin_values["right"].append(right_margin)
        margin_values["top"].append(top_margin)
        margin_values["bottom"].append(bottom_margin)

    # Compute average margins across pages
    avg_left_margin = round(sum(margin_values["left"]) / len(margin_values["left"]), 2)
    avg_right_margin = round(sum(margin_values["right"]) / len(margin_values["right"]), 2)
    avg_top_margin = round(sum(margin_values["top"]) / len(margin_values["top"]), 2)
    avg_bottom_margin = round(sum(margin_values["bottom"]) / len(margin_values["bottom"]), 2)

    return {
        "margins": {
            "left_margin_inch": round(avg_left_margin),
            "right_margin_inch": round(avg_right_margin),
            "top_margin_inch": round(avg_top_margin),
            "bottom_margin_inch": round(avg_bottom_margin)
        }
    }

# Text Alignment Extraction
def text_alignment_extractor(doc):
    alignment_counts = []  # Store detected alignments

    for page_num in range(len(doc)):  # Loop through all pages
        page = doc[page_num]
        text_blocks = page.get_text("dict")["blocks"]

        for block in text_blocks:
            if "lines" in block:
                left_margins = []
                right_margins = []

                for line in block["lines"]:
                    x0, _, x1, _ = line["bbox"]  # Get left & right positions of the line
                    left_margins.append(x0)
                    right_margins.append(x1)

                # Compute alignment by analyzing variation in margins
                left_variation = max(left_margins) - min(left_margins) if left_margins else 0
                right_variation = max(right_margins) - min(right_margins) if right_margins else 0

                if left_variation < 5 and right_variation < 5:
                    alignment_counts.append("Justified")
                elif left_variation < 5:
                    alignment_counts.append("Left")
                elif right_variation < 5:
                    alignment_counts.append("Right")
                else:
                    alignment_counts.append("Mixed")

    # Determine most frequent text alignment
    most_common_alignment = most_frequent(alignment_counts)

    return {
        "text_alignment": {
            "text_alignment": most_common_alignment
        }
    }

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

    