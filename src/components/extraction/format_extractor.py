import fitz
from src.exception import CustomException
from src.logger import logging
import os;import sys

def open_pdf_file(pdf_path):
    doc = fitz.open(pdf_path)
    return doc
def table_of_content_extractor(doc):
    return True
def list_of_figures_extractor(doc):
    return True
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

    