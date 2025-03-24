def generate_formatting_compliance_report(user_input:dict, extracted_output:dict)->dict:
    compliance_report = {}

    # 1️⃣ Table of Contents (ToC)
    toc_compliant = (user_input["table_of_contents"] == extracted_output["table_of_contents"])
    compliance_report["Table of Contents (ToC)"] = "Compliant" if toc_compliant else "Non-compliant"

    # 2️⃣ List of Figures (LoF)
    lof_compliant = (user_input["list_of_figures"] == extracted_output["list_of_figures"])
    compliance_report["List of Figures (LoF)"] = "Compliant" if lof_compliant else "Non-compliant"

    # 3️⃣ Abbreviations Section
    abbreviations_compliant = (user_input["abbreviations_section"] == extracted_output["abbreviations_section"])
    compliance_report["Abbreviations Section"] = "Compliant" if abbreviations_compliant else "Non-compliant"

    # 4️⃣ Font Type & Size (Body Text)
    font_body_correct = (
        user_input["font_type_size"]["body_font_type"].replace(" ", "").lower() ==
        extracted_output["font_type_size"]["body_font_type"].replace(" ", "").lower() and
        user_input["font_type_size"]["body_font_size"] == extracted_output["font_type_size"]["body_font_size"]
    )
    compliance_report["Font Type & Size"] = "Correct" if font_body_correct else "Incorrect"

    # 5️⃣ Header Fonts
    header_fonts_correct = (
    normalize_font_name(user_input["font_type_size"]["heading_font_type"]) ==
    normalize_font_name(extracted_output["font_type_size"]["heading_font_type"]) and
    user_input["font_type_size"]["heading_font_size"] == extracted_output["font_type_size"]["heading_font_size"]
    )
    compliance_report["Header Fonts"] = "Correct" if header_fonts_correct else "Incorrect"

    # 6️⃣ Margins
    margins_correct = (
        user_input["margins"] == extracted_output["margins"]
    )
    compliance_report["Margins"] = "Correct" if margins_correct else "Incorrect"

    # 7️⃣ Text Alignment
    text_alignment_correct = (
        user_input["text_alignment"]["text_alignment"].lower() == 
        extracted_output["text_alignment"]["text_alignment"].lower()
    )
    compliance_report["Text Alignment"] = (
        "Justified" if text_alignment_correct else "Incorrect"
    )

    # 8️⃣ Figure Placement
    figure_placement_correct = (
        user_input["figure_placement"] == extracted_output["figure_placement"]
    )
    compliance_report["Figure Placement"] = "Correct" if figure_placement_correct else "Incorrect"

    # 9️⃣ Table Placement
    table_placement_correct = (
        user_input["table_placement"] == extracted_output["table_placement"]
    )
    compliance_report["Table Placement"] = "Correct" if table_placement_correct else "Incorrect"

    # 🔟 References Formatting
    references_correct = (
        user_input["references_formatting"] == extracted_output["references_formatting"]
    )
    compliance_report["References Formatting"] = "Compliant" if references_correct else "Non-compliant"

    return compliance_report

def normalize_font_name(font_name):
    """Normalize font names to a standard format."""
    font_mappings = {
        "timesnewromanpsmt": "timesnewroman",
        "timesnewromanps-boldmt": "timesnewroman",
        "times new roman": "timesnewroman",
        "arialmt": "arial",
        "arial-boldmt": "arial",
        "calibrimt": "calibri",
        "calibri-boldmt": "calibri"
    }
    
    normalized_name = font_name.replace(" ", "").lower()
    return font_mappings.get(normalized_name, normalized_name)  # Return mapped font or original
