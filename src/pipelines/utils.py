import re
import fitz
import os
# Define Label Mapping (Adjust according to your model)
label_list = ["O", "B-AUTHOR", "I-AUTHOR", "B-ROLL_NUM",
              "B-ORG", "I-ORG", "B-SUPERVISOR", "I-SUPERVISOR", "B-DATE", "I-DATE"]
label_map = {f"LABEL_{i}": label for i, label in enumerate(label_list)}

def merge_word_pieces(ner_results):
    """
    Merges subword tokens correctly (fixes WordPiece issues).
    Example: ['na', '##bara', '##j'] → ['Nabaraj']
    """
    merged_results = []
    current_word = ""
    current_label = None
    current_start = None

    for entity in ner_results:
        word = entity["word"]
        label = label_map[entity["entity"]]  # Convert LABEL_X to actual label
        start, end = entity["start"], entity["end"]

        if word.startswith("##"):  # Subword token detected
            current_word += word[2:]  # Remove "##" and append
        else:
            if current_word:  # Store previous word
                merged_results.append({"word": current_word, "entity": current_label, "start": current_start, "end": end})
            current_word = word
            current_label = label
            current_start = start

    if current_word:  # Append last word
        merged_results.append({"word": current_word, "entity": current_label, "start": current_start, "end": end})

    return merged_results
def clean_roll_number(text):
    """ Remove unwanted characters like '(', ')', ',' from roll numbers. """
    return re.sub(r"[^\d]", "", text)
def clean_pdf_text(text):
    """ Cleans PDF text by removing unwanted characters and converting it into a single line. """
    text = re.sub(r"\n+", " ", text)  # Replace newlines with spaces
    text = re.sub(r"[^a-zA-Z0-9.,\s]", "", text)  # Remove unwanted characters
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    return text
def extract_first_page_text(pdf_path):
        doc = fitz.open(pdf_path)  # Open PDF
        first_page_text = doc[0].get_text("text")  # Extract text from first page
        return first_page_text.strip()
def convert_ner_results(ner_results):
    """
    Converts processed NER results into structured metadata.
    Fixes multi-token merging for each label.
    """
    extracted_metadata = {
        "Author": set(),
        "Roll number": set(),
        "Organization": "",
        "Supervisor": "",
        "Submission Date": ""
    }

    merged_results = merge_word_pieces(ner_results)  # Ensure WordPiece tokens are merged correctly

    # Temporary variables to store multi-token entities
    author_text, roll_text, org_text, supervisor_text, date_text = "", "", "", "", ""
    in_author, in_roll, in_org, in_supervisor, in_date = False, False, False, False, False

    for entity in merged_results:
        label = entity["entity"]
        word = entity["word"]

        # Handle authors
        if label == "B-AUTHOR":
            if in_author:
                extracted_metadata["Author"].add(author_text.strip())  # Store previous
            author_text = word
            in_author = True
        elif label == "I-AUTHOR" and in_author:
            author_text += " " + word

        # Handle roll numbers
        elif label == "B-ROLL_NUM":
            if in_roll:
                cleaned_roll_num = clean_roll_number(roll_text.strip())
                if cleaned_roll_num:
                    extracted_metadata["Roll number"].add(cleaned_roll_num)
            roll_text = word
            in_roll = True
        elif label == "I-ROLL_NUM" and in_roll:
            roll_text += " " + word

        # Handle organization
        elif label == "B-ORG":
            if in_org:
                extracted_metadata["Organization"] = org_text.strip()
            org_text = word
            in_org = True
        elif label == "I-ORG" and in_org:
            org_text += " " + word

        # Handle supervisor
        elif label == "B-SUPERVISOR":
            if in_supervisor:
                extracted_metadata["Supervisor"] = supervisor_text.strip()
            supervisor_text = word
            in_supervisor = True
        elif label == "I-SUPERVISOR" and in_supervisor:
            supervisor_text += " " + word

        # Handle date
        elif label == "B-DATE":
            if in_date:
                extracted_metadata["Submission Date"] = date_text.strip()
            date_text = word
            in_date = True
        elif label == "I-DATE" and in_date:
            date_text += " " + word

    # Store the last entity values
    if author_text:
        extracted_metadata["Author"].add(author_text.strip())
    if roll_text:
        cleaned_roll_num = clean_roll_number(roll_text.strip())
        if cleaned_roll_num:
            extracted_metadata["Roll number"].add(cleaned_roll_num)
    if org_text:
        extracted_metadata["Organization"] = org_text.strip()
    if supervisor_text:
        extracted_metadata["Supervisor"] = supervisor_text.strip()
    if date_text:
        extracted_metadata["Submission Date"] = date_text.strip()

    return extracted_metadata

if __name__ == "__main__":
    pdf_path = os.path.join(os.getcwd(),'dataset',"pdfs","toxicMeter.pdf")
    pdf_text = extract_first_page_text(pdf_path)
    print("Extracted Text from First Page:\n", clean_pdf_text(pdf_text))