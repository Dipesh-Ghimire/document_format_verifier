import re
from together import Together
import json

def extract_metadata_llama(text)->dict:
    """
    Extracts metadata from the given document text using Llama 2 API via Together AI.
    
    Parameters:
        text (str): The document text to process.
    
    Returns:
        dict: The extracted metadata in JSON format.
    """
    # Initialize Together AI Client
    client = Together(api_key="61feb712ca012f046fb68a4a3ead3554091b6053a880b32f6babc10fcde23e09")
    # Construct Prompt
    prompt = f"""
    Extract metadata from the following document:

    {text}

    Return just the response in JSON format with:
    1. Metadata: (Author, Organization, Roll Number, Supervisor, Submission Date)
    Note(if there are multiple values for any, you can use an array inside.)
    2. Do not reply any other information, just the valid json response.
    """
    
    # Call Llama 2 on Together AI
    response = client.chat.completions.create(
        model="meta-llama/Llama-Vision-Free",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.5,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=True  # Streaming Response
    )

    # Process response
    output = ""
    for token in response:
        if hasattr(token, 'choices') and token.choices:
            output += token.choices[0].delta.content
    # Extract JSON content (find the first occurrence of `{` and extract everything from there)
    match = re.search(r'\{.*', output, re.DOTALL)
    cleaned_output = ""
    if match:
        cleaned_output = match.group(0)  # Extract the JSON part
        cleaned_output = re.sub(r'```$', '', cleaned_output).strip()
    try:
        json_output = json.loads(cleaned_output)  # Convert response to JSON format
        if isinstance(json_output, dict):
            return json_output  # Return structured JSON output
        else:
            return {"error": "Unexpected JSON format from Llama 2"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from Llama 2"}

# Example usage
if __name__ == "__main__":
    # sample_text = """
    # TRIBHUVAN UNIVERSITY INSTITUTE OF SCIENCE AND TECHNOLOGY Project Report On TOXIC COMMENT MODERATION SYSTEM 
    # In the partial fulfilment of the requirements for the Bachelor’s Degree in Information Technology 
    # Under the supervision of Mr. Nabaraj Bahadur Negi Lecturer Department of Information Technology Amrit Campus 
    # Lainchaur, Kathmandu Submitted by Dipesh Ghimire (199/077) Rajesh Adhikari (212/077) Sijan B.K. (223/077) 
    # Department of Information Technology Amrit Campus Lainchaur, Kathmandu Submitted to Tribhuvan University 
    # Institute of Science and Technology February 2025
    # """
    # metadata = extract_metadata(sample_text)
    # print(json.dumps(metadata, indent=4))
    print("Llama 2 API Integration for Metadata Extraction")
